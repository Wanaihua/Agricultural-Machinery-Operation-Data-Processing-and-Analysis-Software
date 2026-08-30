"""
Vue3 前端 SPA 视图 — 托管打包后的 dist 目录
"""

import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


# 静态文件扩展名
STATIC_EXTS = {
    '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
    '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map', '.json',
}

# 强制 MIME 类型映射（避免某些系统 mimetypes 猜错）
EXTRA_MIME = {
    '.js': 'application/javascript',
    '.mjs': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.svg': 'image/svg+xml',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.map': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
}


def serve_frontend(request, path=""):
    """
    托管 Vue3 打包产物

    - 静态文件 (js/css/png/...) → 直接返回文件
    - 其他路径 → 返回 index.html (SPA 路由)
    """
    dist = settings.FRONTEND_DIST

    if not dist.exists():
        raise Http404("前端打包目录不存在，请先运行 npm run build")

    # 从 request.path 获取实际路径
    req_path = request.path.lstrip('/')

    # 尝试返回静态文件
    if req_path:
        file_path = dist / req_path
        if file_path.is_file():
            ext = file_path.suffix.lower()
            content_type = EXTRA_MIME.get(ext) or mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
            response = FileResponse(open(file_path, "rb"), content_type=content_type)
            return response

    # SPA fallback: 返回 index.html
    index = dist / "index.html"
    if index.exists():
        return FileResponse(open(index, "rb"), content_type="text/html")

    raise Http404("index.html 不存在")
