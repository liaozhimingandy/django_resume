from collections import OrderedDict
from itertools import chain

from django.contrib.auth.models import User
from django.db import models
from django.contrib.admin.utils import label_for_field, display_for_field
from django.forms import fields_for_model
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import UpdateView, DetailView, ListView
from django.views.generic.edit import CreateView
from django.apps import apps

from proj_django_resume import settings
from .models import BasicInfoModel, EducationModel, SkillModel, WorkExperienceModel
import logging

# 日志配置
logger = logging.getLogger("django.request")


# Create your views here.
def show(request, username=None):

    basic_info = get_object_or_404(BasicInfoModel, user=User.objects.get(username=username) if username else request.user)
    edu_infos = get_list_or_404(EducationModel, resume=basic_info)
    edu_infos = sorted(edu_infos, key=lambda x: x.gmt_education_end, reverse=True)

    skill_infos = get_list_or_404(SkillModel, resume=basic_info)
    skill_infos = sorted(skill_infos, key=lambda value: value.skill_level, reverse=True)

    work_experiences = get_list_or_404(WorkExperienceModel, resume=basic_info)
    work_experiences = sorted(work_experiences, key=lambda value: value.gmt_duration, reverse=True)

    list_bg_color = ['bg-success', 'bg-info', 'bg-warning', 'bg-danger', 'bg-primary', 'bg-secondary', 'bg-dark']
    list_badge_color = ['badge-info', 'badge-primary', 'badge-light', 'badge-success', 'badge-danger',
                        'badge-secondary', 'badge-warning', 'badge-dark']

    return render(request, 'resume/resume.html',
                  context={'basic_info': basic_info, 'edu_infos': edu_infos,
                           'skill_infos': skill_infos, 'list_bg_color': list_bg_color,
                           'list_badge_color': list_badge_color, 'work_experiences': work_experiences})


class IndexView(View):
    """
    首页处理逻辑
    """
    template_name = "resume/index.html"

    def get(self, request, *args, **kwargs):
        logger.info(f"{ request.get_host() }")
        user_obj = request.user
        # 判断用户是否登录
        if not user_obj.is_authenticated:
            return redirect(reverse("account:login"))

        return render(request, self.template_name, context={'user': user_obj})


class BasicInfoUpdate(UpdateView):
    template_name = 'resume/basicinfomodel/update.html'
    model = BasicInfoModel
    # fields = ['name_cn']
    fields = fields_for_model(model=model)

    # success_url = '/resume/'

    def get_success_url(self):
        pk = self.kwargs.get('pk', '')
        return reverse_lazy("resume:detail", kwargs={'model': 'BasicInfoModel', 'pk': pk})


class DetailModelView(DetailView):
    """
    获取模型详细数据通用视图,多个模型均可使用
    """
    context_object_name = 'obj'

    def get_template_names(self):
        template_name = f"resume/{self.kwargs.get('model', '')}/detail.html"
        return template_name

    def dispatch(self, request, *args, **kwargs):
        # parse param from url
        _model = self.kwargs.get('model', '')
        self.model = apps.get_model('resume', _model.lower())
        self.pk_url_kwarg = self.kwargs.get('pk', '')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.pk_url_kwarg)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _extra = {
            'obj': self.get_object(),
            'obj_as_table': self.make_info_panel,
            'model': self.kwargs.get('model', '')
        }
        context.update(**_extra)
        self.field_for_model()
        return context

    @property
    def make_info_panel(self):
        """
        动态转换字段,将字段转成html标签
        :return:
        """
        exclude = [
            'id', 'password', 'user_permissions', 'gmt_modified', 'gmt_created', 'creator', 'operator'
        ]

        base_field = self.field_for_model()
        fields = [f for f in base_field if f not in exclude]
        default_fields = getattr(self.model._meta, 'list_display', None)
        if default_fields and isinstance(default_fields, list):
            o = [f for f in fields if f not in default_fields]
            default_fields.extend(o)
            fields = default_fields
        panel = ''
        for index, field_name in enumerate(fields, 1):
            tr_format = '<tr><th>{th}</th><td>{td}</td>'
            th = label_for_field(name=field_name, model=self.model)

            field = self.model._meta.get_field(field_name)
            value = field.value_from_object(self.object)
            value_field = display_for_field(value, field, empty_value_display=False)

            tr_html = tr_format.format(th=th, td=value_field)
            panel += tr_html

        return mark_safe(panel)

    def field_for_model(self, fields=None, exclude=None):
        field_list = []
        opts = self.model._meta
        for f in chain(opts.concrete_fields, opts.many_to_many):
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            else:
                field_list.append((f.name, f))
        field_dict = OrderedDict(field_list)
        return field_dict


