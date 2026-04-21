import hashlib
import os
import uuid
from pathlib import Path

import pymysql
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


def ok(data=None, msg="success"):
    return Response({"code": "200", "data": data, "msg": msg})


def fail(msg="failed", code="500", data=None):
    return Response({"code": str(code), "data": data, "msg": msg})


def _db_conf():
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "wanaihua"),
        "database": os.getenv("MYSQL_DB", "agricultural_machinery_db"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
    }


def _fetch_all(sql, params=None):
    conn = pymysql.connect(**_db_conf())
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
    finally:
        conn.close()


def _fetch_one(sql, params=None):
    rows = _fetch_all(sql, params)
    return rows[0] if rows else None


def _execute(sql, params=None):
    conn = pymysql.connect(**_db_conf())
    try:
        with conn.cursor() as cursor:
            count = cursor.execute(sql, params or ())
            return count
    finally:
        conn.close()


def _build_menu_tree(rows):
    by_id = {}
    roots = []
    for item in rows:
        node = {
            "id": item.get("id"),
            "name": item.get("name"),
            "path": item.get("path"),
            "icon": item.get("icon"),
            "description": item.get("description"),
            "pid": item.get("pid"),
            "pagePath": item.get("pagePath"),
            "children": [],
        }
        by_id[node["id"]] = node

    for node in by_id.values():
        pid = node.get("pid")
        if pid and pid in by_id:
            by_id[pid]["children"].append(node)
        else:
            roots.append(node)

    return roots


def _to_md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


_USER_HAS_IS_DELETE = None


def _user_has_is_delete():
    global _USER_HAS_IS_DELETE
    if _USER_HAS_IS_DELETE is not None:
        return _USER_HAS_IS_DELETE

    row = _fetch_one(
        """
        SELECT COUNT(*) AS cnt
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'user' AND column_name = 'is_delete'
        """,
        (_db_conf()["database"],),
    )
    _USER_HAS_IS_DELETE = bool(row and row.get("cnt", 0) > 0)
    return _USER_HAS_IS_DELETE
 
@api_view(['GET'])
def get_data(request):
    data = {'message': 'Hello from Django!'}
    return Response(data)


