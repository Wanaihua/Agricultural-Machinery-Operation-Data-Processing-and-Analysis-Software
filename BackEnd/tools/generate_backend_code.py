#!/usr/bin/env python
"""Generate Django backend code from a MySQL database schema.

This script reads table/column metadata from information_schema and generates:
- models.py (unmanaged models)
- serializers.py
- views.py (DRF ModelViewSet)
- urls.py (DRF router)
- __init__.py

Example:
python tools/generate_backend_code.py \
  --host 127.0.0.1 --port 3306 \
    --user root --password your_password \
  --db-name agricultural_machinery_db \
  --output-dir generated_api
"""

from __future__ import annotations

import argparse
import importlib
import keyword
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    column_type: str
    is_nullable: bool
    default: Optional[str]
    comment: str
    max_length: Optional[int]
    numeric_precision: Optional[int]
    numeric_scale: Optional[int]
    is_primary: bool
    is_auto_increment: bool
    fk_table: Optional[str]
    fk_column: Optional[str]


@dataclass
class TableInfo:
    name: str
    comment: str
    columns: List[ColumnInfo] = field(default_factory=list)


def snake_to_camel(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    result = "".join(p.capitalize() for p in parts if p)
    return result or "GeneratedModel"


def to_valid_identifier(name: str) -> str:
    value = re.sub(r"\W+", "_", name)
    if not value:
        value = "field"
    if value[0].isdigit():
        value = f"f_{value}"
    if keyword.iskeyword(value):
        value = f"{value}_"
    return value


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Django backend code from MySQL schema")
    parser.add_argument("--host", default="127.0.0.1", help="MySQL host")
    parser.add_argument("--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--user", required=True, help="MySQL username")
    parser.add_argument("--password", required=True, help="MySQL password")
    parser.add_argument(
        "--db-name",
        default="agricultural_machinery_db",
        help="Database name to introspect",
    )
    parser.add_argument(
        "--output-dir",
        default="generated_api",
        help="Directory (relative to BackEnd) for generated files",
    )
    parser.add_argument(
        "--table-prefix",
        default="",
        help="Optional table name prefix filter, e.g. am_",
    )
    return parser.parse_args()


def fetch_schema(args: argparse.Namespace) -> List[TableInfo]:
    try:
        pymysql = importlib.import_module("pymysql")
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: pymysql. Install it with `pip install pymysql`."
        ) from exc

    conn = pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name, IFNULL(table_comment, '') AS table_comment
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """,
                (args.db_name,),
            )
            table_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    c.table_name,
                    c.column_name,
                    c.data_type,
                    c.column_type,
                    c.is_nullable,
                    c.column_default,
                    IFNULL(c.column_comment, '') AS column_comment,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale,
                    c.column_key,
                    c.extra,
                    k.referenced_table_name,
                    k.referenced_column_name
                FROM information_schema.columns c
                LEFT JOIN information_schema.key_column_usage k
                  ON c.table_schema = k.table_schema
                 AND c.table_name = k.table_name
                 AND c.column_name = k.column_name
                 AND k.referenced_table_name IS NOT NULL
                WHERE c.table_schema = %s
                ORDER BY c.table_name, c.ordinal_position
                """,
                (args.db_name,),
            )
            column_rows = cursor.fetchall()
    finally:
        conn.close()

    table_map: Dict[str, TableInfo] = {}
    for row in table_rows:
        name = row["table_name"]
        if args.table_prefix and not name.startswith(args.table_prefix):
            continue
        table_map[name] = TableInfo(name=name, comment=row["table_comment"])

    for row in column_rows:
        table_name = row["table_name"]
        if table_name not in table_map:
            continue
        table_map[table_name].columns.append(
            ColumnInfo(
                name=row["column_name"],
                data_type=row["data_type"],
                column_type=row["column_type"],
                is_nullable=(row["is_nullable"] == "YES"),
                default=row["column_default"],
                comment=row["column_comment"],
                max_length=row["character_maximum_length"],
                numeric_precision=row["numeric_precision"],
                numeric_scale=row["numeric_scale"],
                is_primary=(row["column_key"] == "PRI"),
                is_auto_increment=("auto_increment" in (row["extra"] or "")),
                fk_table=row["referenced_table_name"],
                fk_column=row["referenced_column_name"],
            )
        )

    return [table_map[name] for name in sorted(table_map)]


