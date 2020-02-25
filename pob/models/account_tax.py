#!/usr/bin/env python
# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)#
#																				 #
##################################################################################

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = 'account.tax'


    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        ecomm_cannels = dict(self.env['connector.snippet']._get_ecomm_extensions()).keys()
        if any(key in ctx for key in ecomm_cannels):
            if vals.get('name'):
                tax_id = self.search([('name','=', vals['name'])])
                if tax_id:
                    return tax_id
        return super(AccountTax,self).create(vals)