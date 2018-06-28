# -*- coding:utf-8 -*-

from django import template
register = template.Library()



@register.inclusion_tag('rbac/menu.html')
def get_menu(request):
    # 获取当前 用户 应该放到 菜单栏的 权限
    menu_permission_list = request.session.get('menu_permission_list')

    return {'menu_permission_list':menu_permission_list}
