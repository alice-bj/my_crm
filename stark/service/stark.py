# -*- coding:utf-8 -*-
# from django.urls import path,re_path,reverse
from django.urls import reverse
from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from stark.utils.page import Pagination
from django.db.models import Q
from django.db.models.fields.related import ManyToManyField

class ShowList(object):
    def __init__(self,config,data_list,request):
        self.config = config
        self.data_list = data_list
        self.request = request

        #分页
        data_count = self.data_list.count()
        current_page = self.request.GET.get('page',1)
        base_path = self.request.path

        self.pagination = Pagination(current_page,data_count,base_path,self.request.GET,per_page_num=10, pager_count=11)
        self.page_data = self.data_list[self.pagination.start:self.pagination.end]

        # action
        # self.actions = self.config.actions
        self.actions = self.config.new_actions()


    def get_filter_linktags(self):
        print('list_filter',self.config.list_filter)

        link_list = {}  # str 拿 字段对象 ['publish', 'authors']

        link_dic = {}

        import copy
        print('get:-----',self.request.GET)
        # params = copy.deepcopy(self.request.GET)
        # print('params:------',params)
        # params["alice"] = "1"
        # print(params)
        # print('urlencode:',params.urlencode()) # publish=1&author=5&alice=1
        # <QueryDict: {'publish': ['1'], 'author': ['5']}>
        for filter_field in self.config.list_filter:
            params = copy.deepcopy(self.request.GET)

            cid = self.request.GET.get(filter_field,0)

            print(filter_field)
            filter_field_obj = self.config.model._meta.get_field(filter_field)
            print(filter_field_obj)
            print(type(filter_field_obj))

            from django.db.models.fields.related import ForeignKey
            from django.db.models.fields.related import ManyToManyField

            # 拿到关联得得字段对象，如何去数据
            # print("rel...", filter_field_obj.rel.to.objects.all())
            # rel... < QuerySet[ < Publish: 苹果出版社 >, < Publish: 香蕉出版社 >] >
            # rel... <QuerySet [<Author: alex>, <Author: egon>]>

            if isinstance(filter_field_obj,ForeignKey) or isinstance(filter_field_obj,ManyToManyField):
                data_list = filter_field_obj.rel.to.objects.all()  # 关联对象 适用 一对多，多对多

            else: # 普通字段
                data_list =  self.config.model.objects.all().values('pk',filter_field)

            temp = []
            # 处理全部标签
            if params.get(filter_field):
                del params[filter_field]
                temp.append('<a href="?%s">全部</a>'%(params.urlencode()))
            else:
                temp.append('<a href="#" class="active">全部</a>' )

            # 处理数据标签
            for obj in data_list:
                if isinstance(filter_field_obj,ForeignKey) or isinstance(filter_field_obj,ManyToManyField):
                    pk = obj.pk
                    text = str(obj)
                    params[filter_field] = pk
                else:
                    # data_list = ["pk":1,"title":'go']
                    pk = obj.get('pk')
                    text = obj.get(filter_field)
                    params[filter_field] = text

                _url = params.urlencode()  # 序列化后得结构

                if cid == str(pk) or cid == text:
                    link_tag = '<a class="active" href="?%s">%s</a>'%(_url,text)
                else:
                    link_tag = '<a href="?%s">%s</a>' % (_url,text)
                temp.append(link_tag)

            link_dic[filter_field] = temp

        return link_dic


    def get_action_list(self):
        temp = []
        for action in self.actions:
            temp.append({
                "name":action.__name__,
                "desc":action.short_description
            })  # [{'name':'patch_init','desc':'xxx'}]

        return temp

    def get_header(self):
        # 构建表头
        header_list = []
        print('header', self.config.new_list_play())

        for field in self.config.new_list_play():  # 如何取中文
            if callable(field):
                val = field(self.config, header=True)
                header_list.append(val)
            else:
                if field == '__str__':
                    header_list.append(self.config.model._meta.model_name.upper())
                else:
                    val = self.config.model._meta.get_field(field).verbose_name
                    header_list.append(val)

        return header_list

    def get_body(self):
        # 构建表单
        new_data_list = []
        for obj in self.page_data:

            temp = []
            for field in self.config.new_list_play():
                if callable(field):
                    val = field(self.config, obj)
                else:

                    try:
                        from django.db.models.fields.related import ManyToManyField

                        field_obj = self.config.model._meta.get_field(field)
                        # 多对多
                        if isinstance(field_obj,ManyToManyField):
                            # val = getattr(obj, field+".all()")  # 多对多 不能这样写！！
                            ret = getattr(obj, field).all()  # 多对多
                            t = []
                            for mobj in ret:
                                t.append(str(mobj))
                            val = ",".join(t)

                        else:
                            if field_obj.choices:
                                val = getattr(obj,"get_"+field+"_display")
                            else:
                                val = getattr(obj, field)

                            if field in self.config.list_display_links:  # 重复代码 ？？？

                                _url = self.config.get_change_url(obj)
                                val = mark_safe('<a href="%s">%s</a>' % (_url, val))

                    except Exception as e:
                        val = getattr(obj,field)


                temp.append(val)
            new_data_list.append(temp)

        return new_data_list


