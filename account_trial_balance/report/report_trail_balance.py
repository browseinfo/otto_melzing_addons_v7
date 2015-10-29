# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 -Today Tiny SPRL (<http://tiny.be>).
#
##############################################################################

import time
import operator
import itertools
from datetime import datetime
from dateutil import relativedelta
from report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.report import report_sxw
from account.report.common_report_header import common_report_header
from datetime import datetime
class Parser(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'mergelines': self.mergelines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_display_account' : self.get_display_account,
            'compute_currency': self.compute_currency,
            'get_total_ytd_debit': self.get_total_ytd_debit,
            'get_total_ytd_credit': self.get_total_ytd_credit,
            'get_total_ytd_balance': self.get_total_ytd_balance,
            'get_total_debit': self.get_total_debit,
            'get_total_credit': self.get_total_credit,
            'get_total_balance': self.get_total_balance,
            
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            if data['form']['filter'] == 'filter_date':
                fromdate = data['form']['date_from']
                todate = data['form']['date_to']
                formatter_string = "%Y-%m-%d" 
                datetime_object = datetime.strptime(fromdate, formatter_string)
                date_object = datetime_object.date()
                datetime_object_to = datetime.strptime(todate, formatter_string)
                date_object_to = datetime_object_to.date()
                self.start_date = date_object.strftime("%m-%d-%Y")
                self.end_date = date_object_to.strftime("%m-%d-%Y")
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(Parser, self).set_context(objects, data, new_ids, report_type=report_type)

    #def _add_header(self, node, header=1):
    #    if header == 0:
    #        self.rml_header = ""
    #    return True


    def get_total_ytd_debit(self):
        return self.ytd_debit

    def get_total_ytd_credit(self):
        return self.ytd_credit

    def get_total_ytd_balance(self):
        return self.ytd_balance

    def get_total_debit(self):
        return self.debit

    def get_total_credit(self):
        return self.credit

    def get_total_balance(self):
        return self.balance
    
    def get_display_account(self, data):
        val = ''
        if data['form']['display_account'] == 'all':
            val = 'All' 
        elif data['form']['display_account'] == 'movement':
            val = 'With movements'
        else:
            val = 'With balance is not equal to 0'
            
        return val

    def merge_lists(self,l1, l2, key):
        merged = {}
        for item in l1+l2:
            if item[key] in merged:
                merged[item[key]].update(item)
            else:
                merged[item[key]] = item
        return [val for (_, val) in merged.items()]

    
    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(Parser ,self)._get_account(data)

    def lines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        res = self.result_acc
        return res


    def newlines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()

        start = time.strftime('%Y-%m-01') 
        end = time.strftime('%Y-%m-30')
        now = time.strftime('%Y-%m-%d')
        mon = now.split('-')
        month = mon[1] 
        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_no':
            ctx['date_from'] = start
            ctx['date_to'] =  end
        if form['filter'] == 'filter_period':
            ctx['period_from'] = month
            ctx['period_to'] = month
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = start
            ctx['date_to'] =  end
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        res = self.result_acc
        return res

    def mergelines(self, form, ids=None, done=None):
        oldfields = []
        newfields = []
        newres = []
        newlist = []
        self.ytd_debit = 0.0
        self.ytd_credit = 0.0
        self.ytd_balance = 0.0
        self.debit = 0.0
        self.credit = 0.0
        self.balance = 0.0

        res = self.lines(form, ids, done)
        for resval in res:
            resval
            linedict = {
                    'id': resval['id'],
                    'type': resval['type'],
                    'code': resval['code'],
                    'name': resval['name'],
                    'level': resval['level'],
                    'debit': resval['debit'],
                    'credit': resval['credit'],
                    'balance': resval['balance'],
                    'parent_id': resval['parent_id'],
                    'bal_type': '',
                }
            oldfields.append(linedict)
            
        newline = self.newlines(form, ids, done)
        for newval in newline:
            newval
            newlinedict = {
                    'id': newval['id'],
                    'ytd_debit': newval['debit'],
                    'ytd_credit': newval['credit'],
                    'ytd_balance': newval['balance'],
                }
            newfields.append(newlinedict)
        new = self.merge_lists(oldfields, newfields, 'id')
        if new:
            for line in new:
                #self.total_debit = self.sub_total_qty + line.product_uom_qty
                newres.append({
                    'id': line.get('id', False),
                    'code': line.get('code', False),
                    'name': line.get('name', False),
                    'parent_id': line.get('parent_id', False),
                    'level': line.get('level', False),
                    'type': line.get('type', False),
                    'bal_type': line.get('', False),
                    'ytd_credit': line.get('ytd_credit', False),
                    'ytd_debit': line.get('ytd_debit', False),
                    'ytd_balance': line.get('ytd_balance', False),
                    'debit': line.get('debit', False),
                    'credit': line.get('credit', False),
                    'balance': line.get('balance', False),
                    'ytd_total_debit': self.ytd_debit,
                    'ytd_total_credit': self.ytd_credit,
                    'ytd_total_balance': self.ytd_debit,
                    'total_debit': self.debit,
                    'total_credit': self.credit,
                    'total_balance': self.balance,
                   })
                self.ytd_debit += (line.get('ytd_debit'))
                self.ytd_credit += (line.get('ytd_credit'))
                self.ytd_balance += (line.get('ytd_balance'))
                self.debit += (line.get('debit'))
                self.credit += (line.get('credit'))
                self.balance += (line.get('balance'))
        return newres

    def compute_currency(self,to_currency, from_currency, amt):
        currency_obj = self.pool.get('res.currency')
        curr_current = from_currency
        if to_currency:
            curr_current = to_currency[0]
        amount = currency_obj.compute(self.cr, self.uid, curr_current, from_currency, amt)
        return amount
report_sxw.report_sxw('report.account.trial.balance.report', 'account.account', 'addons/account_trial_balance/report/account_trial_balance.rml', parser=Parser, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