def map_field_type(col: ColumnInfo) -> Tuple[str, Dict[str, str]]:
    t = col.data_type.lower()

    if col.is_primary and col.is_auto_increment and t in {"int", "integer", "bigint", "smallint"}:
        if t == "bigint":
            return "BigAutoField", {}
        return "AutoField", {}

    if t in {"char", "varchar"}:
        return "CharField", {"max_length": str(col.max_length or 255)}
    if t in {"text", "tinytext", "mediumtext", "longtext"}:
        return "TextField", {}
    if t in {"int", "integer"}:
        return "IntegerField", {}
    if t == "bigint":
        return "BigIntegerField", {}
    if t == "smallint":
        return "SmallIntegerField", {}
    if t == "tinyint":
        if col.column_type.lower() == "tinyint(1)":
            return "BooleanField", {}
        return "SmallIntegerField", {}
    if t in {"decimal", "numeric"}:
        return "DecimalField", {
            "max_digits": str(col.numeric_precision or 10),
            "decimal_places": str(col.numeric_scale or 0),
        }
    if t in {"float", "double", "real"}:
        return "FloatField", {}
    if t == "date":
        return "DateField", {}
    if t == "time":
        return "TimeField", {}
    if t in {"datetime", "timestamp"}:
        return "DateTimeField", {}
    if t in {"json"}:
        return "JSONField", {}
    if t in {"blob", "tinyblob", "mediumblob", "longblob", "binary", "varbinary"}:
        return "BinaryField", {}
    if t in {"enum", "set"}:
        return "CharField", {"max_length": str(col.max_length or 255)}

    return "TextField", {}


def build_field_line(
    col: ColumnInfo,
    table_name: str,
    table_class_name_map: Dict[str, str],
    used_fields: Dict[str, int],
    is_primary_field: bool,
) -> str:
    base_name = to_valid_identifier(col.name)
    if base_name in used_fields:
        used_fields[base_name] += 1
        field_name = f"{base_name}_{used_fields[base_name]}"
    else:
        used_fields[base_name] = 0
        field_name = base_name

    if col.fk_table and col.fk_table in table_class_name_map:
        target_class = table_class_name_map[col.fk_table]
        related_name = f"{to_valid_identifier(table_name)}_{field_name}_set"
        options = [
            f"to='{target_class}'",
            "on_delete=models.DO_NOTHING",
            f"db_column='{col.name}'",
            f"related_name='{related_name}'",
        ]
        if col.is_nullable:
            options.append("null=True")
            options.append("blank=True")
        options.append("db_constraint=False")

        # Preserve PK attribute for unusual schemas where FK is also PK.
        if is_primary_field:
            options.append("primary_key=True")
        return f"    {field_name} = models.ForeignKey({', '.join(options)})"

    django_type, extra_args = map_field_type(col)

    options: List[str] = []
    for k, v in extra_args.items():
        options.append(f"{k}={v}")

    if is_primary_field:
        options.append("primary_key=True")

    if col.is_nullable and not is_primary_field:
        options.append("null=True")
        options.append("blank=True")

    if col.default is not None and not col.is_auto_increment:
        default_val = repr(col.default)
        options.append(f"default={default_val}")

    if col.name != field_name:
        options.append(f"db_column='{col.name}'")

    if col.comment:
        options.append(f"help_text={repr(col.comment)}")

    return f"    {field_name} = models.{django_type}({', '.join(options)})"


