#!/usr/bin/env python3
# coding: utf-8

"""
    This script is used to pre-note data when User is unfamiliar
"""
import logging
import hashlib

from django.core.management.base import BaseCommand

from aswan.permissions.init_data import create_user
from aswan.menu.init_data import create_menu_event, add_element_to_menu
from aswan.bk_config.init_data import create_data_source
from aswan.strategy.init_data import (create_menu_strategy, create_bool_strategy, create_freq_strategy,
                                      create_user_strategy)
from aswan.rule.init_data import create_rule

logger = logging.getLogger(__name__)
logging.basicConfig()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create a normal User
        create_user(email='momo_init@immomo.com', username='momo_init',
                    password='momo_init', is_superuser=True)

        # Create a list
        event_code = 'init_event'
        create_menu_event(event_code=event_code, event_name="InitialProject")
        add_element_to_menu(event_code, menu_type='black', dimension='user_id',
                            element='111111')
        add_element_to_menu(event_code, menu_type='white', dimension='uid',
                            element=hashlib.md5('white_uid'.encode()).hexdigest())
        add_element_to_menu(event_code, menu_type='gray', dimension='ip',
                            element='1.1.1.1')
        add_element_to_menu(event_code, menu_type='black', dimension='phone',
                            element=hashlib.md5('12345678901'.encode()).hexdigest())
        add_element_to_menu(event_code, menu_type='black', dimension='pay',
                            element=hashlib.md5('pay_account'.encode()).hexdigest())

        # Create a policy
        # List strategy
        menu_strategy_name_1 = 'User on the User blacklist for the initial project'
        menu_uuid_1 = create_menu_strategy(event_code, dimension='user_id',
                                           menu_type='black', menu_op='is',
                                           strategy_name=menu_strategy_name_1,
                                           strategy_desc='Initial blacklist policy')
        menu_strategy_name_2 = 'uid on the initial project'

        menu_uuid_2 = create_menu_strategy(event_code, dimension='uid',
                                           menu_type='white', menu_op='is',
                                           strategy_name=menu_strategy_name_2,
                                           strategy_desc='Initial whitelisting strategy')
        menu_strategy_name_3 = 'IP on the IP Gray List for The Initial Project'
        menu_uuid_3 = create_menu_strategy(event_code, dimension='ip',
                                           menu_type='gray', menu_op='is',
                                           strategy_name=menu_strategy_name_3,
                                           strategy_desc='Initial Gray List Strategy')

        # Bool Strategy
        bool_strategy_name_1 = 'User is an exception To User'
        bool_uuid_1 = create_bool_strategy(strategy_var="user_id",
                                           strategy_op="is",
                                           strategy_func="is_abnormal",
                                           strategy_threshold="",
                                           strategy_name=bool_strategy_name_1,
                                           strategy_desc=bool_strategy_name_1)
        bool_strategy_name_2 = "User logins greater than 50"
        bool_uuid_2 = create_bool_strategy(strategy_var='user_id',
                                           strategy_op='gt',
                                           strategy_func="user_login_count",
                                           strategy_threshold="50",
                                           strategy_name=bool_strategy_name_2,
                                           strategy_desc=bool_strategy_name_2)
        # Data source-related policies
        # Create a data source
        source_key = "init_source_key"
        create_data_source(source_key=source_key, source_name="Initial_Sample_Data_Source",
                           fields=["user_id", "uid", "ip", "phone"])

        # Time-time frequency control strategy
        freq_strategy_name = "Same uid, 10 times in 24 hours(Initial sample data source)"
        freq_uuid = create_freq_strategy(strategy_source=source_key,
                                         strategy_body='uid',
                                         strategy_time=24 * 3600,
                                         strategy_limit=10,
                                         strategy_name=freq_strategy_name,
                                         strategy_desc='Initial time period frequency control strategy')

        # User-limited number-based policy
        user_strategy_name = '10 User are for the same device on the same day (Initial sample source)'
        user_uuid = create_user_strategy(strategy_source=source_key,
                                         strategy_body='uid',
                                         strategy_day=1, strategy_limit=10,
                                         strategy_name=user_strategy_name,
                                         strategy_desc='Initial time period frequency control strategy')

        # Rules related
        strategy_confs = [
            [';'.join((menu_strategy_name_1, menu_strategy_name_2,
                       menu_strategy_name_3)),
             ';'.join((menu_uuid_1, menu_uuid_2, menu_uuid_3)), 'deny',
             'This User hit List strategy',
             '100'],

            [';'.join((bool_strategy_name_1, bool_strategy_name_2)),
             ';'.join((bool_uuid_1, bool_uuid_2)), 'log',
             'This User hit Boolean strategy',
             '90'],

            [freq_strategy_name,
             freq_uuid, 'number',
             'This User hit Time-time frequency control strategy',
             '80'],

            [user_strategy_name,
             user_uuid, 'verify',
             'This User hit User-limited number-based policy',
             '80'],
        ]
        create_rule(strategy_confs=strategy_confs, title='Initial_Rules',
                    describe='Initial sample rule', status='on', creator_name='Super_Administrator')