class ModelStark(object):
    # list_display = []
    list_display = ["__str__"]
    list_display_links = []
    modelform_class = []
    search_fields = []
    actions = []
    list_filter = []

    def __init__(self,model,site):
        self.model = model
        self.site = site

    def patch_delete(self,request,queryset):
        queryset.delete()
    patch_delete.short_description = '批量删除'


    # 删除 编辑 复选框
    def checkbox(self,obj=None,header=False):
        if header:
            return mark_safe('<input id="choice" type="checkbox">')

        return mark_safe('<input class="choice_item" type="checkbox" name="selected_pk" value="%s">'%obj.pk)

    def edit(self, obj=None, header = False):
        if header:
            return "操作"

        _url = self.get_change_url(obj)

        return mark_safe("<a href='%s'>编辑</a>" % _url)

    def deletes(self, obj=None,header=False):
        if header:
            return "操作"

        _url = self.get_delete_url(obj)

        return mark_safe("<a href='%s'>删除</a>" % _url)

    def get_modelform_class(self):
        if not self.modelform_class:
            from django.forms import ModelForm
            from django.forms import widgets as wid
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"

            return ModelFormDemo
        else:
            return self.modelform_class

    def add_view(self,request):
        # modelform
        ModelFormDemo = self.get_modelform_class()
        form = ModelFormDemo()

        for bfield in form:
            from django.forms.boundfield import BoundField
            print('i::',type(bfield)) # 字段类型
            print('i::',bfield.field)  # 字段对象
            print('name', bfield.name)  # 字段名字符串
            # i:: <class 'django.forms.boundfield.BoundField'>
            #i:: <django.forms.fields.CharField object at 0x0000019CC77259E8>
            # i:: <class 'django.forms.boundfield.BoundField'>
            #i:: <django.forms.models.ModelChoiceField object at 0x0000019CC7725B38>
            #i:: <class 'django.forms.boundfield.BoundField'>
            #i:: <django.forms.models.ModelMultipleChoiceField object at 0x0000019CC7725BA8>

            from django.forms.models import ModelChoiceField
            if isinstance(bfield.field,ModelChoiceField):
                bfield.is_pop = True
                print("model:",bfield.field.queryset.model)
                # 一对 多，或多对多得 关联 模型表
                # <class 'app01.models.Publish'>
                # model: <class 'app01.models.Author'>
                related_model_name = bfield.field.queryset.model._meta.model_name
                related_app_label = bfield.field.queryset.model._meta.app_label
                _url= reverse("%s_%s_add"%(related_app_label,related_model_name))
                bfield.url = _url+"?pop_res_id=id_%s"%bfield.name

        if request.method == 'POST':
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                obj = form.save()

                # 两种情况 分
                pop_res_id = request.GET.get("pop_res_id")
                if pop_res_id:
                    res = {"pk":obj.pk,"text":str(obj),"pop_res_id":pop_res_id}
                    import json
                    return render(request,'pop.html',{"res":res})
                else:
                    return redirect(self.get_list_url())

        return render(request,'add_view.html',locals())


    def delete_view(self,request,del_id):
        url = self.get_list_url()
        print("-------------------",del_id,type(del_id))
        if isinstance(del_id,str):
            del_id = [del_id,]
        if request.method == 'POST':
            # self.model.objects.filter(pk=del_id).delete()
            self.model.objects.filter(pk__in=del_id).delete()
            return redirect(url)

        return render(request,'delete_view.html',locals())


    def change_view(self,request,change_id):
        ModelFormDemo = self.get_modelform_class()
        edit_obj = self.model.objects.filter(pk=change_id).first()
        form = ModelFormDemo(instance=edit_obj)

        if request.method == 'POST':
            form = ModelFormDemo(request.POST,instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())

        return render(request,'change_view.html',locals())


    def new_list_play(self):
        temp = []
        temp.append(ModelStark.checkbox)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.deletes)

        print('temp',temp)
        return temp

    def new_actions(self):

        temp = []
        temp.append(ModelStark.patch_delete)
        temp.extend(self.actions)

        return temp


    def get_change_url(self,obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))

        return _url

    def get_delete_url(self,obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_delete" % (app_label, model_name), args=(obj.pk,))

        return _url

    def get_add_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_add"%(app_label,model_name))

        return _url

    def get_list_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_list"%(app_label,model_name))

        return _url

    def get_search_condition(self,request):
        key_words = request.GET.get('q',"")
        self.key_words = key_words
        from django.db.models import Q  # Q查询得两种方法，一种可以放str,
        # data_list = self.model.objects.all()  # [obj,obj,obj。。。]
        # self.search_fields   ['title','price']
        search_connection = Q()
        if key_words:
            search_connection.connector = 'or'
            for search_field in self.search_fields:  # 一种可以放str, 模糊查询
                search_connection.children.append((search_field + "__contains", key_words))

        return search_connection

    def get_filter_condition(self,request):
        filter_condition = Q()
        for filter_field, val in request.GET.items():
            # if filter_field in self.list_filter:
            if filter_field !="page":
                filter_condition.children.append((filter_field, val))

        return filter_condition

    def list_view(self,request):

        if request.method == 'POST':
            print(request.POST)
            action = request.POST.get('action')
            selected_pk = request.POST.getlist('selected_pk')
            print('*'*120)
            print(selected_pk)
            action_func = getattr(self,action)  # 反射
            queryset = self.model.objects.filter(pk__in=selected_pk) # 这也太妙了吧！！
            action_func(request, queryset)
            # ret = action_func(request,queryset)

            # return ret

        # print('model:----',self.model)
        """
        <class 'app01.models.UserInfo'>
        <class 'app01.models.Book'>
        """

        # ['name', 'age']   ['']  分情况，配置类对象的list_display ,

        print('list_display:', self.list_display)

        # 获取search得Q对象
        search_connection = self.get_search_condition(request)

        #获取filter得Q对象
        filter_condition = self.get_filter_condition(request)

        # 筛选获取当前表所有数据
        data_list = self.model.objects.all().filter(search_connection).filter(filter_condition)

        # 按这个showlist展示页面
        showlist = ShowList(self,data_list,request)

        # 构建一个查看得url
        add_url = self.get_add_url()
        return render(request,'list_view.html',locals())

    def extra_url(self):
        return []

    def get_urls2(self):
        temp = []

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        temp.append(url(r'add/',self.add_view,name="%s_%s_add"%(app_label,model_name)))
        temp.append(url(r'(\d+)/delete',self.delete_view,name = '%s_%s_delete'%(app_label,model_name)))
        temp.append(url(r'(\d+)/change',self.change_view,name='%s_%s_change'%(app_label,model_name)))
        temp.append(url(r'^$',self.list_view,name='%s_%s_list'%(app_label,model_name)))

        temp.extend(self.extra_url())
        
        return temp

    @property
    def urls2(self):

        return self.get_urls2(),None,None


class StarkSite(object):
    def __init__(self):
        self._registry = {}

    def register(self,model,stark_class=None):
        if not stark_class:
            stark_class = ModelStark

        self._registry[model] = stark_class(model,self)


    def get_urls(self):
        temp = []

        # 模型表 配置类对象
        for model, stark_class_obj in self._registry.items():
            model_name = model._meta.model_name
            app_lable = model._meta.app_label

            # 分发增删改查
            temp.append(url(r'%s/%s/'%(app_lable,model_name),stark_class_obj.urls2))

        return temp

    @property
    def urls(self):
        print('---------')
        return self.get_urls(), None,None


site = StarkSite()
