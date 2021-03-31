# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super(IrHttp, self).session_info()
        user = self.env.user
        if user.has_group('base.group_user'):

            school_codes = self.env.user.school_code_ids
            district_codes = self.env.user.district_code_ids

            current_school_code = school_codes[0].read(['name'])[0]
            current_school_code['district_code_id'] = school_codes[0].district_code_id.id

            school_code_vals_list = []
            for i, school_code_vals, in enumerate(school_codes.read(['name'])):
                school_code_vals['district_code_id'] = school_codes[i].district_code_id.id
                school_code_vals_list.append(school_code_vals)

            session_info.update({
                "user_district_codes": {
                    'current_district_code': district_codes[0].read(['name'])[0],
                    'allowed_district_codes': district_codes.read(['name'])
                    },
                "user_school_codes": {
                    'current_school_code': current_school_code,
                    'allowed_school_codes': school_code_vals_list,
                    },
                })
        return session_info
