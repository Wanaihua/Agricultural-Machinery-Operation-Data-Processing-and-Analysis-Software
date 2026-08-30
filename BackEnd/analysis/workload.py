"""
模块1：农机作业量统计分析

实现以下指标计算：
1. 作业总时长 Ttotal
2. 作业总行程 Dtotal
3. 作业面积 Sfield
4. 平均作业速度 vwork
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from django.db.models import QuerySet

from BackEnd.generated_api.models import Track, Trackpoints


def calculate_workload(track_id: int, work_width: float = 2.0) -> Dict:
    """
    计算指定作业轨迹的工作量统计

    Args:
        track_id: 作业轨迹ID
        work_width: 农机作业幅宽(米)，默认2.0米

    Returns:
        包含四个指标的字典
    """
    # 获取轨迹信息
    try:
        track = Track.objects.get(trackid=track_id)
    except Track.DoesNotExist:
        return {"error": f"轨迹 {track_id} 不存在"}

    # 获取所有轨迹点，按时间排序
    trackpoints = Trackpoints.objects.filter(trackid=track).order_by('gpstime')

    if not trackpoints.exists():
        return {"error": "轨迹点数据为空"}

    # 1. 作业总时长：多段工作状态累加（秒）
    total_time = calculate_total_time(trackpoints)

    # 2. 作业总行程：所有轨迹点逐点欧氏距离累加（米）
    total_distance = calculate_total_distance(trackpoints)

    # 3. 作业面积：只使用工作状态=True的轨迹点 × 幅宽（平方米）
    work_area = calculate_work_area(trackpoints, work_width)

    # 4. 平均作业速度：工作状态=True的轨迹点速度字段算术平均
    avg_velocity = calculate_average_velocity(trackpoints)

    return {
        "track_id": track_id,
        "total_time": {
            "seconds": total_time,
            "formatted": format_time(total_time)
        },
        "total_distance": {
            "meters": round(total_distance, 2),
            "kilometers": round(total_distance / 1000, 3)
        },
        "work_area": {
            "square_meters": round(work_area, 2),
            "mu": round(work_area / 666.67, 3)
        },
        "average_velocity": {
            "m_per_s": round(avg_velocity, 3),
            "km_per_h": round(avg_velocity * 3.6, 3)
        },
        "work_width": work_width
    }


def calculate_total_time(trackpoints: QuerySet) -> float:
    """
    计算作业总时长 Ttotal

    公式：Ttotal = sum(作业状态=1的时间段)
    只累加workstatus=1的作业时间段

    Args:
        trackpoints: 轨迹点查询集（已按时间排序）

    Returns:
        总时长秒数
    """
    if not trackpoints.exists():
        return 0.0

    total_seconds = 0.0
    prev_work_status = None
    segment_start = None

    for point in trackpoints:
        current_work_status = point.workstatus == 1

        if prev_work_status is None:
            if current_work_status:
                segment_start = point.gpstime
        else:
            if not prev_work_status and current_work_status:
                segment_start = point.gpstime
            elif prev_work_status and not current_work_status:
                if segment_start is not None:
                    total_seconds += (point.gpstime - segment_start).total_seconds()
                    segment_start = None

        prev_work_status = current_work_status

    if segment_start is not None and prev_work_status:
        last_point = trackpoints.last()
        total_seconds += (last_point.gpstime - segment_start).total_seconds()

    return total_seconds


def detect_work_segments(trackpoints: QuerySet) -> List[Tuple[datetime, datetime]]:
    """
    检测作业片段

    当工作状态从非工作变为工作时，开始新片段
    当工作状态从工作变为非工作时，结束当前片段

    Args:
        trackpoints: 轨迹点查询集（已按时间排序）

    Returns:
        作业片段列表 [(start_time, end_time), ...]
    """
    segments = []
    current_segment_start = None
    prev_work_status = None

    for point in trackpoints:
        current_work_status = point.workstatus == 1  # 假设1表示工作状态

        if prev_work_status is None:
            # 第一个点
            if current_work_status:
                current_segment_start = point.gpstime
        else:
            # 状态变化检测
            if not prev_work_status and current_work_status:
                # 开始工作
                current_segment_start = point.gpstime
            elif prev_work_status and not current_work_status:
                # 结束工作
                if current_segment_start is not None:
                    segments.append((current_segment_start, point.gpstime))
                    current_segment_start = None

        prev_work_status = current_work_status

    # 如果最后一个片段仍在进行中
    if current_segment_start is not None and prev_work_status:
        last_point = trackpoints.last()
        segments.append((current_segment_start, last_point.gpstime))

    return segments


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    使用 Haversine 公式计算两点间的球面距离（米）

    Args:
        lon1, lat1: 第一个点的经纬度（度）
        lon2, lat2: 第二个点的经纬度（度）

    Returns:
        两点间距离（米）
    """
    R = 6371000  # 地球平均半径（米）

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def calculate_total_distance(trackpoints: QuerySet) -> float:
    """
    计算作业总行程 Dtotal

    公式：Dtotal = sum(sqrt((xi+1‑xi)²+(yi+1‑yi)²))
    全部作业时段内轨迹点逐点欧氏距离累加，坐标单位米
    优先使用 x/y 平面坐标；若 x/y 为 NULL 则使用 lon/lat 经纬度 + Haversine

    Args:
        trackpoints: 轨迹点查询集（已按时间排序）

    Returns:
        总行程米数
    """
    if trackpoints.count() < 2:
        return 0.0

    total_distance = 0.0
    prev_point = None

    for point in trackpoints:
        if prev_point is not None:
            # 优先使用 x/y 平面坐标
            if point.x is not None and point.y is not None and prev_point.x is not None and prev_point.y is not None:
                dx = point.x - prev_point.x
                dy = point.y - prev_point.y
                distance = math.sqrt(dx * dx + dy * dy)
                total_distance += distance
            # 回退到 lon/lat 经纬度
            elif point.lon is not None and point.lat is not None and prev_point.lon is not None and prev_point.lat is not None:
                distance = haversine_distance(prev_point.lon, prev_point.lat, point.lon, point.lat)
                total_distance += distance

        prev_point = point

    return total_distance


