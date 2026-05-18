"""Unmanaged Django models mapped to the existing MySQL schema."""

from django.db import models
from django.utils import timezone


class Dict(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, null=True, blank=True)
    value = models.CharField(max_length=45, null=True, blank=True)
    type = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'dict'

    def __str__(self):
        return self.name or f'Dict-{self.pk}'


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    flag = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'role'

    def __str__(self):
        return self.name or f'Role-{self.pk}'


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    pid = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        db_column='pid',
        on_delete=models.SET_NULL,
        related_name='children',
    )
    page_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'menu'

    def __str__(self):
        return self.name or f'Menu-{self.pk}'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=45, null=True, blank=True, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    nickname = models.CharField(max_length=45, null=True, blank=True)
    email = models.CharField(max_length=45, null=True, blank=True)
    phone = models.CharField(max_length=45, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    creat_time = models.DateTimeField(null=True, blank=True, default=timezone.now)
    avatar_url = models.CharField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(
        Role,
        null=True,
        blank=True,
        db_column='role',
        on_delete=models.PROTECT,
        related_name='users',
    )

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return self.username or f'User-{self.pk}'


class File(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    is_delete = models.BooleanField(null=True, blank=True)
    enable = models.BooleanField(null=True, blank=True)
    md5 = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'file'

    def __str__(self):
        return self.name or f'File-{self.pk}'


class ImportLog(models.Model):
    id = models.AutoField(primary_key=True)
    admin_id = models.ForeignKey(
        User,
        db_column='admin_id',
        on_delete=models.CASCADE,
        related_name='import_logs',
    )
    file_name = models.CharField(max_length=100)
    import_count = models.IntegerField()
    import_status = models.CharField(max_length=20)
    error_info = models.TextField(null=True, blank=True)
    import_time = models.DateTimeField(null=True, blank=True, default=timezone.now)

    class Meta:
        managed = False
        db_table = 'import_log'

    def __str__(self):
        return self.file_name or f'ImportLog-{self.pk}'


class Track(models.Model):
    trackid = models.AutoField(primary_key=True)
    starttime = models.DateTimeField(null=True, blank=True)
    endtime = models.DateTimeField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    totalpoints = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'track'

    def __str__(self):
        return f'Track-{self.trackid}'


class Trackpoints(models.Model):
    id = models.AutoField(primary_key=True)
    trackid = models.ForeignKey(
        Track,
        db_column='trackid',
        on_delete=models.CASCADE,
        related_name='trackpoints',
    )
    gpstime = models.DateTimeField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    velocity = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)
    workstatus = models.IntegerField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    depth = models.FloatField(null=True, blank=True)
    depthstandard = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'trackpoints'

    def __str__(self):
        return f'Trackpoints-{self.pk}'


class Work(models.Model):
    trackid = models.ForeignKey(
        Track,
        db_column='trackid',
        on_delete=models.CASCADE,
        related_name='work_records',
        primary_key=True,
    )
    worktime = models.FloatField(null=True, blank=True)
    worklength = models.FloatField(null=True, blank=True)
    workarea = models.FloatField(null=True, blank=True)
    avgvelocity = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'work'

    def __str__(self):
        return f'Work-{self.trackid_id}'


class Rate(models.Model):
    trackid = models.ForeignKey(
        Track,
        db_column='trackid',
        on_delete=models.CASCADE,
        related_name='rate_records',
        primary_key=True,
    )
    passrate = models.FloatField(null=True, blank=True)
    productionrate = models.FloatField(null=True, blank=True)
    timerrate = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'rate'

    def __str__(self):
        return f'Rate-{self.trackid_id}'


class RoleMenu(models.Model):
    role_id = models.ForeignKey(
        Role,
        db_column='role_id',
        on_delete=models.CASCADE,
        related_name='role_menu_links',
        primary_key=True,
    )
    menu_id = models.ForeignKey(
        Menu,
        db_column='menu_id',
        on_delete=models.CASCADE,
        related_name='role_menu_links',
    )

    class Meta:
        managed = False
        db_table = 'role_menu'
        unique_together = (('role_id', 'menu_id'),)

    def __str__(self):
        return f'RoleMenu(role={self.role_id_id}, menu={self.menu_id_id})'