@api_view(['POST'])
def login_test(request):
    username = request.data.get('username')
    password = request.data.get('password')
    db_host = os.getenv('MYSQL_HOST', '127.0.0.1')
    db_port = int(os.getenv('MYSQL_PORT', '3306'))
    db_user = os.getenv('MYSQL_USER', 'root')
    db_password = os.getenv('MYSQL_PASSWORD', 'wanaihua')
    db_name = os.getenv('MYSQL_DB', 'agricultural_machinery_db')

    conn = None

    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception as exc:
        return Response({'ok': False, 'connected': False, 'error': str(exc)}, status=500)
    finally:
        if conn is not None:
            conn.close()

    if not username or not password:
        return Response({'ok': False, 'connected': True, 'message': 'username/password required'}, status=400)

    md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()

    try:
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, role
                FROM user_info
                WHERE username = %s AND LOWER(password) = %s AND IFNULL(is_delete, 0) = 0
                LIMIT 1
                """,
                (username, md5_password),
            )
            user = cursor.fetchone()
    except Exception as exc:
        return Response({'ok': False, 'connected': False, 'error': str(exc)}, status=500)
    finally:
        if conn is not None:
            conn.close()

    if user:
        return Response({'ok': True, 'connected': True, 'user_id': user['id'], 'role': user['role']})

    return Response({'ok': False, 'connected': True, 'message': 'invalid credentials'}, status=401)


@api_view(["POST"])
def user_login(request):
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""
    if not username or not password:
        return fail("用户名或密码不能为空", code="400")

    md5_password = _to_md5(password)
    active_filter = "AND IFNULL(is_delete, 0) = 0" if _user_has_is_delete() else ""
    sql = f"""
    SELECT id, username, nickname, email, phone, address, avatar_url AS avatarUrl, role
    FROM user
    WHERE username = %s
      {active_filter}
      AND (LOWER(password) = %s OR password = %s)
    LIMIT 1
    """
    user = _fetch_one(sql, (username, md5_password, password))
    if not user:
        return fail("用户名或密码错误", code="401")

    role_flag = user.get("role")
    menus_sql = """
    SELECT m.id, m.name, m.path, m.icon, m.description, m.pid, m.page_path AS pagePath
    FROM menu m
    JOIN role_menu rm ON rm.menu_id = m.id
    JOIN role r ON r.id = rm.role_id
    WHERE r.flag = %s
    ORDER BY m.id
    """
    menus = _fetch_all(menus_sql, (role_flag,)) if role_flag else []
    user["menus"] = _build_menu_tree(menus)
    user["token"] = str(uuid.uuid4())
    return ok(user, "登录成功")


@api_view(["POST"])
def user_register(request):
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""
    if not username or not password:
        return fail("用户名或密码不能为空", code="400")

    exists = _fetch_one("SELECT id FROM user WHERE username = %s LIMIT 1", (username,))
    if exists:
        return fail("用户名已存在", code="400")

    if _user_has_is_delete():
        _execute(
            """
            INSERT INTO user(username, password, nickname, role, is_delete)
            VALUES(%s, %s, %s, %s, 0)
            """,
            (username, _to_md5(password), username, "ROLE_USER"),
        )
    else:
        _execute(
            """
            INSERT INTO user(username, password, nickname, role)
            VALUES(%s, %s, %s, %s)
            """,
            (username, _to_md5(password), username, "ROLE_USER"),
        )
    user = _fetch_one(
        "SELECT id, username, nickname, email, phone, address, avatar_url AS avatarUrl, role FROM user WHERE username=%s LIMIT 1",
        (username,),
    )
    user["menus"] = []
    user["token"] = str(uuid.uuid4())
    return ok(user, "注册成功")


@api_view(["GET"])
def user_by_username(request, username):
    user = _fetch_one(
        """
        SELECT id, username, password, nickname, email, phone, address, avatar_url AS avatarUrl, role
        FROM user
        WHERE username = %s
        LIMIT 1
        """,
        (username,),
    )
    return ok(user)


@api_view(["GET"])
def user_page(request):
    page_num = int(request.query_params.get("pageNum", 1))
    page_size = int(request.query_params.get("pageSize", 10))
    username = request.query_params.get("username", "")
    address = request.query_params.get("address", "")
    email = request.query_params.get("email", "")
    active_where = "IFNULL(is_delete,0)=0 AND " if _user_has_is_delete() else ""
    where = f"WHERE {active_where}username LIKE %s AND address LIKE %s AND email LIKE %s"
    params = (f"%{username}%", f"%{address}%", f"%{email}%")
    total_row = _fetch_one(f"SELECT COUNT(*) AS total FROM user {where}", params)
    total = total_row["total"] if total_row else 0
    offset = (page_num - 1) * page_size
    rows = _fetch_all(
        f"""
        SELECT id, username, nickname, email, phone, address, avatar_url AS avatarUrl, role
        FROM user
        {where}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
        """,
        params + (page_size, offset),
    )
    return ok({"records": rows, "total": total})


@api_view(["POST"])
def user_save(request):
    body = request.data or {}
    user_id = body.get("id")
    password = body.get("password")
    if password and len(password) != 32:
        body["password"] = _to_md5(password)

    if user_id:
        fields = []
        values = []
        for key, col in [
            ("username", "username"),
            ("password", "password"),
            ("nickname", "nickname"),
            ("email", "email"),
            ("phone", "phone"),
            ("address", "address"),
            ("avatarUrl", "avatar_url"),
            ("role", "role"),
        ]:
            if key in body and body.get(key) is not None:
                fields.append(f"{col}=%s")
                values.append(body.get(key))
        if fields:
            values.append(user_id)
            _execute(f"UPDATE user SET {', '.join(fields)} WHERE id=%s", tuple(values))
        return ok(True, "保存成功")

    if _user_has_is_delete():
        _execute(
            """
            INSERT INTO user(username, password, nickname, email, phone, address, avatar_url, role, is_delete)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 0)
            """,
            (
                body.get("username"),
                body.get("password") or _to_md5("123456"),
                body.get("nickname"),
                body.get("email"),
                body.get("phone"),
                body.get("address"),
                body.get("avatarUrl"),
                body.get("role") or "ROLE_USER",
            ),
        )
    else:
        _execute(
            """
            INSERT INTO user(username, password, nickname, email, phone, address, avatar_url, role)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                body.get("username"),
                body.get("password") or _to_md5("123456"),
                body.get("nickname"),
                body.get("email"),
                body.get("phone"),
                body.get("address"),
                body.get("avatarUrl"),
                body.get("role") or "ROLE_USER",
            ),
        )
    return ok(True, "新增成功")