def calculate_work_area(trackpoints: QuerySet, work_width: float) -> float:
    """
    计算作业面积 Sfield

    公式：Sfield = sum(sqrt((xi+1‑xi)²+(yi+1‑yi)²)) * w
    ⚠️只使用工作状态=True的轨迹点参与面积计算

    Args:
        trackpoints: 轨迹点查询集（已按时间排序）
        work_width: 农机作业幅宽(米)

    Returns:
        作业面积（平方米）
    """
    # 过滤工作状态=True的轨迹点
    work_trackpoints = trackpoints.filter(workstatus=1)

    if work_trackpoints.count() < 2:
        return 0.0

    work_distance = 0.0
    prev_point = None

    for point in work_trackpoints:
        if prev_point is not None:
            # 优先使用 x/y 平面坐标
            if point.x is not None and point.y is not None and prev_point.x is not None and prev_point.y is not None:
                dx = point.x - prev_point.x
                dy = point.y - prev_point.y
                distance = math.sqrt(dx * dx + dy * dy)
                work_distance += distance
            # 回退到 lon/lat 经纬度
            elif point.lon is not None and point.lat is not None and prev_point.lon is not None and prev_point.lat is not None:
                distance = haversine_distance(prev_point.lon, prev_point.lat, point.lon, point.lat)
                work_distance += distance

        prev_point = point

    # 面积 = 工作行程 × 作业幅宽
    return work_distance * work_width


def calculate_average_velocity(trackpoints: QuerySet) -> float:
    """
    计算平均作业速度 vwork

    仅取工作状态=True的有效轨迹点Pi的速度做算术平均
    过滤不合理异常速度

    Args:
        trackpoints: 轨迹点查询集（已按时间排序）

    Returns:
        平均速度（米/秒）
    """
    # 过滤工作状态=True的轨迹点
    work_trackpoints = trackpoints.filter(workstatus=1)

    if not work_trackpoints.exists():
        return 0.0

    velocities = []
    # 定义合理的速度范围（米/秒）
    min_velocity = 0.0
    max_velocity = 50.0  # 假设最大速度50m/s（180km/h）

    for point in work_trackpoints:
        if point.velocity is not None:
            # 数据库velocity字段单位是km/h，转换为m/s
            velocity_ms = point.velocity / 3.6
            # 过滤异常速度
            if min_velocity <= velocity_ms <= max_velocity:
                velocities.append(velocity_ms)

    if not velocities:
        return 0.0

    # 计算算术平均值
    return sum(velocities) / len(velocities)


def format_time(seconds: float) -> str:
    """
    将秒数格式化为 HH:mm:ss 格式

    Args:
        seconds: 秒数

    Returns:
        格式化的时间字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def calculate_workload_for_all_tracks(work_width: float = 2.0) -> List[Dict]:
    """
    计算所有作业轨迹的工作量统计

    Args:
        work_width: 农机作业幅宽(米)

    Returns:
        所有轨迹的工作量统计列表
    """
    tracks = Track.objects.all()
    results = []

    for track in tracks:
        result = calculate_workload(track.trackid, work_width)
        results.append(result)

    return results


def get_workload_summary(work_width: float = 2.0) -> Dict:
    """
    获取所有轨迹的工作量汇总

    Args:
        work_width: 农机作业幅宽(米)

    Returns:
        汇总统计
    """
    all_workloads = calculate_workload_for_all_tracks(work_width)

    # 过滤掉错误结果
    valid_workloads = [w for w in all_workloads if "error" not in w]

    if not valid_workloads:
        return {"error": "没有有效的轨迹数据"}

    total_time = sum(w["total_time"]["seconds"] for w in valid_workloads)
    total_distance = sum(w["total_distance"]["meters"] for w in valid_workloads)
    total_area = sum(w["work_area"]["square_meters"] for w in valid_workloads)
    avg_velocity = sum(w["average_velocity"]["m_per_s"] for w in valid_workloads) / len(valid_workloads)

    return {
        "total_tracks": len(valid_workloads),
        "total_time": {
            "seconds": total_time,
            "formatted": format_time(total_time)
        },
        "total_distance": {
            "meters": round(total_distance, 2),
            "kilometers": round(total_distance / 1000, 3)
        },
        "total_area": {
            "square_meters": round(total_area, 2),
            "mu": round(total_area / 666.67, 3)
        },
        "average_velocity": {
            "m_per_s": round(avg_velocity, 3),
            "km_per_h": round(avg_velocity * 3.6, 3)
        },
        "work_width": work_width
    }
