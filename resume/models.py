import base64
import os.path
import uuid
import re
from functools import cached_property

from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError

from ckeditor.fields import RichTextField
from django.urls import reverse_lazy


def validate_contact_phone(value):
    if not re.match(r"^(?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-79])|(?:5[0-35-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9["
                    r"189]))\d{8}$", value):
        raise ValidationError(f'联系方式({value})校验不通过,请重新填写!')


class Creator(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_creator",
        null=False, verbose_name="创建人", help_text="该对象的创建人")

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
        auto_now_add=True, editable=True,
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
    class SexEnum(models.TextChoices):
        Male = 1, '男性'
        Female = 2, '女性'
        Unknown = 9, '其它'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="用户名",
                             help_text='用于生成网址的唯一性,''先到先得原则, 简历预览地址为:<B> http://127.0.0.1:8000/resume/show/</B>')
    name_cn = models.CharField('姓名', max_length=64, help_text='您的姓名')
    name_en = models.CharField('英文名称', max_length=64, default='', help_text='您的英文名字(可不填)')
    sex = models.CharField('性别', max_length=2, choices=SexEnum.choices, help_text='性别')
    expected_position = models.CharField('期望岗位', max_length=64, help_text='您的期望岗位')
    contact_phone = models.CharField('您的手机号码', max_length=64, null=True, help_text="为了方便联系到您",
                                     validators=[validate_contact_phone, ])
    head_sculpture = models.ImageField('您的头像', null=True, upload_to='images/%Y')
    email = models.EmailField('电子邮箱', max_length=256, help_text='您的电子邮箱')
    self_desc = RichTextField('自我描述', default='', help_text='填写你对自己的评价')
    hobby = RichTextField('兴趣爱好', default='', help_text='填写你感兴趣的方面')

    def __str__(self):
        return f"{self.name_cn}({self.user.username})"

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
        try:
            base64Encoded = base64.b64encode(self.head_sculpture.read())
        except FileNotFoundError:
            # 返回一个默认图片
            with open(os.path.join(settings.MEDIA_ROOT, "images/2023/Capture001.png"), 'rb') as fp:
                base64Encoded = base64.b64encode(fp.read())
        finally:
            str_base64 = f"data:;base64,{str(base64Encoded)}".replace("b'", '').replace("'", '')
            return str_base64

    class Meta:
        db_table = "basic_info"
        verbose_name = "简历基本信息"
        verbose_name_plural = verbose_name


class WorkExperienceModel(Operator, Creator, Created, Modified, Mark):
    resume = models.ForeignKey(BasicInfoModel, on_delete=models.CASCADE, verbose_name='简历所属人',
                               help_text='简历所属人')
    company = models.CharField('工作单位', max_length=255, help_text='您的工作单位')
    gmt_duration = models.DateField('工作开始时间', help_text='工作开始时间')
    gmt_duration_end = models.DateField('工作结束时间', help_text='工作结束时间')
    work_position = models.CharField('工作岗位', max_length=64, help_text='工作岗位')
    work_desc = RichTextField('工作内容', help_text='工作内容描述')
    used_tech = models.CharField('使用到的技术', max_length=255, help_text='工作中使用到的技术')

    class Meta:
        db_table = "work_experience"
        verbose_name = "工作经验信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.company


class EducationModel(Operator, Creator, Created, Modified, Mark):
    resume = models.ForeignKey(BasicInfoModel, on_delete=models.CASCADE, verbose_name='简历所属人',
                               help_text='简历所属人')
    edu_unit = models.CharField('教育单位/机构', max_length=64, help_text='教育单位/机构')
    edu_desc = RichTextField('教育描述', help_text='描述一下你的教育经历')
    certificate = models.CharField('证书', max_length=128, help_text='获取的证书名称')
    gmt_education = models.DateField('教育开始时间', help_text='教育开始时间')
    gmt_education_end = models.DateField('教育结束时间', help_text='教育结束时间')

    class Meta:
        db_table = "education"
        verbose_name = "教育信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.edu_unit


class SkillModel(Operator, Creator, Created, Modified, Mark):
    resume = models.ForeignKey(BasicInfoModel, on_delete=models.CASCADE, verbose_name='简历所属人',
                               help_text='简历所属人')
    skill = models.CharField('技能', max_length=32, help_text='技能描述')
    skill_level = models.PositiveSmallIntegerField('掌握程度', help_text='技能掌握程度', validators=[
        MaxValueValidator(100),
        MinValueValidator(1)
    ])

    class Meta:
        db_table = "skill"
        verbose_name = "技能信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.skill
