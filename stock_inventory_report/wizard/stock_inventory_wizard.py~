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
from datetime import datetime
from dateutil import relativedelta

from osv import fields, osv

class stock_inventory_wizard(osv.osv_memory):
    _name ='stock.inventory.wizard'

    _columns = {
        'type': fields.selection([('supplier', 'Incoming Location'), ('customer', 'Outgoing Location'), ('internal', 'Internal Location')], 'Type', required=True),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: return report
        """
        if context is None:
            context = {}
                
        data = self.read(cr, uid, ids[0], ['type', 'active'], context=context)
        
        stock_location_obj = self.pool.get('stock.location')
        location_ids = stock_location_obj.search(cr, uid, [('usage', '=', data['type'])])
        for location in stock_location_obj.browse(cr, uid, location_ids):
            location.write({'print_report': True})
        
        datas = {
            'ids': location_ids,
            'model': 'stock.inventory.wizard',
            'context': {'location': location_ids},
            'domain': [('type', '<>', 'service')]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.inventory.all.rml',
            'datas': datas,
        }

stock_inventory_wizard()

class stock_location(osv.Model):
    _inherit = 'stock.location'
    
    _columns = {
        'print_report': fields.boolean('Active'),
    }
    
    _defaults = {
        'print_report': 0,
    }
    
    def _product_get_report(self, cr, uid, ids, product_ids=False,
            context=None, recursive=False):
        """ Finds the product quantity and price for particular location.
        @param product_ids: Ids of product
        @param recursive: True or False
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        # Take the user company and pricetype
        context['currency_id'] = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id

        # To be able to offer recursive or non-recursive reports we need to prevent recursive quantities by default
        context['compute_child'] = False
        
        stock_ids = self.browse(cr, uid, ids, context=context)
        
        if stock_ids[0].print_report:
            if not product_ids:
                product_ids = product_obj.search(cr, uid, [], context={'active_test': False})

            products = product_obj.browse(cr, uid, product_ids, context=context)
            products_by_uom = {}
            products_by_id = {}
            for product in products:
                products_by_uom.setdefault(product.uom_id.id, [])
                products_by_uom[product.uom_id.id].append(product)
                products_by_id.setdefault(product.id, [])
                products_by_id[product.id] = product

            result_ok = {}
            result_ok['product'] = []

            stock_obj = self.pool.get('stock.move')        
            for id in ids:
                quantity_total = 0.0
                total_price = 0.0
                
                fnc = self._product_get
                if recursive:
                    fnc = self._product_all_get
                        
                serial_number = stock_obj.search(cr, uid, [('location_id', '=', id)], context=context)
                for stock_move_browse in stock_obj.browse(cr, uid, serial_number):
                    if stock_move_browse.prodlot_id:
                        result_ok['product'].append({
                            'price': (stock_move_browse.product_qty * stock_move_browse.price_unit),
                            'prod_name': stock_move_browse.product_id.name,
                            'serial_num': stock_move_browse.prodlot_id.name,
                            'product_id':stock_move_browse.product_id.id,
                            'code': stock_move_browse.product_id.default_code, # used by lot_overview_all report!
                            'variants': stock_move_browse.product_id.variants or '',
                            'uom': stock_move_browse.product_id.uom_id.name,
                            'prod_qty': stock_move_browse.product_qty,
                            'price_value': stock_move_browse.price_unit,
                        })
                    else:
                        result_ok['product'].append({
                            'price': (stock_move_browse.product_qty * stock_move_browse.price_unit),
                            'product_id':stock_move_browse.product_id.id,
                            'serial_num': '',
                            'prod_name': stock_move_browse.product_id.name,
                            'code': stock_move_browse.product_id.default_code, # used by lot_overview_all report!
                            'variants': stock_move_browse.product_id.variants or '',
                            'uom': stock_move_browse.product_id.uom_id.name,
                            'prod_qty': stock_move_browse.product_qty,
                            'price_value': stock_move_browse.price_unit,
                        })
            stock_ids[0].write({'print_report': False})
            return result_ok
            
        else:
            if not product_ids:
                product_ids = product_obj.search(cr, uid, [], context={'active_test': False})

            products = product_obj.browse(cr, uid, product_ids, context=context)
            products_by_uom = {}
            products_by_id = {}
            for product in products:
                products_by_uom.setdefault(product.uom_id.id, [])
                products_by_uom[product.uom_id.id].append(product)
                products_by_id.setdefault(product.id, [])
                products_by_id[product.id] = product

            result = {}
            result['product'] = []
            for id in ids:
                quantity_total = 0.0
                total_price = 0.0
                for uom_id in products_by_uom.keys():
                    fnc = self._product_get
                    if recursive:
                        fnc = self._product_all_get
                    ctx = context.copy()
                    ctx['uom'] = uom_id
                    qty = fnc(cr, uid, id, [x.id for x in products_by_uom[uom_id]],
                            context=ctx)
                    for product_id in qty.keys():
                        if not qty[product_id]:
                            continue
                        product = products_by_id[product_id]
                        quantity_total += qty[product_id]

                        # Compute based on pricetype
                        # Choose the right filed standard_price to read
                        amount_unit = product.price_get('standard_price', context=context)[product.id]
                        price = qty[product_id] * amount_unit

                        total_price += price
                        result['product'].append({
                            'price': amount_unit,
                            'prod_name': product.name,
                            'code': product.default_code, # used by lot_overview_all report!
                            'variants': product.variants or '',
                            'uom': product.uom_id.name,
                            'prod_qty': qty[product_id],
                            'price_value': price,
                        })
            result['total'] = quantity_total
            result['total_price'] = total_price
            return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
