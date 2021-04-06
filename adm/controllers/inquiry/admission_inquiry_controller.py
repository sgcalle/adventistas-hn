# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.adm.utils import formatting
import base64


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class InquiryController(http.Controller):

    #===================================================================================================================
    # @http.route("/")
    # def
    #===================================================================================================================

    @http.route("/admission/inquiry", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        countries = http.request.env['res.country'].sudo()
        states = http.request.env['res.country.state'].sudo()
        contact_times = http.request.env['adm.contact_time']
        degree_programs = http.request.env['adm.degree_program']

        grade_level = http.request.env['school_base.grade_level']
        school_year = http.request.env['school_base.school_year']

        family_id = -1

        if 'family_id' in params:
            family_id = params['family_id']

        companies = http.request.env['res.company'].sudo().search([('country_id','!=',False)])
        response = http.request.render('adm.template_admission_inquiry', {
            'grade_levels': grade_level.search([('active_admissions', '=', True)]),
            'countries': countries.search([]),
            'check_family_id': True,
            'family_name': '',
            'family_id': family_id,
            'company': companies and companies[0],
        })
        return response

    @http.route("/admission/inquiry", auth="public", methods=["POST"], website=True, csrf=False)
    def add_inquiry(self, **params):
        PartnerEnv = http.request.env['res.partner']

        if "txtMiddleName_1" not in params:
            params["txtMiddleName_1"] = ""

        if 'checkbox_family_id' in params and params["checkbox_family_id"] == 'on':
            family_id_fact = params["input_family_id"]
            if len(PartnerEnv.sudo().search([('facts_id', '=', family_id_fact), ('is_family', '=', True)])) == 0:
                countries = http.request.env['res.country']
                states = http.request.env['res.country.state']
                contact_times = http.request.env['adm.contact_time']
                degree_programs = http.request.env['adm.degree_program']
                grade_level = http.request.env['school_base.grade_level']
                school_year = http.request.env['school_base.school_year']

                response = http.request.render('adm.template_admission_inquiry', {
                    'grade_levels': grade_level.search([('active_admissions', '=', True)]),
                    'countries': countries.search([]),
                    'check_family_id': False,
                    'family_name': '',
                    'parent': False,
                })
                return response
            else:
                # Para tomar por facts id
                # Caso de tomar por el facts ud id
                family_data = \
                    PartnerEnv.sudo().search([
                        ('facts_id', '=', family_id_fact),
                        ('is_family', '=', True)])[0]
                family_id = family_data
                mobile_1 = family_data.mobile
                email_1 = family_data.email
                parents_ids_created = (
                    family_data.member_ids
                    .filtered(lambda item: item.function == 'parent')).ids

        else:
            # Create a new family
            first_name = params["txtFirstName_1"]
            middle_name = params["txtMiddleName_1"]
            last_name = params["txtLastName_1"]
            country_id = int(params["selCountry_1"])

            mobile_1 = params["txtCellPhone_1"]
            email_1 = params["txtEmail_1"]

            family_1 = ''
            if 'selFamily_1' in params:
                family_1 = params["selFamily_1"]

            partner_body = {
                    "name": "{} family".format(last_name),
                    "company_type": "company",
                    "is_family": True,
                    'mobile': mobile_1,
                    'email': email_1,
                }

            if family_1 is '':
                family_id = PartnerEnv.sudo().create(partner_body)
                parent_id_1 = PartnerEnv.sudo().create({
                    # "name": full_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "parent_id": family_id.id,
                    "function": "parent",
                    "family_ids": [(6,0,[family_id.id])],
                    "country_id":country_id,
                    'mobile': mobile_1,
                    'email': email_1,
                    })
                parent_id_1.auto_format_name()
            else:
                family_id = PartnerEnv.sudo().search([('id', '=', family_1)])
                parent_id_1 = \
                    PartnerEnv.sudo().search([
                        ('email', '=',email_1),
                        ('function', '=', 'parent')
                        ])[0]

            parents_ids_created = []
            family_id.write({'member_ids': [(4,parent_id_1.id)]})
            parents_ids_created.append(parent_id_1.id)

            if "txtMiddleName_2" not in params:
                params["txtMiddleName_2"] = ""

            if all(k in params for k in ("txtFirstName_2", "txtLastName_2", "selCountry_2", "txtCellPhone_2","txtEmail_2")):
                first_name = params["txtFirstName_2"]
                middle_name = params["txtMiddleName_2"]
                last_name = params["txtLastName_2"]
                country_id = int(params["selCountry_2"])
                mobile_2 = params["txtCellPhone_2"]
                email_2 = params["txtEmail_2"]

                if len(PartnerEnv.sudo().search([('email', '=', email_2), ('function', '=', 'parent')])) > 0:
                    parent_id_2 = PartnerEnv.sudo().search([('email', '=', email_2), ('function', '=', 'parent')])[0]
                    parent_id_2.write({'family_ids': [(4,family_id.id)]})
                else:
                    parent_id_2 = PartnerEnv.sudo().create({
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "parent_id": family_id.id,
                        "function": "parent",
                        "family_ids": [(6, 0, [family_id.id])],
                        "country_id": country_id,
                        'mobile': mobile_2,
                        'email': email_2,
                        })
                    parent_id_2.auto_format_name()

                parents_ids_created.append(parent_id_2.id)
                family_id.write({'member_ids': [(4, parent_id_2.id)]})

        # Create students
        id_students = list()
        students_total = int(params["studentsCount"])

        first_name_list = post_parameters().getlist("txtStudentFirstName")
        last_name_list = post_parameters().getlist("txtStudentLastName")
        middle_name_list = post_parameters().getlist("txtStudentMiddleName")
        birthday_list = post_parameters().getlist("txtStudentBirthday")
        current_grade_level_list = \
            post_parameters().getlist("selStudentCurrentGradeLevel")

        InquiryEnv = http.request.env["adm.inquiry"]

        for index_student in range(students_total):
            first_name = first_name_list[index_student]
            middle_name = middle_name_list[index_student]
            last_name = last_name_list[index_student]
            birthday = birthday_list[index_student]
            current_grade_level = current_grade_level_list[index_student]

            id_student = PartnerEnv.sudo().create({
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "parent_id": family_id.id,
                "function": "student",
                "person_type": "student",
                "family_ids": [(6, 0, [family_id.id])],
                'date_of_birth': birthday,
                'mobile': mobile_1,
                'email': email_1,
                })
            id_student.auto_format_name()
            family_id.write({'member_ids': [(4, id_student.id)]})

            # Create an inquiry for each new student
            new_inquiry = InquiryEnv.sudo().create({
                'partner_id': id_student.id,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'current_grade_level_id':
                    current_grade_level and int(current_grade_level) or False,
                'responsible_id': [(6, 0, parents_ids_created)],
                })

            id_student.inquiry_id = new_inquiry.id
            id_students.append(id_student)

            if params.get("message"):
                new_inquiry.message_post(body="Message/Question: %s" % params["message"])

        response = http.request.render('adm.template_inquiry_sent')
        return response

