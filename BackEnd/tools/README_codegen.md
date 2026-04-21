# Django 后端代码生成器

该目录下的脚本会根据 MySQL 数据库表结构自动生成 Django + DRF 代码。

## 目标数据库

默认数据库名：`agricultural_machinery_db`

## 安装依赖

在你的 AMOD 环境中安装：

```bash
pip install pymysql
```

## 运行命令

在 `BackEnd` 目录执行：

```bash
python tools/generate_backend_code.py \
  --host 127.0.0.1 \
  --port 3306 \
  --user root \
  --password 你的密码 \
  --db-name agricultural_machinery_db \
  --output-dir generated_api
```

可选：只生成某个前缀的表

```bash
python tools/generate_backend_code.py \
  --user root \
  --password 你的密码 \
  --db-name agricultural_machinery_db \
  --table-prefix am_
```

## 生成内容

生成到 `BackEnd/generated_api/`：

- `models.py`：`managed = False` 的模型
- `serializers.py`：ModelSerializer
- `views.py`：ModelViewSet
- `urls.py`：DRF Router 路由

## 接入主路由

在 `BackEnd/urls.py` 中引入并挂载：

```python
from django.urls import include, path

urlpatterns = [
    path('api/', include('generated_api.urls')),
]
```

> 注意：若你的项目里已有同名路由，请合并后再保存。
