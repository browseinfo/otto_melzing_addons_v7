# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 StoneERP
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

from openerp.osv import fields, osv

class balance_sheet_report(osv.osv_memory):
    _name = "balance.sheet.report"
    _inherit = "accounting.report"
    _description = "Balance Sheet Report"

    _columns ={
        'filter': fields.selection([('filter_period', 'Periods')], "Filter by", required=True),
    }

    _defaults = {
        'filter': 'filter_period',
        'account_report_id': 4,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter','target_move'], context=context)[0])
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.financial.report.bs',
            'datas': data,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: