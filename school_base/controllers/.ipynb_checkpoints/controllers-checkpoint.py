# -*- coding: utf-8 -*-
from odoo import http

# class Addons/schoolBase(http.Controller):
#     @http.route('/addons/school_base/addons/school_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/addons/school_base/addons/school_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('addons/school_base.listing', {
#             'root': '/addons/school_base/addons/school_base',
#             'objects': http.request.env['addons/school_base.addons/school_base'].search([]),
#         })

#     @http.route('/addons/school_base/addons/school_base/objects/<model("addons/school_base.addons/school_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('addons/school_base.object', {
#             'object': obj
#         })