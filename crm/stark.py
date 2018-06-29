# -*- coding:utf-8 -*-

from .models import *
from stark.service.stark import site, ModelStark
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse, reverse, redirect, render
import datetime
from django.db.models import Q


class DepartmentConfig(ModelStark):
    list_display = ['title', 'code']


site.register(Department, DepartmentConfig)


class UserInfoConfig(ModelStark):
    list_display = ["name", 'email', 'depart']


site.register(UserInfo, UserInfoConfig)


class ClassListConfig(ModelStark):
    def display_classname(self, obj=None, header=False):
        if header:
            return "班级名称"
        return "%s(%s)" % (obj.course.name, obj.semester)

    list_display = [display_classname, 'tutor', 'teachers']


site.register(ClassList, ClassListConfig)


class CustomerConfig(ModelStark):
    def display_course(self, obj=None, header=False):
        if header:
            return "咨询课程"

        temp = []
        for course in obj.course.all():
            temp.append(
                "<a href='/stark/crm/customer/cancel_course/%s/%s' style='border:1px solid #369; padding:3px 6px;'><span>%s</span></a>&nbsp;" % (
                    obj.pk, course.pk, course.name))

        return mark_safe("".join(temp))

    def cancel_course(self, request, customer_id, course_id):
        customer_obj = Customer.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        return redirect(self.get_list_url())  # 重定向到当前表得查看页面

    def public_customer(self, request):
        # 未报名且3天未跟进或者15天未成单
        from django.db.models import Q
        import datetime
        now = datetime.datetime.now()
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=15)

        # 不应该让之前的课程顾问 再看到这个已经放到公共名单的人了
        user_id = request.session.get("user_id")
        customer_list = Customer.objects.filter(
            Q(last_consult_date__lt=now - delta_day3) | Q(recv_date__lt=now - delta_day15), status=2).exclude(
            consultant=user_id)

        return render(request, 'public.html', locals())

    def further(self, request, customer_id):
        """确认跟进"""
        user_id = request.session.get("user_id")

        now = datetime.datetime.now()
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=15)

        # 为该客户更改课程顾问 和对应得时间，
        ret = Customer.objects.filter(pk=customer_id).filter(
            Q(last_consult_date__lt=now - delta_day3) | Q(recv_date__lt=now - delta_day15), status=2).update(
            consultant=user_id, last_consult_date=now, recv_date=now
        )
        if not ret:
            return HttpResponse('已经被跟进了')

        CustomerDistrbute.objects.create(
            customer_id=customer_id, consultant_id=user_id,
            date=now, status=1,
        )
        return HttpResponse('跟进成功')

    def mycustomer(self, request):
        user_id = request.session.get("user_id")

        customer_distrubute_list = CustomerDistrbute.objects.filter(consultant_id=user_id)

        return render(request, 'mycustomer.html', locals())

    def extra_url(self):
        temp = []
        temp.append(url(r'^cancel_course/(\d+)/(\d+)', self.cancel_course))
        temp.append(url(r'^public/', self.public_customer))
        temp.append(url(r'^further/(\d+)', self.further))
        temp.append(url(r'^mycustomer/', self.mycustomer))
        return temp

    list_display = ["name", "gender", display_course, "consultant"]


site.register(Customer, CustomerConfig)


class ConsultRecordConfig(ModelStark):
    list_display = ["customer", 'consultant', 'date', 'note']


site.register(ConsultRecord, ConsultRecordConfig)

from django.http import JsonResponse