def make_tbody_tr(opts, obj, index, fields, extra_fields, to_field_name, *args, **kwargs):
    rowdata = ''
    detail_link = obj.get_absolute_url
    # update_link = obj.get_edit_url
    # detail_link = ''
    for field_name in fields:
        td_format = '<td class="{}">{}</td>'
        td_text = ''
        td_class = "{}".format(field_name)
        if field_name == 'field-first':
            td_text = obj.pk
            td_format = '''<td class="no-print {}">
                      <input type="checkbox" name="index" value="{}"></td>'''
        if field_name == 'field-second':
            td_text = index
            td_format = '<td class="{}">{}</td>'
        if field_name == 'field-last':
            # td_text = mark_safe(_edit + _show)
            td_format = '<td class="no-print {}">{}</td>'

        if field_name not in extra_fields:
            td_class = "field-{}".format(field_name)
            td_format = '<td class="{}">{}</td>'
            classes = 'text-info'
            field = opts.get_field(field_name)
            value = mark_safe(field.value_from_object(obj))
            td_text = display_for_field(value, field, empty_value_display=False)
            if field_name == to_field_name:
                title = "点击查看 {} 为 {} 的详情信息".format(
                    opts.verbose_name, obj
                )
                td_text = mark_safe(
                    '<a title="{}" href="{}">{}</a>'.format(
                        title, detail_link, td_text
                    )
                )

        rowdata += format_html(td_format, td_class, td_text)

    return mark_safe(rowdata)


