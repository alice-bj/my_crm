# -*- coding:utf-8 -*-

def initial_session(user,request):

    # 方案一
    # permission = user.roles.all().values('permission__url').distinct()
    # # print(permission)
    # # 去重后的  所有权限！！ 将权限 存在 session 中！！
    # # <QuerySet [{'permission__url': '/users/'}, {'permission__url': '/users/add'}]>
    #
    # permission_list = []
    # for item in permission:
    #     permission_list.append(item['permission__url'])
    #
    # print(permission_list)  # ['/users/', '/users/add']
    #
    # # 在session中注册权限列表   用户权限
    # request.session['permission_list'] = permission_list

    # 方案二
    permission = user.roles.all().values('permission__url','permission__group_id','permission__action').distinct()

    print('permission:',permission)

    # permission: <QuerySet [
    # {'permission__url': '/users/',
    # 'permission__group_id': 1,
    # 'permission__action': 'list'},

    # {'permission__url': '/users/add/',
    # 'permission__group_id': 1,
    # 'permission__action': 'add'},

    # {'permission__url': '/users/delete/(\\d+)/',
    # 'permission__group_id': 1,
    # 'permission__action': 'delete'},

    # {'permission__url': '/users/edit/(\\d+)/',
    # 'permission__group_id': 1,
    # 'permission__action': 'edit'}]>

    # {'permission__url': 'roles/',
    # 'permission__group_id': 2,
    # 'permission__action': 'list'}]>

    # 处理数据 ： 以组为键
    """
    1:{
        "url":['/users/','/users/add','/users/delete/(\\d+)/','/users/edit/(\\d+)']
        "action":['list','add','delete','edit']
    }
    
    2：{
        "url":['/roles/']
        "action":['list']  
    }
    
    
    """

    permission_dict = {}
    for item in permission:
        gid = item.get('permission__group_id')
        url = item.get('permission__url')
        action = item.get('permission__action')

        if not gid in permission_dict.keys():
            permission_dict[gid] = {
                "urls":[url,],
                "actions":[action,]
            }

        else:
            permission_dict[gid]['urls'].append(url)
            permission_dict[gid]['actions'].append(action)

    print(permission_dict)
    """
    {1: {'urls': ['/users/', '/users/add/', '/users/delete/(\\d+)/', '/users/edit/(\\d+)/'], 
        'actions': ['list', 'add', 'delete', 'edit']}, 
    2: {'urls': ['/roles/'], 
        'actions': ['list']}}
    """

    # 注册session
    # # 在session中注册权限字典   用户权限

    request.session['permission_dict'] = permission_dict


    # 注册菜单 权限
    # permissions = user.roles.all().values('permission__url','permission__action','permission__group__title').distinct()
    permissions = user.roles.all().values('permission__url','permission__action','permission__title').distinct()
    print('------',permissions)
    """
    <QuerySet [{'permission__url': '/users/', 'permission__action': 'list'}, 
    {'permission__url': '/users/add/', 'permission__action': 'add'},
    """

    """
    <QuerySet [{'permission__url': '/users/', 'permission__action': 'list', 'permission__group__title': '用户管理'},
    {'permission__url': '/users/add/', 'permission__action': 'add', 'permission__group__title': '用户管理'}, 

    """
    """
    <QuerySet [{'permission__url': '/users/', 'permission__action': 'list', 'permission__group__title': '用户管理'},
 
    {'permission__url': '/roles/', 'permission__action': 'list', 'permission__group__title': '角色管理'},

    """

    menu_permission_list = []
    for item in permissions:
        if item['permission__action'] == 'list':
            # menu_permission_list.append((item['permission__url'],item['permission__group__title']))
            menu_permission_list.append((item['permission__url'],item['permission__title']))

    print(menu_permission_list)
    # [('/users/', '用户管理'), ('/roles/', '角色管理')]

    request.session['menu_permission_list'] = menu_permission_list