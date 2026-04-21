"""Auto-generated Django models."""

from django.db import models

class Dict(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, null=True, blank=True)
    value = models.CharField(max_length=45, null=True, blank=True)
    type = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'dict'

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'

class File(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True, default='文件名称')
    type = models.CharField(max_length=255, null=True, blank=True, default='文件类型')
    size = models.BigIntegerField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True, default='文件地址')
    is_delete = models.BooleanField(null=True, blank=True)
    enable = models.BooleanField(null=True, blank=True)
    md5 = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'file'

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'

class ImportLog(models.Model):
    """Excel数据导入日志表，记录管理员导入操作详情"""
    id = models.AutoField(primary_key=True, help_text='日志唯一ID，自增')
    admin_id = models.IntegerField(help_text='执行导入操作的管理员ID，关联user_info表id')
    file_name = models.CharField(max_length=100, help_text='导入的Excel文件名')
    import_count = models.IntegerField(help_text='本次导入的数据条数')
    import_status = models.CharField(max_length=20, help_text='导入状态：success（成功）、fail（失败）')
    error_info = models.TextField(null=True, blank=True, help_text='导入失败时的错误信息，可选')
    import_time = models.DateTimeField(null=True, blank=True, default='CURRENT_TIMESTAMP', help_text='导入操作时间')

    class Meta:
        managed = False
        db_table = 'import_log'

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'

class MachineryTrack(models.Model):
    """农机作业轨迹数据表，存储所有导入的Excel轨迹数据"""
    id = models.BigAutoField(primary_key=True, help_text='轨迹记录唯一ID，自增')
    plot_no = models.CharField(max_length=50, help_text='地块编号，用于轨迹查询、数据删除，唯一标识作业地块')
    gnss_time = models.DateTimeField(help_text='GNSS定位时间，精确到秒级')
    longitude = models.DecimalField(max_digits=12, decimal_places=6, help_text='经度，保留6位小数')
    latitude = models.DecimalField(max_digits=11, decimal_places=6, help_text='纬度，保留6位小数')
    speed = models.DecimalField(max_digits=8, decimal_places=2, help_text='农机行驶速度，保留2位小数')
    course = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default='0.00', help_text='航向角，保留2位小数，可选字段')
    work_status = models.CharField(max_length=20, help_text='工作状态（如：作业中、空闲、停止）')
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default='0.00', help_text='作业幅宽，保留2位小数')
    plowing_depth = models.DecimalField(max_digits=8, decimal_places=2, help_text='耕整深度，保留2位小数')
    standard_depth = models.DecimalField(max_digits=8, decimal_places=2, help_text='深度标准值，保留2位小数，用于计算达标率')
    import_time = models.DateTimeField(null=True, blank=True, default='CURRENT_TIMESTAMP', help_text='数据导入时间')

    class Meta:
        managed = False
        db_table = 'machinery_track'

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'

class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    page_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'menu'

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, null=True, blank=True, default='名称')
    description = models.CharField(max_length=255, null=True, blank=True, default='描述')
    flag = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'role'

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'

class RoleMenu(models.Model):
    role_id = models.IntegerField(primary_key=True)
    menu_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'role_menu'
        unique_together = (('role_id', 'menu_id'),)

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=45, null=True, blank=True, default='用户名')
    password = models.CharField(max_length=45, null=True, blank=True, default='密码')
    nickname = models.CharField(max_length=45, null=True, blank=True, default='昵称')
    email = models.CharField(max_length=45, null=True, blank=True, default='邮箱')
    phone = models.CharField(max_length=45, null=True, blank=True, default='电话')
    address = models.CharField(max_length=255, null=True, blank=True, default='地址')
    creat_time = models.DateTimeField(null=True, blank=True, default='CURRENT_TIMESTAMP')
    avatar_url = models.CharField(max_length=255, null=True, blank=True, default='URL')
    role = models.CharField(max_length=45, null=True, blank=True, default='角色')

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return f'{self.__class__.__name__}(pk={self.pk})'
