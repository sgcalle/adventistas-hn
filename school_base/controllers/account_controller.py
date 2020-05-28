# -*- coding: utf-8 -*-

from odoo import http 

import json
from datetime import datetime
from datetime import date

class StudentController(http.Controller):
    
    #metodo encargado de devolver datos de estudiantes para insertarlos en FACTS
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/account/dataAccount", auth="public", methods=["GET"], cors='*')
    # define una funcion principal
    def get_adm_uni(self, **params): 
        
        #Codigo para buscar en un modelo los datos que nos interesan        
        #crea una variable con el modelo desde donde se va a tomar la información:'adm_uni.application'          
        students = http.request.env['adm_uni.application']        
        
        #filtro del modelo basados en parametros de la url 
        #Filtramos para recoger unicamente los datos de los alumnos con un status_type = stage. Los otro filtros solo sirven de ejemplo
        search_domain = [("status_type","=","stage")]
        #search_domain = [("status_type","=","fact_integration"),("country_id", "=", int(params['country_id']))]      
        #search_domain = [("status_type","=","fact_integration")] #,("country_id", "=", int(params['country_id']))] if "country_id" in params else []
                
        #Buscamos informacion en el modelo con el filtro definido
        students_record = students.search(search_domain)      
        
        #Obtenemos los registros con los datos que buscamos. Solo recogemos los campos definidos a continuacion
        students_values = students_record.read(["id","city","country_id","state_id", "street_address","zip","first_name","middle_name","last_name","name","email",
                                                "birthdate","gender","phone", "status_id","status_type","current_school","current_school_address","create_date",
                                                "create_uid","write_date","write_uid"])

        #Se recorren por cada estudiante los datos que hemos buscado anteriormente
        for record in students_values: 
            
            # Convertir fechas a string
            if record["birthdate"]:
                record["birthdate"] = record["birthdate"].strftime('%m/%d/%Y')
            else:
                record["birthdate"] = '' 
            # Es lo mismo que:
            # date_of_birth = record["birthdate"]
            # date_of_birth = date_of_birth.strftime('%m/%d/%Y')
            # record["birthdate"] = date_of_birth 
            
            if record["create_date"]:
                record["create_date"] = record["create_date"].strftime('%m/%d/%Y')
            else:
                record["create_date"] = ''                
            
            if record["write_date"]:
                record["write_date"] = record["write_date"].strftime('%m/%d/%Y')
            else:
                record["write_date"] = ''
                
            #Por cada estudiante buscamos todos los archivos que tiene asignados
            #crea una variable con el modelo desde donde se va a tomar la información:'ir.attachment'          
            attachments = http.request.env['ir.attachment']        
        
            #filtro del modelo basados en parametros de la url. El res_id debe ser igual a el id de cada registro.
            search_domain_attach = [("res_model", "=", "adm_uni.application"),("res_id","=",record["id"])]
        
            #Buscamos informacion en el modelo con el filtro definido
            attachments_record = attachments.search(search_domain_attach)      
        
            #Obtenemos los registros con los datos que buscamos. Solo recogemos los campos definidos a continuacion
            attachments_values = attachments_record.read(["id","name"])    
            #Insertamos en el registro los valores obtenidos en esta busqueda en un campo que nos creamos llamado attachIds
            record["attachIds"] = json.dumps(attachments_values)
            
        #pasamos la informacion a Facts. Es lo que devuelve la funcion ajax.         
        return json.dumps(students_values)

    #metodo encargado de insertar en Odoo un personId que viene desde FACTS
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/account/adm_insertId", auth="public", methods=["POST"], cors='*', csrf=False)
    # define una funcion principal 
    def insertId(self, **kw):  
        data = json.loads(kw["data"])
        for itemData in data: 
            #itemData["odooId"]
            #itemData["factsId"]
            application = http.request.env['adm_uni.application']
          
            search_domain = [("id","=",itemData["odooId"])]
            
            #Tomar informacion basado en el modelo y en el domain IDS
            application_record = application.search(search_domain)      
        
            #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            application_values = application_record.partner_id
        
            application_values.sudo().write({'x_facts_id': itemData["factsId"]})
            #tomamos el modelo de application
            #application = http.request.env['adm_uni.application']        
            #obtenemos el contacto de odoo
            #contact = http.request.env['res.partner'] 
            #obj = contact.sudo().browse(application_values[0]["id"])
            #actualizamos campo
            #obj.sudo().write({'x_facts_id': itemData["factsId"]}) 
        
        return json.dumps(data)
    
    #metodo encargado de recuperar datos de una factura y enviarla a FACTS
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/account/getDataOdooFromFamilyID", auth="public", methods=["GET"], cors='*', csrf=False)
    # define una funcion principal
    def datosFact(self, **kw):         
        
        compania = http.request.env['res.company']
        search_compania = [("x_district_code","=",(kw['dist']))]
        compania_record = compania.search(search_compania)
        compania_values = compania_record.read(["id"])
        
        for com in compania_values:
            distCod = com["id"]
        
       
        students = http.request.env['account.move']        
        #students = http.request.env['account.invoice'] 

        
        #filtro del modelo basados en parametros de la url
        #Recogemos el parametro id. Si no esta en kw le pone unos []
        search_domain = [("company_id","=",distCod),("partner_id","=",int(kw['id']))] if "id" in kw else []
        
#        id = kw["fact_id"] if "fact_id" in kw else kw["id"]
#        search_domain = [("facts_id","=",int(id))]         
        
        #search_domain = [("status_type","=","fact_integration")] #,("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        #search_domain = [("status_type","=","fact_integration"),("country_id", "=", int(params['country_id']))]        
        
        #if kw['id'] != None: 
        
        #Tomar informacion basado en el modelo y en el domain IDS
        students_record = students.search(search_domain)       

        #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior       "invoice_payment_term_id", 
        students_values = students_record.read(["partner_id","ref","student_id","family_id","invoice_date","invoice_payment_term_id","journal_id","company_id","access_token",
                                                "amount_untaxed","amount_by_group","amount_total","invoice_line_ids","line_ids"])
        
        for record in students_values: 
            if record["invoice_date"]:
                record["invoice_date"] = record["invoice_date"].strftime('%m/%d/%Y')
            else:
                record["invoice_date"] = ''  
                           
                
            record["datos"] = []
            
            #crea una variable con el modelo desde donde se va a tomar la información
            datosLinea = http.request.env['account.move.line']        
            #filtro del modelo basados en parametros de la url 
            search_domain_linea = [("move_id","=",record["id"])]
            #Tomar informacion basado en el modelo y en el domain IDS
            datosLinea_record = datosLinea.search(search_domain_linea)      
            #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosLinea_values = datosLinea_record.read(["product_id","quantity","price_unit","discount","analytic_tag_ids","subscription_id","account_id","tax_ids"]) 
 
            record["datos"] = datosLinea_values
                

        return json.dumps(students_values)


#if(row[1] != None and row[2] != None):