class StudentConfig(ModelStark):
    def score_view(self, request, sid):
        if request.is_ajax():
            # print(request.GET)
            cid = request.GET.get('cid')
            sid = request.GET.get('sid')

            # 跨表查
            study_record_list = StudyRecord.objects.filter(student=sid, course_record__class_obj=cid)

            data_list = []
            for study_record in study_record_list:
                day_num = study_record.course_record.day_num
                data_list.append(["day%s" % day_num, study_record.score])
                #  # [['day94', 85], ['day95', 85], ['day96', -1]]
            return JsonResponse(data_list, safe=False)

        else:
            student = Student.objects.filter(pk=sid).first()
            class_list = student.class_list.all()
            return render(request, 'score_view.html', locals())

    def extra_url(self):
        temp = []
        temp.append(url(r"^score_view/(\d+)", self.score_view))
        return temp

    def score_show(self, obj=None, header=False):
        if header:
            return "查看成绩"
        return mark_safe("<a href='score_view/%s'>查看成绩</a>" % obj.pk)

    list_display = ['customer', 'class_list', score_show]
    list_display_links = ['customer']


site.register(Student, StudentConfig)


class CourseRecordConfig(ModelStark):

    def score(self, request, course_record_id):
        if request.method == "POST":
            print('post::::', request.POST)
            """
            <QueryDict: {'csrfmiddlewaretoken': ['muIrf7pwbxIueSJcKADRlZEGVbzzRZOaiGVkBV8DGYC2V9gmxZtyZgujddFtTojk'],
            'score_33': ['100'], 'homework_note_33': ['很好'], 
            'score_34': ['85'], 'homework_note_34': ['棒'],
             'score_35': ['60'], 'homework_note_35': ['None']}>
            """
            data = {}  # data={"33":{"score":100,"homework_note":'xxx'},}
            for key, value in request.POST.items():
                if key == "csrfmiddlewaretoken": continue
                field, pk = key.rsplit('_', 1)

                if pk in data:
                    data[pk][field] = value
                else:
                    data[pk] = {field: value}

            print("data-->", data)
            """
             {'33': {'score': '90', 'homework_note': '很好'}, 
             '34': {'score': '80', 'homework_note': '帮帮哒'}, 
             '35': {'score': '50', 'homework_note': '没问题'}}

            """
            for pk, update_data in data.items():
                StudyRecord.objects.filter(pk=pk).update(**update_data)

            return redirect(request.path)

        else:
            study_record_list = StudyRecord.objects.filter(course_record__id=course_record_id)
            score_choices = StudyRecord.score_choices
            return render(request, 'score.html', locals())

    def extra_url(self):
        temp = []
        temp.append(url(r'^record_score/(\d+)', self.score))
        return temp

    def record(self, obj=None, header=False):
        if header:
            return "学习记录"
        return mark_safe("<a href='/stark/crm/studyrecord/?course_record=%s'>记录</a>" % (obj.pk))

    def record_score(self, obj=None, header=False):
        if header:
            return "录入成绩"
        return mark_safe("<a href='record_score/%s'>录入成绩</a>" % obj.pk)

    list_display = ["class_obj", 'day_num', "teacher", record, record_score]

    def patch_studyrecord(self, request, queryset):
        # print('queryset:--》',queryset)
        temp = []
        for course_record in queryset:
            # 与course_record 关联得班级对应得学生
            students_list = Student.objects.filter(class_list__id=course_record.class_obj.pk)
            for student in students_list:
                student_obj = StudyRecord(course_record=course_record, student=student)
                temp.append(student_obj)

        StudyRecord.objects.bulk_create(temp)

    actions = [patch_studyrecord]
    patch_studyrecord.short_description = "批量生成学习记录"


site.register(CourseRecord, CourseRecordConfig)


class StudyRecordConfig(ModelStark):
    list_display = ['student', 'course_record', 'record', 'score']

    def patch_late(self, request, queryset):
        queryset.update(record="late")

    patch_late.short_description = "迟到"
    actions = [patch_late]


site.register(StudyRecord, StudyRecordConfig)

site.register(Course)
site.register(School)


class CustomerDistrbuteConfig(ModelStark):
    list_display = ["customer", 'consultant', 'date', 'status']


site.register(CustomerDistrbute, CustomerDistrbuteConfig)
