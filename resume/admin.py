from django.contrib import admin
from django.apps import apps

from . import models


def save_model(request, obj, form, change):
    # 设置设置字段
    if not obj.creator_id:
        obj.creator_id = request.user.id
        obj.operator_id = request.user.id
    if not change:
        obj.operator_id = request.user.id


# Register your models here.
@admin.register(models.BasicInfoModel)
class BasicInfoModelAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'sex', 'contact_phone', 'email']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']
    # 搜索
    search_fields = ['name_cn']
    # 分页 - 设置每页最大显示数目
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        save_model(request, obj, form, change)
        super().save_model(request, obj, form, change)


@admin.register(models.SkillModel)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['skill', 'skill_level', 'resume_id']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']
    ordering = ['-skill_level']
    # 分页 - 设置每页最大显示数目
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        save_model(request, obj, form, change)
        super().save_model(request, obj, form, change)


@admin.register(models.EducationModel)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['edu_unit', 'certificate', 'gmt_education', 'gmt_education_end', 'resume_id']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']
    ordering = ['-gmt_education_end']

    def save_model(self, request, obj, form, change):
        save_model(request, obj, form, change)
        super().save_model(request, obj, form, change)


@admin.register(models.WorkExperienceModel)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['company', 'gmt_duration', 'gmt_duration_end', 'work_position', 'work_desc', 'resume_id']
    exclude = ['gmt_modified', 'gmt_created', 'operator', 'creator']
    ordering = ['-gmt_duration']

    def save_model(self, request, obj, form, change):
        # 设置设置字段
        save_model(request, obj, form, change)
        super().save_model(request, obj, form, change)


# 管理后台抬头和标题显示调整
admin.site.site_header = '简历后台管理'
admin.site.site_title = '简历'
