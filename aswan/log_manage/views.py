#!/usr/bin/env python3
# coding: utf-8

from django.utils.translation import gettext_lazy as _
import logging
from datetime import timedelta

from braces.views import JSONResponseMixin
from django.db import connection

from aswan.log_manage.models import AuditLogModel, get_hit_log_model
from risk_models.rule import Rules
from aswan.core.generic import ListView
from django.views.generic import View
from aswan.log_manage.tables import HitLogDetailTable, AuditLogTable
from aswan.log_manage.forms import HitLogDetailFilterForm, AuditLogForm

logger = logging.getLogger(__name__)


class HitListDetailView(ListView):
    template_name = "log_manage/hit_list_detail.html"
    filter_form = HitLogDetailFilterForm
    table_class = HitLogDetailTable
    enable_page_size_config = True

    @staticmethod
    def get_hit_table_names(query):
        prefix = "hit_log"
        start = query['start_day']
        end = query['end_day']

        with connection.cursor() as cursor:  # Determine if a data table exists
            all_table_names = set(
                connection.introspection.table_names(cursor=cursor))
        table_names = []
        while start <= end:
            table_name = "{}_{}".format(prefix, start.strftime("%Y%m%d"))
            if table_name in all_table_names:
                table_names.append(table_name)
            start += timedelta(days=1)
        return table_names

    @staticmethod
    def get_query_params(query):

        query_params = {
            'time__gte': query['start_day'],
            'time__lte': query['end_day'],
        }
        user_id = query.get('user_id', '')
        if user_id:
            query_params['user_id'] = user_id

        rule_id = query.get('rule_id')
        if rule_id:
            query_params['rule_id'] = rule_id

        strategy_group = query.get('strategy_group')
        if strategy_group:
            query_params['group_uuid'] = strategy_group

        control = query.get('control', _('All'))
        if control and control != _('All'):
            query_params['control'] = control
        return query_params

    def get_queryset(self):
        form = self.filter_form(data=self.request.GET)

        if not form.is_valid():
            return []

        select_fields = ('time', 'rule_id', 'group_name', 'req_body',
                         'user_id', 'control', 'hit_number')

        query_params = self.get_query_params(form.cleaned_data)
        table_names = self.get_hit_table_names(form.cleaned_data)

        # todo The paging here doesn't do very well, optimize it.
        qs = []
        for model_cls in (get_hit_log_model(table_name) for table_name in
                          table_names):
            qs.extend(model_cls.objects.filter(**query_params).order_by(
                '-time').values(*select_fields))
        return sorted(qs, key=lambda d: d['time'], reverse=True)

    def get_filter_form(self):
        return self.filter_form(initial=self.request.GET)


class RuleStrategyMapView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        rule_id = request.GET.get('rule_id', None)
        groups = {}

        # Argument incomplete
        if rule_id is None:
            return self.render_json_response({
                'state': False,
                "rules_num": 0
            })

        rules = Rules(load_all=True).id_rule_map
        if rule_id in ("", _("All")):  # All_Rules
            return self.render_json_response({
                'state': True,
                'strategy_groups': groups,
                "rules_num": len(rules.keys())
            })

        rule_obj = rules.get(rule_id)
        if not rule_obj:
            return self.render_json_response({
                'state': False,
                "rules_num": 0
            })

        group_list = rule_obj.strategy_group_list

        for strategy_group in group_list:
            group_name = strategy_group[3]
            groups[rule_id] = group_name
            break

        return self.render_json_response({
            'state': True,
            'strategy_groups': groups,
            "rules_num": len(rules.keys())
        })


class AuditLogListView(ListView):
    enable_page_size_config = True
    template_name = "log_manage/access_audit.html"
    table_class = AuditLogTable
    form_class = AuditLogForm

    def get_queryset(self):
        form = self.form_class(data=self.request.GET)
        query = {}
        if form.is_valid():
            cd = form.cleaned_data
            query = {k: cd[k] for k in cd if cd[k]}
        qs = AuditLogModel.objects.filter(**query)
        return qs

    def get_filter_form(self):
        return self.form_class(data=self.request.GET)
