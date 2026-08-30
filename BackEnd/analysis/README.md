# 模块1：农机作业量统计分析

## 概述

本模块实现了农机作业量的统计分析功能，包括四个核心指标的计算：

1. **作业总时长 (Ttotal)** - 总工作时间
2. **作业总行程 (Dtotal)** - 总行驶距离
3. **作业面积 (Sfield)** - 实际作业面积
4. **平均作业速度 (vwork)** - 平均工作速度

## 指标计算公式

### 1. 作业总时长 Ttotal

```
Ttotal = Σ (tend - tstart)
```

- 存在关机、多段作业片段时，对每段作业时间累加
- 输出：总时长秒数 + HH:mm:ss格式化字符串

### 2. 作业总行程 Dtotal

```
Dtotal = Σ √((xi+1 - xi)² + (yi+1 - yi)²)
```

- 全部作业时段内轨迹点逐点欧氏距离累加
- 坐标单位：米

### 3. 作业面积 Sfield

```
Sfield = Σ √((xi+1 - xi)² + (yi+1 - yi)²) × w
```

- ⚠️ **只使用工作状态=True的轨迹点**参与面积计算
- `w` 为可配置农机作业幅宽(米)
- 输出：平方米、亩 (1亩 = 666.67㎡)

### 4. 平均作业速度 vwork

```
vwork = Σ Pi.velocity / n
```

- 仅取**工作状态=True**的有效轨迹点Pi的速度做算术平均
- 过滤不合理异常速度

## API接口

### 1. 分析单条轨迹

```
GET /api/analysis/track/<track_id>/?work_width=2.0
```

**参数：**
- `track_id`: 轨迹ID（路径参数）
- `work_width`: 农机作业幅宽(米)，可选，默认2.0米

**返回示例：**
```json
{
  "track_id": 1,
  "total_time": {
    "seconds": 3600.5,
    "formatted": "01:00:00"
  },
  "total_distance": {
    "meters": 5234.67,
    "kilometers": 5.235
  },
  "work_area": {
    "square_meters": 10469.34,
    "mu": 15.704
  },
  "average_velocity": {
    "m_per_s": 2.345,
    "km_per_h": 8.442
  },
  "work_width": 2.0
}
```

### 2. 分析所有轨迹

```
GET /api/analysis/all-tracks/?work_width=2.0
```

**参数：**
- `work_width`: 农机作业幅宽(米)，可选，默认2.0米

**返回：** 所有轨迹的统计结果数组

### 3. 获取汇总统计

```
GET /api/analysis/summary/?work_width=2.0
```

**参数：**
- `work_width`: 农机作业幅宽(米)，可选，默认2.0米

**返回示例：**
```json
{
  "total_tracks": 10,
  "total_time": {
    "seconds": 36000.0,
    "formatted": "10:00:00"
  },
  "total_distance": {
    "meters": 52346.7,
    "kilometers": 52.347
  },
  "total_area": {
    "square_meters": 104693.4,
    "mu": 157.04
  },
  "average_velocity": {
    "m_per_s": 2.456,
    "km_per_h": 8.842
  },
  "work_width": 2.0
}
```

## 使用方法

### 1. Python代码调用

```python
from BackEnd.analysis.workload import calculate_workload, get_workload_summary

# 计算单条轨迹
result = calculate_workload(track_id=1, work_width=2.5)
print(f"作业时长: {result['total_time']['formatted']}")
print(f"作业面积: {result['work_area']['mu']:.3f}亩")

# 获取汇总统计
summary = get_workload_summary(work_width=2.0)
print(f"总作业面积: {summary['total_area']['mu']:.3f}亩")
```

### 2. HTTP API调用

```bash
# 分析单条轨迹
curl "http://localhost:8000/api/analysis/track/1/?work_width=2.0"

# 分析所有轨迹
curl "http://localhost:8000/api/analysis/all-tracks/?work_width=2.0"

# 获取汇总统计
curl "http://localhost:8000/api/analysis/summary/?work_width=2.0"
```

### 3. 运行测试脚本

```bash
cd BackEnd
python -m BackEnd.analysis.test_workload
```

## 配置参数

### 作业幅宽 (work_width)

- **默认值：** 2.0米
- **作用：** 用于计算作业面积
- **可配置范围：** 根据实际农机设备调整

### 异常速度过滤

- **最小速度：** 0.0 m/s
- **最大速度：** 50.0 m/s (180 km/h)
- **过滤逻辑：** 超出范围的速度值不参与平均速度计算

## 数据要求

### 轨迹点数据 (Trackpoints)

- `gpstime`: GPS时间
- `x`, `y`: 平面坐标（单位：米）
- `velocity`: 速度（单位：米/秒）
- `workstatus`: 工作状态（1=工作，0=非工作）

### 轨迹数据 (Track)

- `trackid`: 轨迹ID
- `starttime`: 开始时间
- `endtime`: 结束时间

## 文件结构

```
BackEnd/analysis/
├── __init__.py           # 模块初始化
├── workload.py           # 核心计算逻辑
├── api.py                # API接口定义
├── test_workload.py      # 测试脚本
└── README.md             # 本文档
```

## 注意事项

1. **坐标系统：** 假设x, y坐标已经是投影后的平面坐标（单位：米），如果使用经纬度需要先进行投影转换。

2. **工作状态判断：** 默认`workstatus=1`表示工作状态，可根据实际数据结构调整。

3. **时间格式：** 输出的时间格式为`HH:mm:ss`，支持超过24小时的累计时间。

4. **精度：** 所有数值计算结果保留2-3位小数。

5. **性能：** 对于大量轨迹点的数据，建议使用数据库查询优化。
