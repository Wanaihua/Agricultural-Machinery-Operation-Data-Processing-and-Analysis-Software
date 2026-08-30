"""
模块1：农机作业量统计分析 - 测试脚本

用于验证四个指标的计算是否正确
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from BackEnd.analysis.workload import (
    calculate_workload,
    calculate_total_time,
    calculate_total_distance,
    calculate_work_area,
    calculate_average_velocity,
    format_time,
    get_workload_summary
)
from BackEnd.generated_api.models import Track, Trackpoints


def test_format_time():
    """测试时间格式化函数"""
    print("测试时间格式化函数...")

    test_cases = [
        (0, "00:00:00"),
        (30, "00:00:30"),
        (60, "00:01:00"),
        (3600, "01:00:00"),
        (3661, "01:01:01"),
        (86399, "23:59:59"),
    ]

    for seconds, expected in test_cases:
        result = format_time(seconds)
        assert result == expected, f"格式化失败: {seconds}秒 -> {result}, 期望: {expected}"
        print(f"  ✓ {seconds}秒 -> {result}")

    print("时间格式化函数测试通过!\n")


def test_track_workload(track_id, work_width=2.0):
    """测试单条轨迹的工作量计算"""
    print(f"测试轨迹 {track_id} 的工作量计算...")

    result = calculate_workload(track_id, work_width)

    if "error" in result:
        print(f"  错误: {result['error']}")
        return result

    print(f"  作业总时长: {result['total_time']['formatted']} ({result['total_time']['seconds']:.2f}秒)")
    print(f"  作业总行程: {result['total_distance']['meters']:.2f}米 ({result['total_distance']['kilometers']:.3f}公里)")
    print(f"  作业面积: {result['work_area']['square_meters']:.2f}平方米 ({result['work_area']['mu']:.3f}亩)")
    print(f"  平均作业速度: {result['average_velocity']['m_per_s']:.3f}米/秒 ({result['average_velocity']['km_per_h']:.3f}公里/小时)")
    print(f"  作业幅宽: {result['work_width']}米")

    return result


def test_summary(work_width=2.0):
    """测试汇总统计"""
    print("测试汇总统计...")

    result = get_workload_summary(work_width)

    if "error" in result:
        print(f"  错误: {result['error']}")
        return result

    print(f"  总轨迹数: {result['total_tracks']}")
    print(f"  总作业时长: {result['total_time']['formatted']} ({result['total_time']['seconds']:.2f}秒)")
    print(f"  总作业行程: {result['total_distance']['meters']:.2f}米 ({result['total_distance']['kilometers']:.3f}公里)")
    print(f"  总作业面积: {result['total_area']['square_meters']:.2f}平方米 ({result['total_area']['mu']:.3f}亩)")
    print(f"  平均作业速度: {result['average_velocity']['m_per_s']:.3f}米/秒 ({result['average_velocity']['km_per_h']:.3f}公里/小时)")
    print(f"  作业幅宽: {result['work_width']}米")

    return result


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("模块1：农机作业量统计分析 - 测试")
    print("=" * 60)
    print()

    # 测试时间格式化
    test_format_time()

    # 获取数据库中的轨迹
    tracks = Track.objects.all()
    print(f"数据库中共有 {tracks.count()} 条轨迹\n")

    if tracks.exists():
        # 测试第一条轨迹
        first_track = tracks.first()
        print(f"测试第一条轨迹 (ID: {first_track.trackid})...")
        test_track_workload(first_track.trackid)

        # 测试汇总统计
        print()
        test_summary()
    else:
        print("数据库中没有轨迹数据，跳过轨迹计算测试")

    print()
    print("=" * 60)
    print("所有测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
