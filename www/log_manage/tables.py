#!/usr/bin/env python3
# coding=utf8


from collections import defaultdict

from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables, columns

from risk_models.rule import Rules
from www.permissions.permission import (UserPermission, GroupPermission,
                                      UriGroupPermission)
from www.rule.forms import CONTROL_MAP


class HitLogDetailTable(tables.Table):
    time = columns.Column(verbose_name=_(u'Touch time'))
    rule_id = columns.Column(verbose_name=_(u'RuleName'), orderable=False)
    group_name = columns.Column(verbose_name=_(u'PolicyGroupNameCall'), orderable=False)
    user_id = columns.Column(verbose_name=_(u'UserID'), orderable=False)
    control = columns.Column(verbose_name=_(u'Projectmanagement'), orderable=False)
    req_body = columns.Column(verbose_name=_(u'RequestBody'), orderable=False)
    hit_number = columns.Column(verbose_name=_(u'Whether to hit for the first time'), orderable=False)

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def before_render(self, request):
        self.rules = Rules(load_all=True)

    def render_time(self, value):
        return value.strftime('%Y-%m-%d %H:%M:%S')

    def render_rule_id(self, value):
        return self.rules.get_rule_name(str(value))

    def render_control(self, value):
        return CONTROL_MAP.get(value, value)

    def render_hit_number(self, value):
        return u'-' if value == 0 else u'是' if value == 1 else u'否'

    def render_passed_users(self, value):
        return u'-' if value == 0 else value


class AuditLogTable(tables.Table):
    username = columns.Column(verbose_name=_(u"Username"), orderable=False)
    email = columns.Column(verbose_name=_(u"Mailbox"), orderable=False)
    role = columns.Column(verbose_name=_(u"Role"), empty_values=(),
                          orderable=False)
    path = columns.Column(verbose_name=_(u"Request address"), orderable=False)
    Confirm = columns.Column(verbose_name=_(u"ActionType"), empty_values=(),
                             orderable=False)
    method = columns.Column(verbose_name=_(u"How to request"), orderable=False)
    status = columns.Column(verbose_name=_(u"Response_Code"), orderable=False)
    req_body = columns.TemplateColumn("""
    <div style="max-width: 600px;">
        {% if record.req_body|length > 128 %}
            <a data-toggle="modal" data-target="#req_body_{{ record.id }}">
                View
            </a>
            <div class="modal inmodal" id="req_body_{{ record.id }}" tabindex="-1" role="dialog"  aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content animated fadeIn">
                        <div class="modal-header">
                            <h2>Request_Parameter</h2>
                        </div>
                        <div class="modal-body">
                        {{ record.req_body }}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-white" data-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        {% else %}
            {{ record.req_body }}
        {% endif %}
    </div>
    """, orderable=False, verbose_name=_(u"Request_Parameter"))
    time = columns.DateTimeColumn(verbose_name=_(u"Request time"),
                                  format="Y-m-d H:i:s")

    class Meta:
        attrs = {'class': 'table table-striped table-hover'}

    def before_render(self, request):
        pk_user_map = {}
        for d in UserPermission.objects.all_fields():
            pk = d.get('pk')
            if pk:
                pk_user_map[pk] = d
        self.pk_user_map = pk_user_map

        group_name_desc_map = {}
        for d in GroupPermission.objects.all_fields():
            name = d.get('name')
            if name:
                group_name_desc_map[name] = d.get('desc', '')
        self.group_name_desc_map = group_name_desc_map

        uri_descs_map = defaultdict(list)
        for d in UriGroupPermission.objects.all_fields():
            uris = d.get('uris', [])
            for uri in uris:
                desc = d.get('desc', '')
                uri_descs_map[uri].append(desc)

        uri_desc_map = {}
        for uri, descs in uri_descs_map.items():
            rw = None
            r = None
            for desc in descs:
                if desc.endswith(u'-Write'):
                    rw = desc
                if desc.endswith(u'-Read'):
                    r = desc
            if rw and r:
                uri_desc_map[uri] = r
            elif rw and not r:
                uri_desc_map[uri] = rw.rstrip(u'-Write') + u'-Write'
            else:
                uri_desc_map[uri] = descs[0]

        self.uri_desc_map = uri_desc_map

    def render_role(self, value, record):
        user = self.pk_user_map.get(record.email)
        if not user:
            return u'Unknown'

        if user.get('is_superuser'):
            return u'Super_Administrator'

        groups = user.get('groups', [])
        descs = [self.group_name_desc_map.get(name, '') for name in groups]
        return ', '.join(descs)

    def render_operation(self, value, record):
        return self.uri_desc_map.get(record.path, '')
