#!/usr/bin/env python3
# coding: utf-8
import json

from django.utils.translation import gettext_lazy as _
from django_tables2 import tables, columns

from www.strategy.forms import (OP_MAP, FUNC_MAP, VAR_MAP, DIM_MAP_MENU,
                              TYPE_MAP_MENU, OP_MAP_MENU)
from www.core.pymongo_client import get_mongo_client
from www.core.redis_client import get_redis_client


class BoolStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_("PolicyName"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_("PolicyDescription"), orderable=False)
    strategy_var = columns.Column(verbose_name=_("Built-in variables"), orderable=False)
    strategy_op = columns.Column(verbose_name=_("ActionCode"), orderable=False)
    strategy_func = columns.Column(verbose_name=_("Built-in functions"), orderable=False)
    strategy_threshold = columns.Column(verbose_name=_("Thresholds"), orderable=False)
    action = columns.TemplateColumn("""
    <a class="strategy-destroy" data-uri="{% url 'strategy:bool_strategy_destroy' %}" data-id="{{ record.uuid }}">delete</a>
    """, orderable=False, verbose_name=_("Confirm"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_strategy_var(self, value):
        name = VAR_MAP.get(value, "")
        if name:
            return u"{0}({1})".format(name, value)
        return value

    def render_strategy_op(self, value):
        name = OP_MAP.get(value, "")
        if name:
            return u"{0}({1})".format(name, value)
        return value

    def render_strategy_func(self, value):
        name = FUNC_MAP.get(value, "")
        if name:
            return u"{0}({1})".format(name, value)
        return value


class FreqStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_("PolicyName"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_("PolicyDescription"), orderable=False)
    strategy_source = columns.Column(verbose_name=_("DataSources"), orderable=False)
    strategy_body = columns.Column(verbose_name=_("BodyName"), orderable=False)
    strategy_time = columns.Column(verbose_name=_("Period (in seconds))"), orderable=False)
    strategy_limit = columns.Column(verbose_name=_("Maximum"), orderable=False)

    action = columns.TemplateColumn("""
    <a class="strategy-destroy" data-uri="{% url 'strategy:freq_strategy_destroy' %}" data-id="{{ record.uuid }}">delete</a>
    """, orderable=False, verbose_name=_("Confirm"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_strategy_source(self, value):
        client = get_redis_client()
        data = client.hget("CONFIG_SOURCE_MAP", value)
        if data:
            try:
                name = json.loads(data).get('name_show', '')
            except ValueError:
                return value
            if name:
                return u"{0}({1})".format(name, value)
        return value


class MenuStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_("PolicyName"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_("PolicyDescription"), orderable=False)
    dimension = columns.Column(verbose_name=_("Dimensions"), orderable=False)
    menu_op = columns.Column(verbose_name=_("ActionCode"), orderable=False)
    event = columns.Column(verbose_name=_("Project"), orderable=False)
    menu_type = columns.Column(verbose_name=_("ListType"), orderable=False)
    action = columns.TemplateColumn("""
    <a class="strategy-destroy" data-uri="{% url 'strategy:menu_strategy_destroy' %}" data-id="{{ record.uuid }}">delete</a>
    """, orderable=False, verbose_name=_("Confirm"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_menu_type(self, value):
        return TYPE_MAP_MENU.get(value, value)

    def render_menu_op(self, value):
        return OP_MAP_MENU.get(value, value)

    def render_dimension(self, value):
        return DIM_MAP_MENU.get(value, value)

    def render_event(self, value):
        db = get_mongo_client()
        res = db['menu_event'].find_one({'event_code': value}) or {}
        return res.get('event_name', value)


class UserStrategyTable(tables.Table):
    strategy_name = columns.Column(verbose_name=_("PolicyName"), orderable=False)
    strategy_desc = columns.Column(verbose_name=_("PolicyDescription"), orderable=False)
    strategy_source = columns.Column(verbose_name=_("DataSources"), orderable=False)
    strategy_body = columns.Column(verbose_name=_("BodyName"), orderable=False)
    strategy_day = columns.Column(verbose_name=_("Nature Day (In Individual)"), orderable=False)
    strategy_limit = columns.Column(verbose_name=_("Maximum"), orderable=False)

    action = columns.TemplateColumn("""
        <a class="strategy-destroy" data-uri="{% url 'strategy:user_strategy_destroy' %}" data-id="{{ record.uuid }}">delete</a>
        """, orderable=False, verbose_name=_("Confirm"))

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def render_strategy_source(self, value):
        client = get_redis_client()
        data = client.hget("CONFIG_SOURCE_MAP", value)
        if data:
            try:
                name = json.loads(data).get('name_show', '')
            except ValueError:
                return value
            if name:
                return u"{0}({1})".format(name, value)
        return value
