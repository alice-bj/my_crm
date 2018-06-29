from django.shortcuts import render,HttpResponse,redirect

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

            # return HttpResponse("登录成功")
            return redirect("/base/")

    return render(request,'login.html',locals())


def base(request):
    if not request.session.get("user_id"):
        return redirect('/login/')

    return render(request,'base.html')