@api_view(["POST"])
def user_update_password(request):
    username = (request.data.get("username") or "").strip()
    old_password = request.data.get("oldPassword") or ""
    new_password = request.data.get("newPassword") or ""

    if not username or not old_password or not new_password:
        return fail("参数不完整", code="400")

    active_filter = "AND IFNULL(is_delete,0)=0" if _user_has_is_delete() else ""
    user = _fetch_one(
        f"SELECT id, password FROM user WHERE username=%s {active_filter} LIMIT 1",
        (username,),
    )
    if not user:
        return fail("用户不存在", code="404")

    stored_password = (user.get("password") or "").lower()
    old_md5 = _to_md5(old_password)
    # Compatible with both legacy plaintext and md5 storage.
    if stored_password not in {old_password.lower(), old_md5.lower()}:
        return fail("原密码错误", code="400")

    _execute("UPDATE user SET password=%s WHERE id=%s", (_to_md5(new_password), user["id"]))
    return ok(True, "密码修改成功")


@api_view(["DELETE"])
def user_delete(request, user_id):
    if _user_has_is_delete():
        _execute("UPDATE user SET is_delete=1 WHERE id=%s", (user_id,))
    else:
        _execute("DELETE FROM user WHERE id=%s", (user_id,))
    return ok(True, "删除成功")


@api_view(["POST"])
def user_delete_batch(request):
    ids = request.data or []
    if not ids:
        return fail("未提供ID", code="400")
    placeholders = ",".join(["%s"] * len(ids))
    if _user_has_is_delete():
        _execute(f"UPDATE user SET is_delete=1 WHERE id IN ({placeholders})", tuple(ids))
    else:
        _execute(f"DELETE FROM user WHERE id IN ({placeholders})", tuple(ids))
    return ok(True, "批量删除成功")


@api_view(["GET"])
def role_list(request):
    rows = _fetch_all("SELECT id, name, flag, description FROM role ORDER BY id DESC")
    return ok(rows)


@api_view(["GET", "POST"])
def role_entry(request):
    if request.method == "GET":
        rows = _fetch_all("SELECT id, name, flag, description FROM role ORDER BY id DESC")
        return ok(rows)

    body = request.data or {}
    role_id = body.get("id")
    if role_id:
        _execute(
            "UPDATE role SET name=%s, flag=%s, description=%s WHERE id=%s",
            (body.get("name"), body.get("flag"), body.get("description"), role_id),
        )
        return ok(True, "保存成功")

    _execute(
        "INSERT INTO role(name, flag, description) VALUES(%s, %s, %s)",
        (body.get("name"), body.get("flag"), body.get("description")),
    )
    return ok(True, "新增成功")


@api_view(["GET"])
def role_page(request):
    page_num = int(request.query_params.get("pageNum", 1))
    page_size = int(request.query_params.get("pageSize", 10))
    name = request.query_params.get("name", "")
    total_row = _fetch_one("SELECT COUNT(*) AS total FROM role WHERE name LIKE %s", (f"%{name}%",))
    total = total_row["total"] if total_row else 0
    offset = (page_num - 1) * page_size
    rows = _fetch_all(
        "SELECT id, name, flag, description FROM role WHERE name LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
        (f"%{name}%", page_size, offset),
    )
    return ok({"records": rows, "total": total})


@api_view(["POST"])
def role_save(request):
    body = request.data or {}
    role_id = body.get("id")
    if role_id:
        _execute(
            "UPDATE role SET name=%s, flag=%s, description=%s WHERE id=%s",
            (body.get("name"), body.get("flag"), body.get("description"), role_id),
        )
        return ok(True, "保存成功")
    _execute(
        "INSERT INTO role(name, flag, description) VALUES(%s, %s, %s)",
        (body.get("name"), body.get("flag"), body.get("description")),
    )
    return ok(True, "新增成功")


@api_view(["DELETE"])
def role_delete(request, role_id):
    _execute("DELETE FROM role_menu WHERE role_id=%s", (role_id,))
    _execute("DELETE FROM role WHERE id=%s", (role_id,))
    return ok(True, "删除成功")


@api_view(["POST"])
def role_delete_batch(request):
    ids = request.data or []
    if not ids:
        return fail("未提供ID", code="400")
    placeholders = ",".join(["%s"] * len(ids))
    _execute(f"DELETE FROM role_menu WHERE role_id IN ({placeholders})", tuple(ids))
    _execute(f"DELETE FROM role WHERE id IN ({placeholders})", tuple(ids))
    return ok(True, "批量删除成功")


@api_view(["POST"])
def role_role_menu_save(request, role_id):
    menu_ids = request.data or []
    _execute("DELETE FROM role_menu WHERE role_id=%s", (role_id,))
    for menu_id in menu_ids:
        _execute("INSERT INTO role_menu(role_id, menu_id) VALUES(%s, %s)", (role_id, menu_id))
    return ok(True, "保存成功")


