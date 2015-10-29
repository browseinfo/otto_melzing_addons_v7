# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today browseinfo
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw
import datetime
#from datetime import datetime
from openerp.tools.translate import _

class account_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_year': self.get_year,
            'get_lines': self.get_lines,
            'get_datetime': self.get_datetime,
            'get_period': self.get_period,
            'get_time': self.get_time,
        })
    def get_period(self, data):
        if data['form'].get('period_to'):
            return self.pool.get('account.period').browse(self.cr, self.uid, data['form'].get('period_to')).code
        return ''

    def get_year(self, data):
        return self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name

    def get_datetime(self):
        return datetime.today()
    def get_time(self):
        return str(datetime.today().time()).split('.')[0]

    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')
        account_type_obj = self.pool.get('account.account.type')
        currency_obj = self.pool.get('res.currency')
        financial_report_obj = self.pool.get('account.financial.report')
        main_dict = {}
        current_date = datetime.date.today()
        current_month_first_date = datetime.date(current_date.year, current_date.month, 1)
        bs_account_id = account_obj.search(self.cr, self.uid, [('name','=',data['form']['account_report_id'][1])])
        ids3 = self.pool.get('account.financial.report').search(self.cr, self.uid, ['|',('parent_id','=',data['form']['account_report_id'][0]),
                                                                                    ('name','in',['Assets', 'Liability', 'Equity'])], context=data['form']['used_context'])
        print "\n\n\n\n ****ids3",ids3
        acc_id = acc2_id = []
        for report in financial_report_obj.browse(self.cr, self.uid, ids3, context=data['form']['used_context']):
            valss = {
                'name': report.name,
                'balance': '',
                'type': 'report',
                'level': 1,
                'account_type': report.type =='sum' and 'view' or False,
            }
            if report.display_detail == 'no_detail':
                continue
            lines.append(valss)
            main_dict.update({report.id : valss})
            account_ids = []
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            if account_ids:
                if not data['form']['used_context'].get('period_from'):
                    data['form']['used_context'].update({'period_from': data['form'].get('period_from')})
                if not data['form']['used_context'].get('period_to'):
                    data['form']['used_context'].update({'period_to': data['form'].get('period_to')})
                if data['form']['used_context'] and data['form']['used_context'].get('date_from'):
                    del data['form']['used_context']['date_from']
                if data['form']['used_context'] and data['form']['used_context'].get('date_to'):
                    del data['form']['used_context']['date_to']
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=data['form']['used_context']):
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    if account.parent_id.id not in bs_account_id and account.type == 'view':# and account.child_id:
                        continue
                    flag = False

                    if account.parent_id.id in bs_account_id:
                        for account2 in account_obj.browse(self.cr, self.uid, acc_id, context=data['form']['used_context']):
                            vals2 = {
                                'name': 'Total ' + account2.name,
                                'balance': account2.balance != 0 and account2.balance * report.sign or account2.balance,
                                'type': 'account',
                                'level': 2,
                                'account_type': account2.type,
                            }
                            if not currency_obj.is_zero(self.cr, self.uid, account2.company_id.currency_id, vals2['balance']):
                                lines.append(vals2)
                                main_dict.update({account2.id : vals2})
                        acc_id = []
                        acc_id.append(account.id)
                        vals = {
                            'name': account.name,
                            'balance': 0.0,
                            'type': 'account',
                            'level': 2,
                            'account_type': account.type,
                        }
                    else:
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance': account.balance != 0 and account.balance * report.sign or account.balance,
                            'type': 'account',
                            'level': 4,
                            'account_type': account.type,
                        }
                    if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, account.balance != 0 and account.balance * report.sign or account.balance):
                        flag = True
                    if flag:
                        lines.append(vals)
                        main_dict.update({account.id : vals})
                for account2 in account_obj.browse(self.cr, self.uid, acc_id, context=data['form']['used_context']):
                    vals2 = {
                        'name': 'Total ' + account2.name,
                        'balance': account2.balance != 0 and account2.balance * report.sign or account2.balance,
                        'type': 'account',
                        'level': 2,
                        'account_type': account2.type,
                    }
                    if not currency_obj.is_zero(self.cr, self.uid, account2.company_id.currency_id, vals2['balance']):
                        lines.append(vals2)
                        main_dict.update({account2.id : vals2})
                acc_id = []
                valss2 = {
                    'name': 'Total ' + report.name,
                    'balance': report.balance * report.sign or 0.0,
                    'type': 'report',
                    'level': 1,
                    'account_type': report.type =='sum' and 'view' or False,
                }
                if data['form']['used_context'] and data['form']['used_context'].get('period_from'):
                    del data['form']['used_context']['period_from']
                if data['form']['used_context'] and data['form']['used_context'].get('period_to'):
                    del data['form']['used_context']['period_to']
                if data['form']['used_context'] and data['form']['used_context'].get('periods'):
                    del data['form']['used_context']['periods']

                data['form']['used_context'].update({'date_from': tools.ustr(current_month_first_date), 'date_to': tools.ustr(current_date)})
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=data['form']['used_context']):
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    if account.parent_id.id not in bs_account_id and account.type == 'view':
                        continue
                    flag = flag2 = False
                    if account.parent_id.id in bs_account_id:
                        i_flag = i_flag2 = False
                        for account2 in account_obj.browse(self.cr, self.uid, acc2_id, context=data['form']['used_context']):
                            vals2 = {
                                'name': 'Total ' +  account2.name,
                                'balance2': account2.balance != 0 and account2.balance * report.sign or account2.balance,
                                'type': 'account',
                                'level': 2,
                                'account_type': account2.type,
                            }
                            if not currency_obj.is_zero(self.cr, self.uid, account2.company_id.currency_id, vals2['balance2']):
                                i_flag = True
                            if i_flag:
                                for key, values in zip(main_dict.keys(), main_dict.values()):
                                    if account.id == key:
                                        values.update({'balance2': account.balance != 0 and account.balance * report.sign or account.balance})
                                        i_flag2=True
                                if not i_flag2:
                                    lines.append(vals2)
                        acc2_id = []
                        acc2_id.append(account.id)
                        vals = {
                            'name': account.name,
                            'balance2': 0.0,
                            'type': 'account',
                            'level': 2,
                            'account_type': account.type,
                        }
                    else:
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance2':  account.balance != 0 and account.balance * report.sign or account.balance,
                            'type': 'account',
                            'level': 4,
                            'account_type': account.type,
                        }
                    if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, account.balance != 0 and account.balance * report.sign or account.balance):
                        flag = True
                    if flag:
                        for key, values in zip(main_dict.keys(), main_dict.values()):
                            if account.id == key:
                                values.update({'balance2': account.balance != 0 and account.balance * report.sign or account.balance})
                                flag2=True
                        if not flag2:
                            lines.append(vals)
                iflag = iflag2 = False
                for account2 in account_obj.browse(self.cr, self.uid, acc2_id, context=data['form']['used_context']):
                    vals2 = {
                        'name': 'Total ' + account2.name,
                        'balance2': account2.balance != 0 and account2.balance * report.sign or account2.balance,
                        'type': 'account',
                        'level': 2,
                        'account_type': account2.type,
                    }
                    if not currency_obj.is_zero(self.cr, self.uid, account2.company_id.currency_id, vals2['balance2']):
                        iflag = True
                    if iflag:
                        for key, values in zip(main_dict.keys(), main_dict.values()):
                            if account2.id == key:
                                values.update({'balance2': account2.balance != 0 and account2.balance * report.sign or account2.balance})
                                iflag2=True
                        if not iflag2:
                            lines.append(vals2)
                acc2_id = []
            for report in financial_report_obj.browse(self.cr, self.uid, [report.id], context=data['form']['used_context']):
                valss2.update({'balance2': report.balance * report.sign or 0.0})
                lines.append(valss2)

        return lines


report_sxw.report_sxw('report.account.pl.extended', 'accounting.report', 'profit_and_loss_report/report/account_profit_and_loss.rml', parser=account_report, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