def generate_models_file(tables: List[TableInfo]) -> str:
    lines: List[str] = []
    lines.append("\"\"\"Auto-generated Django models.\"\"\"")
    lines.append("")
    lines.append("from django.db import models")
    lines.append("")

    table_class_name_map = {table.name: snake_to_camel(table.name) for table in tables}

    for table in tables:
        class_name = table_class_name_map[table.name]
        pk_columns = [col.name for col in table.columns if col.is_primary]
        primary_column = pk_columns[0] if pk_columns else None
        lines.append(f"class {class_name}(models.Model):")
        if table.comment:
            lines.append(f"    \"\"\"{table.comment}\"\"\"")

        if not table.columns:
            lines.append("    pass")
        else:
            used_fields: Dict[str, int] = {}
            for col in table.columns:
                lines.append(
                    build_field_line(
                        col,
                        table.name,
                        table_class_name_map,
                        used_fields,
                        is_primary_field=(col.name == primary_column),
                    )
                )

        lines.append("")
        lines.append("    class Meta:")
        lines.append("        managed = False")
        lines.append(f"        db_table = '{table.name}'")
        if len(pk_columns) > 1:
            columns = ", ".join(repr(name) for name in pk_columns)
            lines.append(f"        unique_together = (({columns}),)")
        lines.append("")
        lines.append("    def __str__(self):")
        lines.append("        return f'{self.__class__.__name__}(pk={self.pk})'")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def generate_serializers_file(tables: List[TableInfo]) -> str:
    lines: List[str] = []
    lines.append("\"\"\"Auto-generated DRF serializers.\"\"\"")
    lines.append("")
    lines.append("from rest_framework import serializers")
    lines.append("from .models import (")
    for table in tables:
        lines.append(f"    {snake_to_camel(table.name)},")
    lines.append(")")
    lines.append("")

    for table in tables:
        class_name = snake_to_camel(table.name)
        serializer_name = f"{class_name}Serializer"
        lines.append(f"class {serializer_name}(serializers.ModelSerializer):")
        lines.append("    class Meta:")
        lines.append(f"        model = {class_name}")
        lines.append("        fields = '__all__'")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def generate_views_file(tables: List[TableInfo]) -> str:
    lines: List[str] = []
    lines.append("\"\"\"Auto-generated DRF viewsets.\"\"\"")
    lines.append("")
    lines.append("from rest_framework import viewsets")
    lines.append("from .models import (")
    for table in tables:
        lines.append(f"    {snake_to_camel(table.name)},")
    lines.append(")")
    lines.append("from .serializers import (")
    for table in tables:
        lines.append(f"    {snake_to_camel(table.name)}Serializer,")
    lines.append(")")
    lines.append("")

    for table in tables:
        class_name = snake_to_camel(table.name)
        viewset_name = f"{class_name}ViewSet"
        serializer_name = f"{class_name}Serializer"
        lines.append(f"class {viewset_name}(viewsets.ModelViewSet):")
        lines.append(f"    queryset = {class_name}.objects.all()")
        lines.append(f"    serializer_class = {serializer_name}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def generate_urls_file(tables: List[TableInfo]) -> str:
    lines: List[str] = []
    lines.append("\"\"\"Auto-generated DRF router URLs.\"\"\"")
    lines.append("")
    lines.append("from rest_framework.routers import DefaultRouter")
    lines.append("from .views import (")
    for table in tables:
        lines.append(f"    {snake_to_camel(table.name)}ViewSet,")
    lines.append(")")
    lines.append("")
    lines.append("router = DefaultRouter()")

    for table in tables:
        class_name = snake_to_camel(table.name)
        viewset_name = f"{class_name}ViewSet"
        path_name = table.name.lower()
        lines.append(f"router.register(r'{path_name}', {viewset_name}, basename='{path_name}')")

    lines.append("")
    lines.append("urlpatterns = router.urls")
    lines.append("")

    return "\n".join(lines)


def write_generated_files(output_dir: Path, tables: List[TableInfo]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "__init__.py": "",
        "models.py": generate_models_file(tables),
        "serializers.py": generate_serializers_file(tables),
        "views.py": generate_views_file(tables),
        "urls.py": generate_urls_file(tables),
    }

    for file_name, content in files.items():
        (output_dir / file_name).write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_arguments()
    tables = fetch_schema(args)

    if not tables:
        raise SystemExit(
            "No tables found. Check db name, credentials, and optional --table-prefix filter."
        )

    backend_dir = Path(__file__).resolve().parent.parent
    output_dir = (backend_dir / args.output_dir).resolve()

    write_generated_files(output_dir, tables)

    print(f"Generated backend code for {len(tables)} table(s).")
    print(f"Output directory: {output_dir}")
    print("Next: include generated_api.urls in your BackEnd/urls.py")


if __name__ == "__main__":
    main()
