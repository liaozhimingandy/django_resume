from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin, messages
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.html import format_html

from proj_django_resume import settings
from . import models

fields_exclude = ['gmt_modified', 'gmt_created', 'updater', 'creator']


# Register your models here.
@admin.register(models.BasicInfo)
class BasicInfoModelAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'sex_display', 'phone', 'email']
    exclude = fields_exclude

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
        return models.BasicInfo.SexEnum(str(obj.sex)).label

    def save_model(self, request, obj, form, change):
        """重新保存逻辑"""
        if not {'name_cn', 'name_en', 'sex', 'phone', 'email', 'expected_position', 'avatar', 'evaluation', 'hobby',
                "user", "href"} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.name_cn}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return

        if not change:
            obj.creator = request.user
            obj.user = request.user
        obj.updater = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """重新获取数据集逻辑,比如只过来本用户下的数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_id=request.user)

    def view_on_site(self, obj):
        """设置 view_on_site 来控制是否显示 “在站点上查看” 链接。这个链接应该把你带到一个可以显示保存对象的 UR"""
        return reverse("resumes:show-resumes", kwargs={"username": obj.user.username})


@admin.register(models.Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['edu_unit', 'certificate', 'gmt_education_start', 'gmt_education_end', 'resume', 'edu_desc_display']
    exclude = fields_exclude
    ordering = ['-gmt_education_start', '-gmt_education_end']

    @admin.display(description="教育描述")
    def edu_desc_display(self, obj):
        return format_html(obj.edu_desc)

    def save_model(self, request, obj, form, change):
        if not {'edu_unit', 'certificate', 'resume', 'gmt_education', 'gmt_education_end', 'edu_desc'} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.edu_unit}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return
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
            base_info_obj = models.BasicInfo.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return qs.filter(resume=None)
        else:
            return qs.filter(resume=base_info_obj)


@admin.register(models.WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['company', 'gmt_duration_start', 'gmt_duration_end', 'work_position', 'work_desc_display', 'resume']
    exclude = fields_exclude
    ordering = ['-gmt_duration_start']

    @admin.display(description="工作内容")
    def work_desc_display(self, obj):
        return format_html(obj.work_desc)

    def save_model(self, request, obj, form, change):
        if not {'company', 'gmt_duration', 'gmt_duration_end', 'work_position', 'work_desc', 'resumes',
                'used_tech'} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.company}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return

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
            base_info_obj = models.BasicInfo.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return qs.filter(resume=None)
        else:
            return qs.filter(resume=base_info_obj)


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["id", 'skill', 'percent']
    exclude = fields_exclude
    ordering = ['-percent']
    list_editable = ['skill', 'percent']
    # 分页 - 设置每页最大显示数目
    list_per_page = 10
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if not {'skill', 'percent', 'resumes'} & set(form.changed_data):
            message = format_html(f"无需要修改的数据, <a href='{request.path}'>{obj.skill}</a>")
            messages.set_level(request, messages.WARNING)
            self.message_user(request, message, messages.WARNING)
            return

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
            base_info_obj = models.BasicInfo.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return qs.filter(resume=None)
        else:
            return qs.filter(resume=base_info_obj)

    # def get_list_display(self, request):
    #     list_display_fields = [field.name for field in self.model._meta.fields]
    #     return list(set(list_display_fields)-set(fields_exclude))


# 重新注册flatpage
admin.site.unregister(FlatPage)


@admin.register(FlatPage)
# 重新定义简单页面管理器
class FlatPageAdmin(FlatPageAdmin):
    fieldsets = [
        ("基本信息", {"fields": ["url", "title", "content", "sites"]}),
        (
            "高级管理",
            {
                "classes": ["collapse"],
                "fields": [
                    "enable_comments",
                    "registration_required",
                    "template_name",
                ],
            },
        ),
    ]
    # 覆盖原字段的组件
    formfield_overrides = {
        models.models.TextField: {"widget": CKEditorWidget},
    }
    filter_horizontal = ["sites", ]


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", 'name', 'link']
    exclude = fields_exclude


# 管理后台抬头和标题显示调整; 参考链接: file:///C:/Users/zhiming/Downloads/django-docs-4.2-zh-hans/ref/contrib/admin/index.html#django
# .contrib.admin.AdminSite
admin.site.site_header = format_html(f'后台管理(<B>{settings.__version__}|{settings.APP_COMMIT_HASH}</B>)')
admin.site.site_title = '网站管理'
# admin.site.index_title = 'app管理'
