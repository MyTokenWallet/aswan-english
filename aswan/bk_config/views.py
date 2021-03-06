#!/usr/bin/env python3
# coding: utf-8
from django.utils.translation import gettext_lazy as _
import json
from braces.views import JSONResponseMixin
from django.views.generic import View

from aswan.core.utils import errors_to_dict
from aswan.core.generic import ListView
from aswan.core.redis_client import get_redis_client
from aswan.bk_config.forms import SourceMapForm, SourceFilterForm
from aswan.bk_config.tables import ConfigSourceTable

FIELD_EN_ZH_MAP = {
    'user_id': _('Account_ID'),
    'uid': _('Device_ID'),
    'ip': _('Current_IP'),
    'phone': _('CellPhoneNumber'),
}


class ConfigSourceListView(ListView):
    enable_page_size_config = True
    template_name = "config/source_list.html"
    table_class = ConfigSourceTable

    def get_queryset(self):
        client = get_redis_client()
        qs = client.hgetall("CONFIG_SOURCE_MAP")
        new_qs = []
        name = self.request.GET.get('name', None)
        for name_key in qs:
            item = {"name_key": name_key}
            content = json.loads(qs[name_key])
            name_show = content.pop('name_show', '')
            if name and name not in name_show:
                continue
            item['name_show'] = name_show
            item['content'] = json.dumps(content)
            new_qs.append(item)
        return new_qs

    def get_filter_form(self):
        return SourceFilterForm(data=self.request.GET)

    def get_context_data(self, **kwargs):
        context = super(ConfigSourceListView, self).get_context_data(**kwargs)
        context["create_form"] = SourceMapForm
        return context


class ConfigSourceAjaxView(JSONResponseMixin, View):
    field_en_zh_map = FIELD_EN_ZH_MAP

    def get_source_data(self):
        client = get_redis_client()
        data_list = client.hgetall("CONFIG_SOURCE_MAP")
        rs = []
        for name_key in data_list:
            item = {"name_key": name_key}
            raw_content = json.loads(data_list[name_key])
            name_show = raw_content.pop('name_show', '')
            content = []
            for en, type_ in raw_content.items():
                zh = self.field_en_zh_map.get(en, en)
                content.append({
                    'name': en,
                    'desc': en,
                    'type': type_
                })
            item['name_show'] = name_show
            item['content'] = content
            rs.append(item)
        return rs

    def get(self, request, *args, **kwargs):
        rs = self.get_source_data()
        return self.render_json_response(dict(
            state=True,
            data=rs
        ))


class ConfigDestroyView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        name_key = request.POST.get('name_key', "")
        if not name_key:
            return self.render_json_response(dict(
                state=False,
                error=_("name_key is required.")
            ))
        client = get_redis_client()
        used_keys = set()
        for key in client.scan_iter(match="freq_strategy:*"):
            source_name = client.hget(key, 'strategy_source')
            if source_name:
                used_keys.add(source_name)
        for key in client.scan_iter(match="user_strategy:*"):
            source_name = client.hget(key, 'strategy_source')
            if source_name:
                used_keys.add(source_name)

        if name_key in used_keys:
            return self.render_json_response(dict(
                state=False,
                error=_("[{}]Has been used, cannot delete").format(name_key)
            ))
        client.hdel("CONFIG_SOURCE_MAP", name_key)
        return self.render_json_response(dict(
            state=True,
            msg=_("ok")
        ))


class ConfigSourceCreateView(JSONResponseMixin, View):
    form_cls = SourceMapForm

    def post(self, request, *args, **kwargs):
        form = self.form_cls(data=request.POST, request=request)
        if form.is_valid():
            msg = form.save()
            data = dict(
                state=True,
                msg=msg
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)
