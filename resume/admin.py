from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.html import format_html

from proj_django_resume import settings
from . import models


# Register your models here.
@admin.register(models.BasicInfoModel)
class BasicInfoModelAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'sex_display', 'contact_phone', 'email']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']

    # 搜索
    search_fields = ['name_cn']
    # 分页 - 设置每页最大显示数目
    list_per_page = 10

    def get_fields(self, request, obj=None):
        """动态根据是否为超级管理员控制编辑字段"""
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        fields.remove("user")
        return fields

    @admin.display(description="性别")
    def sex_display(self, obj):
        """显示枚举值数据"""
        return models.BasicInfoModel.SexEnum(str(obj.sex)).label

    def save_model(self, request, obj, form, change):
        """重新保存逻辑"""
        if not {'name_cn', 'name_en', 'sex', 'contact_phone', 'email', 'expected_position', 'head_sculpture',
                'self_desc', 'hobby', "user"} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.name_cn}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return
        else:
            if not change:
                obj.creator = request.user
                obj.user = request.user
            obj.operator = request.user
            super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """重新获取数据集逻辑,比如只过来本用户下的数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user)

    def view_on_site(self, obj):
        """设置 view_on_site 来控制是否显示 “在站点上查看” 链接。这个链接应该把你带到一个可以显示保存对象的 UR"""
        return reverse("resume:show-resume", kwargs={"username": obj.user.username})


@admin.register(models.SkillModel)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['skill', 'skill_level', 'resume']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']
    ordering = ['-skill_level']
    # 分页 - 设置每页最大显示数目
    list_per_page = 10
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if not {'skill', 'skill_level', 'resume'} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.skill}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return
        else:
            if not change:
                obj.creator = request.user
            obj.operator = request.user
            super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """重新获取数据集逻辑,比如只过来本用户下的数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            base_info_obj = models.BasicInfoModel.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return qs.filter(resume=None)
        else:
            return qs.filter(resume=base_info_obj)


@admin.register(models.EducationModel)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['edu_unit', 'certificate', 'gmt_education', 'gmt_education_end', 'resume', 'edu_desc_display']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']
    ordering = ['-gmt_education_end']

    @admin.display(description="教育描述")
    def edu_desc_display(self, obj):
        return format_html(obj.edu_desc)

    def save_model(self, request, obj, form, change):
        if not {'edu_unit', 'certificate', 'resume', 'gmt_education', 'gmt_education_end'} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.edu_unit}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return
        else:
            if not change:
                obj.creator = request.user
            obj.operator = request.user
            super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """重新获取数据集逻辑,比如只过来本用户下的数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            base_info_obj = models.BasicInfoModel.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return qs.filter(resume=None)
        else:
            return qs.filter(resume=base_info_obj)


@admin.register(models.WorkExperienceModel)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['company', 'gmt_duration', 'gmt_duration_end', 'work_position', 'work_desc_display', 'resume']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']
    ordering = ['-gmt_duration']

    @admin.display(description="工作内容")
    def work_desc_display(self, obj):
        return format_html(obj.work_desc)

    def save_model(self, request, obj, form, change):
        if not {'company', 'gmt_duration', 'gmt_duration_end', 'work_position', 'work_desc', 'resume', 'used_tech'} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.company}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return
        else:
            if not change:
                obj.creator = request.user
            obj.operator = request.user
            super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """重新获取数据集逻辑,比如只过来本用户下的数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            base_info_obj = models.BasicInfoModel.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return qs.filter(resume=None)
        else:
            return qs.filter(resume=base_info_obj)


# 管理后台抬头和标题显示调整; 参考链接: file:///C:/Users/zhiming/Downloads/django-docs-4.2-zh-hans/ref/contrib/admin/index.html#django
# .contrib.admin.AdminSite
admin.site.site_header = '后台管理'
admin.site.site_title = '简历'
admin.site.index_title = 'app管理'