@api_view(["GET", "POST"])
def role_role_menu_entry(request, role_id):
    if request.method == "GET":
        rows = _fetch_all("SELECT menu_id FROM role_menu WHERE role_id=%s", (role_id,))
        return ok([row["menu_id"] for row in rows])

    menu_ids = request.data or []
    _execute("DELETE FROM role_menu WHERE role_id=%s", (role_id,))
    for menu_id in menu_ids:
        _execute("INSERT INTO role_menu(role_id, menu_id) VALUES(%s, %s)", (role_id, menu_id))
    return ok(True, "保存成功")


@api_view(["GET"])
def role_role_menu(request, role_id):
    rows = _fetch_all("SELECT menu_id FROM role_menu WHERE role_id=%s", (role_id,))
    return ok([row["menu_id"] for row in rows])


@api_view(["GET"])
def menu_list(request):
    name = request.query_params.get("name", "")
    rows = _fetch_all(
        """
        SELECT id, name, path, icon, description, pid, page_path AS pagePath
        FROM menu
        WHERE name LIKE %s
        ORDER BY id
        """,
        (f"%{name}%",),
    )
    return ok(_build_menu_tree(rows))


@api_view(["GET", "POST"])
def menu_entry(request):
    if request.method == "GET":
        name = request.query_params.get("name", "")
        rows = _fetch_all(
            """
            SELECT id, name, path, icon, description, pid, page_path AS pagePath
            FROM menu
            WHERE name LIKE %s
            ORDER BY id
            """,
            (f"%{name}%",),
        )
        return ok(_build_menu_tree(rows))

    body = request.data or {}
    menu_id = body.get("id")
    if menu_id:
        _execute(
            "UPDATE menu SET name=%s, path=%s, icon=%s, description=%s, pid=%s, page_path=%s WHERE id=%s",
            (
                body.get("name"),
                body.get("path"),
                body.get("icon"),
                body.get("description"),
                body.get("pid"),
                body.get("pagePath"),
                menu_id,
            ),
        )
        return ok(True, "保存成功")

    _execute(
        "INSERT INTO menu(name, path, icon, description, pid, page_path) VALUES(%s, %s, %s, %s, %s, %s)",
        (
            body.get("name"),
            body.get("path"),
            body.get("icon"),
            body.get("description"),
            body.get("pid"),
            body.get("pagePath"),
        ),
    )
    return ok(True, "新增成功")


@api_view(["GET"])
def menu_ids(request):
    rows = _fetch_all("SELECT id FROM menu ORDER BY id")
    return ok([r["id"] for r in rows])


@api_view(["GET"])
def menu_icons(request):
    icons = [
        {"name": "用户", "value": "el-icon-user"},
        {"name": "菜单", "value": "el-icon-menu"},
        {"name": "设置", "value": "el-icon-setting"},
        {"name": "数据", "value": "el-icon-data-analysis"},
        {"name": "文档", "value": "el-icon-document"},
    ]
    return ok(icons)


@api_view(["POST"])
def menu_save(request):
    body = request.data or {}
    menu_id = body.get("id")
    if menu_id:
        _execute(
            "UPDATE menu SET name=%s, path=%s, icon=%s, description=%s, pid=%s, page_path=%s WHERE id=%s",
            (
                body.get("name"),
                body.get("path"),
                body.get("icon"),
                body.get("description"),
                body.get("pid"),
                body.get("pagePath"),
                menu_id,
            ),
        )
        return ok(True, "保存成功")
    _execute(
        "INSERT INTO menu(name, path, icon, description, pid, page_path) VALUES(%s, %s, %s, %s, %s, %s)",
        (
            body.get("name"),
            body.get("path"),
            body.get("icon"),
            body.get("description"),
            body.get("pid"),
            body.get("pagePath"),
        ),
    )
    return ok(True, "新增成功")


@api_view(["DELETE"])
def menu_delete(request, menu_id):
    _execute("DELETE FROM role_menu WHERE menu_id=%s", (menu_id,))
    _execute("DELETE FROM menu WHERE id=%s OR pid=%s", (menu_id, menu_id))
    return ok(True, "删除成功")


