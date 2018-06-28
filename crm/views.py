from django.shortcuts import render,HttpResponse

# Create your views here.
from rbac.models import User
from rbac.service.permission import initial_session

def login(request):
    if request.method == "POST":
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")

        user = User.objects.filter(name=user,pwd=pwd).first()
        if user:
            request.session["user_id"] = user.pk
            # 注册权限到session中
            initial_session(user,request)

            return HttpResponse("登录成功")

    return render(request,'login.html',locals())


"""
引入权限组件 - rbac
    settings: 'rbac.apps.RbacConfig',
    中间件： 'rbac.service.rbac.ValidPermission',
    
员工表UserInfo和rbac.User表关联 一对一
    UserInfo中的用户名和密码也可删了，只留rbac.User中的用户名和密码。
    user = models.OneToOneField("rbac.User", null=True)
    
    makemigrations
    migrate
-------------------
rbac/stark.py 注册：
     ...

录入数据：

-------------------  
登录页面

页面继承：




"""