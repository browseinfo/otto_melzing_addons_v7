# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Tiny SPRL (<http://www.browseinfo.in>).
##############################################################################

from osv import fields, osv

class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"
    _columns = {
              'currency_id' : fields.many2one('res.currency', 'Currency'),
    }

    def _print_report_excel(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.trial.balance.report', 'datas': data}
    
    def check_report_excel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['currency_id','amount_currency','date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = used_context
        return self._print_report_excel(cr, uid, ids, data, context=context)
account_balance_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
