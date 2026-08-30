# 🚜 农机作业数据处理与分析软件

> Agricultural Machinery Operation Data Processing and Analysis Software

一个全栈 Web 应用程序，用于农机作业 GPS 轨迹数据的导入、管理、可视化与分析。支持 CSV/Excel 轨迹文件上传，在地图上可视化作业轨迹，自动计算作业指标（作业面积、时长、距离、速度等），并提供基于 RBAC 的用户、角色和菜单权限管理。

---

## 📑 目录

- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [页面展示](#页面展示)
- [数据库设计](#数据库设计)
- [API 接口](#api-接口)
- [认证流程](#认证流程)

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端框架** | Django 4.2 + Django REST Framework 3.14 |
| **数据库** | SQLite3（开发） / MySQL（生产，通过 PyMySQL） |
| **前端框架** | Vue 3（Composition API，`<script setup>`） |
| **构建工具** | Vite 6 |
| **UI 组件库** | Element Plus 2.8 |
| **地图** | Leaflet 1.9 + @vue-leaflet/vue-leaflet + 高德瓦片图 |
| **路由** | Vue Router 4 |
| **HTTP 客户端** | Axios |
| **Excel 解析** | openpyxl（.xlsx）、xlrd（.xls） |
| **认证** | 自定义 Token 认证（MD5 密码 + UUID 令牌） |

---

## 项目结构

```
├── BackEnd/                        # Django 后端
│   ├── settings.py                 # Django 配置（中文、上海时区）
│   ├── urls.py                     # 主路由（传统视图 + DRF 路由）
│   ├── views.py                    # 核心视图（用户/角色/菜单/文件 CRUD + 数据导入）
│   ├── generated_api/              # 自动生成的 DRF API 模块
│   │   ├── models.py               # 数据模型（User/Role/Menu/Track/Trackpoints/Work/Rate 等）
│   │   ├── serializers.py          # DRF 序列化器
│   │   ├── views.py                # DRF ViewSet（含自定义 action）
│   │   └── urls.py                 # DRF Router 路由注册
│   ├── scripts/                    # 数据处理与维护脚本
│   │   ├── import_datasets_to_sqlite.py  # CSV 批量导入
│   │   ├── backfill_existing_tracks.py   # 数据回填
│   │   ├── fetch_menu.py                 # 菜单工具
│   │   └── ...                           # 共 18 个脚本
│   ├── tools/
│   │   ├── generate_backend_code.py      # 代码生成器（MySQL → Django Model）
│   │   └── README_codegen.md             # 生成器使用文档
│   └── requirements.txt            # Python 依赖
│
├── FrontEndVue3/                   # Vue 3 前端
│   ├── src/
│   │   ├── main.js                 # 应用入口
│   │   ├── App.vue                 # 根组件
│   │   ├── router/index.js         # 路由定义 + 导航守卫
│   │   ├── layouts/
│   │   │   └── MainLayout.vue      # 主布局（侧边栏 + 顶栏 + 内容区）
│   │   ├── components/
│   │   │   ├── AppHeader.vue       # 顶部导航栏
│   │   │   ├── SidebarMenu.vue     # 可折叠动态菜单
│   │   │   └── DatasetUploadPanel.vue  # 文件上传拖放面板
│   │   ├── views/
│   │   │   ├── Login.vue           # 登录页
│   │   │   ├── Register.vue        # 注册页
│   │   │   ├── Home.vue            # 仪表盘首页
│   │   │   ├── TrackList.vue       # 轨迹列表
│   │   │   ├── TrackMap.vue        # 轨迹地图（Leaflet 可视化）
│   │   │   ├── DataImport.vue      # 数据导入
│   │   │   ├── ImportLog.vue       # 导入日志
│   │   │   ├── UserManage.vue      # 用户管理
│   │   │   ├── RoleManage.vue      # 角色管理
│   │   │   ├── MenuManage.vue      # 菜单管理
│   │   │   ├── File.vue            # 文件管理
│   │   │   ├── PersonInfo.vue      # 个人信息
│   │   │   ├── UpdatePassWord.vue  # 修改密码
│   │   │   └── NotFound.vue        # 404 页面
│   │   ├── utils/
│   │   │   ├── request.js          # Axios 实例 + 拦截器
│   │   │   ├── auth.js             # 认证工具函数
│   │   │   ├── menu.js             # 菜单权限检查
│   │   │   └── response.js         # 响应数据解析
│   │   └── styles/
│   │       └── global.css          # 全局样式
│   ├── vite.config.js              # Vite 配置（代理到 Django）
│   └── package.json                # 前端依赖
│
├── datasets/                       # 上传的数据文件
│   ├── csv/                        # CSV 轨迹文件
│   ├── xlsx/                       # Excel 轨迹文件
│   └── 遥感图/                     # 遥感图像
│
├── images/                         # 截图与文档资源
├── db.sqlite3                      # SQLite 数据库文件
└── README.md
```

---

## 核心功能

### 🗺️ 轨迹数据导入
- 支持 CSV、Excel（.xls / .xlsx）格式上传
- 智能列名映射引擎，兼容中英文多种命名字段
- 自动识别：GPS 时间、经度、纬度、速度、作业状态、幅宽、耕深等
- 坐标合法性校验（经纬度范围检查）
- 上传文件 MD5 去重

### 📊 作业指标计算
- **Haversine 公式**计算点对点球面距离
- 自动统计：作业时长、总距离、作业面积、平均速度、通过率、生产率
- 所有指标在数据导入时自动计算并入库

### 🗺️ 轨迹地图可视化
- Leaflet 集成 + 高德卫星/矢量瓦片图
- 作业状态颜色编码（绿色 = 作业中，灰色 = 停止）
- 动态轨迹播放动画
- 测距工具（点击放置测距点，实时累计距离）
- WGS84 → GCJ-02 坐标变换（适配国内地图）
- 详情面板：轨迹 ID、点数、速度、耕深、作业统计

### 👥 RBAC 权限管理
- **用户管理**：创建/编辑/删除用户，分配角色
- **角色管理**：定义角色，分配菜单访问权限（树形复选框）
- **菜单管理**：管理导航菜单树（名称、路径、图标、父级、页面路径）
- 侧边栏菜单根据用户角色动态渲染
- 路由守卫拦截无权限访问

### 📁 文件管理
- 查看上传文件列表（名称、类型、大小、MD5）
- 文件下载与删除
- 支持查看遥感图像

### 📋 导入日志
- 完整记录每次数据导入操作
- 显示导入时间、文件名、导入数量、成功/失败状态、错误详情

### 📈 仪表盘
- 轨迹、用户、角色、文件数量统计卡片
- 最近导入轨迹列表
- 系统使用指南

---

## 快速开始

### 环境要求

- **Python** >= 3.9
- **Node.js** >= 18
- **npm** >= 9

### 后端启动

```bash
cd BackEnd

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行）
python manage.py migrate

# 启动 Django 开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端启动

```bash
cd FrontEndVue3

# 安装依赖
npm install

# 启动 Vite 开发服务器
npm run dev
```

前端开发服务器运行在 `http://localhost:5174`，API 请求自动代理到 `http://127.0.0.1:8000`。

---

## 页面展示

### 登录与仪表盘
| 登录页 | 仪表盘首页 |
|--------|-----------|
| ![登录](images/e628c2937da440c3b1d470956cd69148.jpg) | ![首页](images/906824d1fcdd47cfbe2e67449a834956.jpg) |

### 轨迹管理
| 轨迹列表 | 轨迹地图 |
|----------|----------|
| ![轨迹管理](images/轨迹管理页面.png) | ![轨迹展示](images/轨迹展示页面.png) |

| 轨迹矢量图 | 轨迹播放 |
|-----------|----------|
| ![轨迹矢量](images/轨迹矢量展示页面.png) | *支持动态播放动画* |

### 系统管理
| 用户管理 | 角色管理 |
|----------|----------|
| ![用户管理](images/用户管理页面.png) | ![角色管理](images/角色管理页面.png) |

| 菜单管理 | 文件管理 |
|----------|----------|
| ![菜单管理](images/菜单管理页面.png) | ![文件管理](images/文件管理页面.png) |

### 个人中心
| 个人信息 | 修改密码 |
|----------|----------|
| ![个人信息](images/个人信息修改页面.png) | ![修改密码](images/修改密码界面.png) |

---

## 数据库设计

### ER 图（核心表关系）

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│   role   │────<│   user   │     │     file     │
└──────────┘     └──────────┘     └──────────────┘
     │                 │
     │            ┌────┴────┐
     │            │import_log│
┌────┴────┐      └──────────┘
│role_menu│
└────┬────┘
     │
┌────┴────┐      ┌──────────┐     ┌──────────────┐
│  menu   │      │  track   │────<│ trackpoints  │
└─────────┘      └────┬─────┘     └──────────────┘
                       │
                  ┌────┴─────┐
                  │   work   │
                  └──────────┘
                  ┌──────────┐
                  │   rate   │
                  └──────────┘
```

### 核心表说明

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `user` | 用户账户 | username, password, nickname, email, role_id, avatar_url |
| `role` | 角色定义 | name, description, flag |
| `menu` | 导航菜单 | name, path, icon, pid (父级自引用), page_path |
| `role_menu` | 角色-菜单关联 | role_id, menu_id (复合唯一) |
| `file` | 上传文件 | name, type, size, url, md5, is_delete |
| `import_log` | 导入日志 | admin_id, file_name, import_count, import_status, error_info |
| `track` | 轨迹批次 | trackid, starttime, endtime, width, totalpoints |
| `trackpoints` | GPS轨迹点 | trackid, gpstime, lon, lat, velocity, workstatus, width, depth |
| `work` | 作业汇总 | trackid, worktime, worklength, workarea, avgvelocity |
| `rate` | 作业效率 | trackid, passrate, productionrate, timerrate |
| `dict` | 字典数据 | name, value, type |

---

## API 接口

### 传统视图接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/user/login` | 用户登录 |
| POST | `/user/register` | 用户注册 |
| GET | `/user/page` | 用户分页列表 |
| POST | `/user/save` | 新增/更新用户 |
| DELETE | `/user/delete` | 删除用户 |
| GET | `/role/page` | 角色分页列表 |
| POST | `/role/save` | 新增/更新角色 |
| GET | `/menu/entry` | 菜单列表（树形） |
| POST | `/menu/save` | 新增/更新菜单 |
| GET | `/file/page` | 文件分页列表 |
| POST | `/upload/file` | 上传文件 |
| POST | `/import/data` | 导入轨迹数据 |
| GET | `/import/log/page` | 导入日志分页 |

### DRF RESTful 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/track/` | 轨迹列表 / 创建 |
| GET/PUT/DELETE | `/api/track/{id}/` | 轨迹详情 / 更新 / 删除 |
| GET | `/api/track/{id}/trackpoints/` | 获取轨迹点 |
| GET/POST | `/api/user/` | 用户列表 / 创建 |
| GET/PUT/DELETE | `/api/user/{id}/` | 用户详情 / 更新 / 删除 |
| GET/POST | `/api/role/` | 角色列表 / 创建 |
| GET/POST | `/api/menu/` | 菜单列表 / 创建 |
| GET | `/api/import-log/` | 导入日志列表 |
| GET | `/api/work/` | 作业指标列表 |
| GET | `/api/rate/` | 效率指标列表 |

---

## 认证流程

1. 用户在登录页输入用户名和密码
2. 前端 POST `/user/login` → Django 使用 MD5 验证密码
3. 验证通过后返回：用户对象 + 菜单权限树 + UUID 令牌
4. 前端将 `user`、`menus`、`token` 存储到 `localStorage`
5. 后续请求通过 Axios 拦截器自动附加认证头：
   - `token`: UUID 令牌
   - `Authorization`: Bearer 令牌
   - `X-User-Id`: 当前用户 ID
   - `X-User-Role`: 当前用户角色
6. 路由守卫根据用户菜单权限限制页面访问

---

> 📝 **开发环境**：后端运行在 `localhost:8000`，前端运行在 `localhost:5174`，通过 Vite 代理转发 API 请求。