@api_view(["POST"])
def menu_delete_batch(request):
    ids = request.data or []
    if not ids:
        return fail("未提供ID", code="400")
    placeholders = ",".join(["%s"] * len(ids))
    _execute(f"DELETE FROM role_menu WHERE menu_id IN ({placeholders})", tuple(ids))
    _execute(f"DELETE FROM menu WHERE id IN ({placeholders})", tuple(ids))
    return ok(True, "批量删除成功")


@api_view(["GET"])
def file_page(request):
    page_num = int(request.query_params.get("pageNum", 1))
    page_size = int(request.query_params.get("pageSize", 10))
    name = request.query_params.get("name", "")
    total_row = _fetch_one("SELECT COUNT(*) AS total FROM file WHERE IFNULL(is_delete,0)=0 AND name LIKE %s", (f"%{name}%",))
    total = total_row["total"] if total_row else 0
    offset = (page_num - 1) * page_size
    rows = _fetch_all(
        """
        SELECT id, name, type, size, url, is_delete, enable, md5
        FROM file
        WHERE IFNULL(is_delete,0)=0 AND name LIKE %s
        ORDER BY id DESC
        LIMIT %s OFFSET %s
        """,
        (f"%{name}%", page_size, offset),
    )
    return ok({"records": rows, "total": total})


@api_view(["DELETE"])
def file_delete(request, file_id):
    _execute("UPDATE file SET is_delete=1 WHERE id=%s", (file_id,))
    return ok(True, "删除成功")


@api_view(["POST"])
def file_delete_batch(request):
    ids = request.data or []
    if not ids:
        return fail("未提供ID", code="400")
    placeholders = ",".join(["%s"] * len(ids))
    _execute(f"UPDATE file SET is_delete=1 WHERE id IN ({placeholders})", tuple(ids))
    return ok(True, "批量删除成功")


@api_view(["POST"])
def file_update(request):
    row = request.data or {}
    _execute(
        "UPDATE file SET name=%s, type=%s, size=%s, url=%s, enable=%s, md5=%s WHERE id=%s",
        (
            row.get("name"),
            row.get("type"),
            row.get("size"),
            row.get("url"),
            1 if row.get("enable") else 0,
            row.get("md5"),
            row.get("id"),
        ),
    )
    return ok(True, "操作成功")


@api_view(["POST"])
def file_upload(request):
    uploaded_file = request.FILES.get("file") or next(iter(request.FILES.values()), None)
    if uploaded_file is None:
        return Response({"code": "400", "data": None, "msg": "未获取到上传文件"}, status=400)

    # 先基于上传内容计算md5，命中则复用已有文件URL，避免重复落盘
    md5_ctx = hashlib.md5()
    for chunk in uploaded_file.chunks():
        md5_ctx.update(chunk)
    file_md5 = md5_ctx.hexdigest()

    existed = _fetch_one(
        """
        SELECT id, url
        FROM file
        WHERE md5=%s AND IFNULL(is_delete,0)=0
        ORDER BY id DESC
        LIMIT 1
        """,
        (file_md5,),
    )
    if existed and existed.get("url"):
        return JsonResponse(existed.get("url"), safe=False)

    uploaded_file.seek(0)

    media_root = Path(settings.MEDIA_ROOT)
    media_root.mkdir(parents=True, exist_ok=True)

    original_name = uploaded_file.name
    suffix = Path(original_name).suffix
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = media_root / stored_name

    with open(file_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    file_size_kb = round(file_path.stat().st_size / 1024, 2)
    backend_public_url = os.getenv("BACKEND_PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")
    file_url = f"{backend_public_url}{settings.MEDIA_URL}{stored_name}"

    _execute(
        """
        INSERT INTO file(name, type, size, url, is_delete, enable, md5)
        VALUES(%s, %s, %s, %s, 0, 1, %s)
        """,
        (
            Path(original_name).stem,
            suffix.lstrip(".").lower(),
            file_size_kb,
            file_url,
            file_md5,
        ),
    )

    return JsonResponse(file_url, safe=False)


@api_view(["GET"])
def echarts_members(request):
    rows = _fetch_all(
        """
        SELECT MONTH(creat_time) AS m, COUNT(*) AS c
        FROM user
        WHERE creat_time IS NOT NULL
        GROUP BY MONTH(creat_time)
        ORDER BY MONTH(creat_time)
        """
    )
    data = [0, 0, 0, 0]
    for row in rows:
        month = int(row.get("m") or 0)
        if 1 <= month <= 3:
            data[0] += row["c"]
        elif 4 <= month <= 6:
            data[1] += row["c"]
        elif 7 <= month <= 9:
            data[2] += row["c"]
        elif 10 <= month <= 12:
            data[3] += row["c"]
    return ok(data)