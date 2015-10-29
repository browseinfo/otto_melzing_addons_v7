# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Tiny SPRL (<http://browseinfo.in>).
##############################################################################

{
    'name': 'Account Trial Balance',
    'version': '0.1',
    'category': 'Tools',
    'description': """
This module open a trial balance report
=================================================================
 this module is for trial balance report  which is rml in openerp 7.0


""",
    'author': 'Browseinfo',
    'website': 'www.brwoseinfo.in',
    'depends': [
        'account',
    ],
    'data': [
        'wizard/wizard_trail_balance_view.xml',
        'report/report_general_ledger_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
