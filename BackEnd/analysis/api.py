"""
农机作业量统计分析API接口
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from BackEnd.analysis.workload import (
    calculate_workload,
    calculate_workload_for_all_tracks,
    get_workload_summary
)


def ok(data=None, msg="success"):
    """统一返回格式"""
    return Response({"code": "200", "data": data, "msg": msg})


def fail(msg="failed", code="500", data=None):
    """统一错误返回格式"""
    return Response({"code": str(code), "data": data, "msg": msg})


@api_view(['GET'])
def analyze_track_workload(request, track_id):
    """
    分析单条轨迹的作业量

    GET /api/analysis/track/<track_id>/?work_width=2.0

    参数:
        work_width: 农机作业幅宽(米)，可选，默认2.0米

    返回:
        包含四个指标的统计结果
    """
    try:
        work_width = float(request.query_params.get('work_width', 2.0))
    except (TypeError, ValueError):
        work_width = 2.0

    result = calculate_workload(track_id, work_width)

    if "error" in result:
        return fail(msg=result["error"], code="404")

    return ok(data=result)


@api_view(['GET'])
def analyze_all_tracks_workload(request):
    """
    分析所有轨迹的作业量

    GET /api/analysis/all-tracks/?work_width=2.0

    参数:
        work_width: 农机作业幅宽(米)，可选，默认2.0米

    返回:
        所有轨迹的统计结果列表
    """
    try:
        work_width = float(request.query_params.get('work_width', 2.0))
    except (TypeError, ValueError):
        work_width = 2.0

    results = calculate_workload_for_all_tracks(work_width)
    return ok(data=results)


@api_view(['GET'])
def get_workload_summary_view(request):
    """
    获取所有轨迹的工作量汇总

    GET /api/analysis/summary/?work_width=2.0

    参数:
        work_width: 农机作业幅宽(米)，可选，默认2.0米

    返回:
        汇总统计结果
    """
    try:
        work_width = float(request.query_params.get('work_width', 2.0))
    except (TypeError, ValueError):
        work_width = 2.0

    result = get_workload_summary(work_width)

    if "error" in result:
        return fail(msg=result["error"], code="404")

    return ok(data=result)