class ListModelView(ListView):
    """
    通用list处理类
    """
    extra_fields = ['field-first', 'field-second', 'field-last']
    paginate_by = 10

    def get_query_string(self, new_params=None, remove=None):
        new_params = {} if not new_params else new_params
        remove = [] if not remove else remove
        p = self.get_params.copy()
        for r in remove:
            for k in list(p):
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        if p:
            return '?%s' % urlencode(sorted(p.items()))
        else:
            return ''

    def dispatch(self, request, *args, **kwargs):
        model = self.kwargs.get('model', '')
        self.model = apps.get_model('resume', model.lower())
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        tpl_names = "resume/{0}/list.html".format(self.kwargs.get('model', ''))
        return tpl_names

    def get_queryset(self):
        queryset = super(ListModelView, self).get_queryset()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        objs = context.get('object_list')
        _extra = {
            'thead': self.make_thead(),
            'tbody': self.make_tbody(objs),
            'paginate': self.make_paginate(objs.count()),
            'model_name': self.kwargs.get('model', '')
        }
        context.update(**_extra)
        return context

    def make_thead(self):
        fields = self.default_list_fields
        for field_name in fields:
            if field_name == 'field-first':
                yield {
                    "text": mark_safe(
                        '''<input id="action-toggle"'''
                        '''name="mode" value="page" type="checkbox">'''
                    ),
                    "field": field_name,
                    "class_attrib": mark_safe(' class="no-print field-first"'),
                    "sortable": False,
                }
                continue
            if field_name == 'field-second':
                yield {
                    "text": "#",
                    "field": False,
                    "class_attrib": mark_safe(' class="field-second"'),
                    "sortable": False,
                }
            if field_name == 'field-last':
                yield {
                    "text": "操作",
                    "field": False,
                    "class_attrib": mark_safe(' class="no-print field-last"'),
                    "sortable": False,
                }
                continue
            if field_name not in self.extra_fields:
                yield {
                    "text": label_for_field(name=field_name, model=self.model),
                    "checked": False,
                    "field": field_name,
                    "class_attrib": format_html(' class="col-{}"', field_name),
                    "sortable": False,
                }

    @property
    def model_list_display(self):
        fields = getattr(self.model._meta, 'list_display', '__all__')
        if fields and fields != '__all__':
            return fields
        return None

    @property
    def default_list_fields(self):
        exclude = ['operator', 'creator']
        base_fields = list(fields_for_model(self.model, exclude=exclude))

        extra_fields = getattr(self.model._meta, 'extra_fields', None)
        if extra_fields and isinstance(extra_fields, list):
            base_fields.extend(extra_fields)

        # 添加自定义字段
        prefix_fields = ['field-first', 'field-second']
        fields = prefix_fields + base_fields
        fields.insert(len(fields), 'field-last')

        return fields

    def make_tbody(self, objs):
        fields = self.default_list_fields
        # to_field_name = self.display_link_field
        to_field_name = self.display_link_field
        for index, obj in enumerate(objs, 1):
            yield make_tbody_tr(
                self.model._meta, obj, index, fields, self.extra_fields, to_field_name
            )

    @property
    def display_link_field(self, model=None) -> str:
        """
        的到一个链接字段
        :param model: 模型
        :return:
        """
        opts = self.model._meta
        fields = [
            f.name for f in opts.fields if (
                    isinstance(f, (models.CharField, models.GenericIPAddressField))
                    and not getattr(f, 'blank', False)
            )
        ]

        if fields:
            if 'name' in fields:
                return 'name'
            elif 'text' in fields:
                return 'text'
            elif 'title' in fields:
                return 'title'
            elif 'username' in fields:
                return 'username'
            elif 'address' in fields:
                return 'address'
            else:
                if 'created' in [f.name for f in opts.fields]:
                    return 'created'
                else:
                    return fields[0]
        else:
            if 'created' in [f.name for f in opts.get_fields()]:
                return 'created'
            else:
                return '{}'.format(opts.pk.attname)

    def make_paginate(self, max_size: int = 0):
        # request_size = int(self.paginate_by)
        request_size = 0
        if max_size <= request_size:
            return False
        else:
            min_size = 10
            max_size = max_size if max_size <= 100 else 100
            burst = len(str(max_size)) + 2
            rate = round(max_size / burst)
            ranges = [i for i in range(min_size, max_size, int(rate))]
            ranges.append(max_size)
            html = ''
            for p in ranges:
                # url = self.get_query_string({'paginate_by': p})
                url = ''
                li = '<li><a href="{}">显示{}项</a></li>'.format(url, p)
                html += li
            return mark_safe(html)


class UpdateModelView(UpdateView):
    """
    更新通用视图
    """

    def get_success_url(self):
        tpl_name = f"/resume/detail/{self.kwargs.get('model', '')}/{self.kwargs.get('pk', '')}"
        return tpl_name

    @property
    def fields(self):
        fields = fields_for_model(self.model)
        return fields

    def get_template_names(self):
        tpl_name = f"resume/{self.kwargs.get('model', '')}/update.html"
        return tpl_name

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.pk_url_kwarg)

    def dispatch(self, request, *args, **kwargs):
        # parse param from url
        _model = self.kwargs.get('model', '')
        self.model = apps.get_model('resume', _model.lower())
        self.pk_url_kwarg = self.kwargs.get('pk', '')
        return super().dispatch(request, *args, **kwargs)


class NewModelView(CreateView):
    template_name = 'resume/base/new.html'

    @property
    def fields(self):
        _model = self.kwargs.get('model', '')
        self.model = apps.get_model('resume', _model.lower())
        fields = fields_for_model(self.model)
        return fields

    def get_success_url(self):
        tpl_name = f"/resume/"
        return tpl_name
