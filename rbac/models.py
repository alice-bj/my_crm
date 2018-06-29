from django.db import models


# Create your models here.

class User(models.Model):
    """用户表"""
    name = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    roles = models.ManyToManyField(to='Role')

    def __str__(self):
        return self.name


class Role(models.Model):
    """角色表"""
    title = models.CharField(max_length=32)
    permission = models.ManyToManyField(to='Permission')

    def __str__(self):
        return self.title


class Permission(models.Model):
    """权限表"""
    title = models.CharField(max_length=32)
    url = models.CharField(max_length=64)

    action = models.CharField(max_length=32, default="")

    group = models.ForeignKey('PermissionGroup', default=1, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class PermissionGroup(models.Model):
    """权限分组表"""
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title
