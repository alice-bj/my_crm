# -*- coding:utf-8 -*-
from django.shortcuts import HttpResponse, redirect
from django.utils.deprecation import MiddlewareMixin
import re

class ValidPermission(MiddlewareMixin):

    def process_request(self, request):

        # 登录 注册 不应该 拦截 怎么办？  白名单，不需要任何权限的url

        # 当前 访问 路径
        current_path = request.path_info

        # 检查 是否属于 白名单
        valid_url_list = ["/login/", '/reg/','/base/', '/admin/.*']

        # if current_path in valid_url_list:
        #     return

        for valid_url in valid_url_list:
            ret = re.match(valid_url,current_path)
            if ret:
                return

        # 校验 是否 登录
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/login/')


        # # 校验权限 1  permission_list
        # permission_list = request.session.get('permission_list', [])
        #
        # flag = False
        # for permission in permission_list:
        #     permission = "^%s$" % permission
        #     ret = re.match(permission, current_path)  # 用正则， 注意^ $
        #     if ret:
        #         flag = True
        #         break
        #
        # if not flag:
        #     return HttpResponse('无访问权限!')

        # 校验权限 2 permission_dict
        permission_dict = request.session.get('permission_dict')
        for item in permission_dict.values():
            urls = item['urls']
            for reg in urls:
                reg = "^%s$"%reg
                ret = re.match(reg,current_path)
                if ret:
                    print("action",item['actions'])

                    # 注意：妙 ！！
                    request.actions = item["actions"]

                    return

        return HttpResponse('无权访问')



"""
permission_dict:

{1: {'urls': ['/users/', '/users/add/', '/users/delete/(\\d+)/', '/users/edit/(\\d+)/'], 
    'actions': ['list', 'add', 'delete', 'edit']}, 
2: {'urls': ['/roles/'], 
    'actions': ['list']}}
    
"""