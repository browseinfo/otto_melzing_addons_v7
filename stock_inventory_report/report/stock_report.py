# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import time
import operator
import itertools
from datetime import datetime
from dateutil import relativedelta
from report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text
from datetime import date
from openerp import pooler

class stock_inventory_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(stock_inventory_report, self).__init__(cr, uid, name, context)
        self.price_total = 0.0
        self.grand_total = 0.0
        self.price_value_total = 0.0
        self.grand_qty_total = 0.0
        
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'price_total': self._price_total,
            'grand_total_price':self._grand_total,
            'price_value_total': self._price_value_total,
            'grand_qty_total':self._grand_qty_total,
        })

    def process(self, location_id):
        location_obj = pooler.get_pool(self.cr.dbname).get('stock.location')
        location_write = location_obj.browse(self.cr, self.uid, [location_id])

        data = location_obj._product_get_report(self.cr,self.uid, [location_id])
        
        data['location_name'] = location_obj.read(self.cr, self.uid, [location_id],['complete_name'])[0]['complete_name']
        self.price_value_total = 0.0
        #self.price_total += data['total_price']
        #self.grand_total += data['total_price']
        
        for price in data['product']:
            self.price_total += price['prod_qty']
            self.price_value_total += price['price'] 
            self.grand_total += price['price'] 
            self.grand_qty_total += price['prod_qty']
        
        return [data]

    def _price_total(self):
        return self.price_total

    def _grand_total(self):
        return self.grand_total
    
    def _grand_qty_total(self):
        return self.grand_qty_total
            
    def _price_value_total(self):
        return self.price_value_total


report_sxw.report_sxw('report.stock.inventory.all.rml', 'stock.inventory.wizard', 'addons/stock_inventory_report/report/stock_inventory_report_all.rml', parser=stock_inventory_report, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
