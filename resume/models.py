import base64
import uuid
import re
from functools import cached_property

from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError

from ckeditor.fields import RichTextField
from django.urls import reverse_lazy
from django.utils.html import format_html


def validate_contact_phone(value):
    if not re.match(r"^(?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-79])|(?:5[0-35-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9["
                    r"189]))\d{8}$", value):
        raise ValidationError(f'联系方式({value})校验不通过,请重新填写!')


class Creator(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_creator",
        null=False, default='',
        verbose_name="创建人", help_text="该对象的创建人")

    class Meta:
        abstract = True


class Operator(models.Model):
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_operator",
        default='', null=False,
        verbose_name="修改人", help_text="该对象的修改人"
    )

    class Meta:
        abstract = True


class Created(models.Model):
    gmt_created = models.DateTimeField(
        auto_now=True, editable=True,
        verbose_name="创建日期", help_text="该对象的创建日期"
    )

    class Meta:
        abstract = True


class Modified(models.Model):
    gmt_modified = models.DateTimeField(
        auto_now=True, verbose_name="修改日期",
        help_text="该对象的修改日期"
    )

    class Meta:
        abstract = True
        ordering = ['-modified']


class Mark:
    @cached_property
    def get_absolute_url(self):
        opts = self._meta
        # if opts.proxy:
        #    opts = opts.concrete_model._meta
        url = reverse_lazy('resume:detail', args=[opts.model_name, self.pk])
        return url

    @cached_property
    def get_edit_url(self):
        opts = self._meta
        url = reverse_lazy('resume:update', args=[opts.model_name, self.pk])
        return url


class BasicInfoModel(Operator, Creator, Created, Modified, Mark):
    SEX = (
        (1, '男性'),
        (2, '女性'),
        (9, '其它')
    )
    user_id = models.CharField(max_length=64, default=uuid.uuid4, null=False, blank=False, verbose_name='用户id',
                               help_text='用于生成网址的唯一性,''先到先得原则, 简历预览地址为: http://127.0.0.1/resume/show/用户id/')
    name_cn = models.CharField(max_length=64, null=False, blank=False, verbose_name='姓名', help_text='您的姓名')
    name_en = models.CharField(max_length=255, default='', verbose_name='英文名称', help_text='您的英文名字(可不填)')
    sex = models.PositiveSmallIntegerField(choices=SEX, verbose_name='性别', help_text='性别')
    expected_position = models.CharField(max_length=64, null=False, blank=False, verbose_name='期望岗位',
                                         help_text='您的期望岗位')
    contact_phone = models.CharField(max_length=64, verbose_name='您的手机号码', null=True, help_text="为了方便联系到您",
                                     validators=[validate_contact_phone])
    head_sculpture = models.ImageField(verbose_name='您的头像', null=True, upload_to='static/images/%Y')
    email = models.EmailField(max_length=256, null=False, verbose_name='电子邮箱', help_text='您的电子邮箱')
    self_desc = RichTextField(null=False, blank=False, verbose_name='自我描述', help_text='填写你对自己的评价')
    hobby = RichTextField(default='', null=True, blank='', verbose_name='兴趣爱好', help_text='填写你感兴趣的方面')

    def __str__(self):
        return self.name_cn

    @cached_property
    def get_absolute_url(self):
        opts = self._meta
        # if opts.proxy:
        #    opts = opts.concrete_model._meta
        url = reverse_lazy('resume:detail', args=[opts.model_name, self.pk])
        return url

    @cached_property
    def get_edit_url(self):
        opts = self._meta
        url = reverse_lazy('resume:update', args=[opts.model_name, self.pk])
        return url

    @cached_property
    def images_head_sculpture_base64(self):
        base64Encoded = base64.b64encode(self.head_sculpture.read())
        str_base64 = f"data:;base64,{str(base64Encoded)}".replace("b'", '').replace("'", '')
        return str_base64

    class Meta:
        db_table = "basic_info"
        verbose_name = "简历基本信息"
        verbose_name_plural = verbose_name


class WorkExperienceModel(Operator, Creator, Created, Modified, Mark):
    resume_id = models.ForeignKey(BasicInfoModel, on_delete=models.CASCADE, verbose_name='简历所属人', help_text='简历所属人')
    company = models.CharField(max_length=255, null=False, blank=False, verbose_name='工作单位', help_text='您的工作单位')
    gmt_duration = models.DateField(null=False, blank=False, verbose_name='工作开始时间', help_text='工作开始时间')
    gmt_duration_end = models.DateField(null=True, blank=True, verbose_name='工作结束时间', help_text='工作结束时间')
    work_position = models.CharField(max_length=64, null=False, blank=False, verbose_name='工作岗位',
                                     help_text='工作岗位')
    work_desc = RichTextField(null=False, blank=False, verbose_name='工作内容', help_text='工作内容描述')
    used_tech = models.CharField(max_length=255, verbose_name='使用到的技术', help_text='工作中使用到的技术')

    class Meta:
        db_table = "work_experience"
        verbose_name = "工作经验信息"
        verbose_name_plural = verbose_name


class EducationModel(Operator, Creator, Created, Modified, Mark):
    resume_id = models.ForeignKey(BasicInfoModel, on_delete=models.CASCADE, verbose_name='简历所属人', help_text='简历所属人')
    edu_unit = models.CharField(max_length=255, null=False, blank=False, verbose_name='教育单位/机构', help_text='教育单位/机构')
    edu_desc = RichTextField(null=False, blank=False, verbose_name='教育描述', help_text='描述一下你的教育经历')
    certificate = models.CharField(max_length=255, verbose_name='证书', help_text='获取的证书名称')
    gmt_education = models.DateField(null=False, blank=False, verbose_name='教育开始时间', help_text='教育开始时间')
    gmt_education_end = models.DateField(null=False, blank=False, verbose_name='教育结束时间', help_text='教育结束时间')

    class Meta:
        db_table = "education"
        verbose_name = "教育信息"
        verbose_name_plural = verbose_name


class SkillModel(Operator, Creator, Created, Modified, Mark):
    resume_id = models.ForeignKey(BasicInfoModel, on_delete=models.CASCADE, verbose_name='简历所属人', help_text='简历所属人')
    skill = models.CharField(max_length=32, null=False, blank=False, verbose_name='技能', help_text='技能描述')
    skill_level = models.PositiveSmallIntegerField(verbose_name='掌握程度', help_text='技能掌握程度', validators=[
        MaxValueValidator(100),
        MinValueValidator(1)
    ])

    class Meta:
        db_table = "skill"
        verbose_name = "技能信息"
        verbose_name_plural = verbose_name
