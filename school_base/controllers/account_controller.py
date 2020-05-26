# -*- coding: utf-8 -*-

from odoo import http 

import json
from datetime import datetime
from datetime import date

##
#controlador encargado de devolver data de estudiantes, para insertarlo en FACTS
class StudentController(http.Controller):
    
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/account/dataAccount", auth="public", methods=["GET"], cors='*')
    # define una funcion principal
    def get_adm_uni(self, **params): 
        #crea una variable con el modelo desde donde se va a tomar la información 
        # adm_uni.application
        # status_type
        students = http.request.env['res.partner']#adm_uni.application']        
        
        #filtro del modelo basados en parametros de la url 
        search_domain = []#("status_type","=","stage")]
        #search_domain = [("status_type","=","fact_integration")] #,("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        #search_domain = [("status_type","=","fact_integration"),("country_id", "=", int(params['country_id']))] 
        
        #Tomar informacion basado en el modelo y en el domain IDS
        students_record = students.search(search_domain)      
        
        #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
        students_values = students_record.read(["id"]#,"city","country_id","state_id", "street_address","zip","first_name","middle_name","last_name","name","email", "birthdate","gender","phone", "status_id","status_type","current_school","current_school_address","create_date","create_uid","write_date","write_uid"])


            
        #students_values.append("test")
        #pintar la información obtenida, esto lo utilizamos para parsearlo en el ajax.         
        return json.dumps(students_values)

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
    
    
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/account/getDataOdooFromFamilyID", auth="public", methods=["GET"], cors='*', csrf=False)
    # define una funcion principal
    def datosFact(self, **kw):                         
        #{"id": 17, "first_name": "Luis"}
        #data = '[{"id": 16}]'
                
        #data = json.loads(data)
        #data = json.loads(kw["data"])        
        
       
        students = http.request.env['account.move']        
        #students = http.request.env['account.invoice']

        
        #filtro del modelo basados en parametros de la url
        #Recogemos el parametro id. Si no esta en kw le pone unos []
        search_domain = [("partner_id","=",int(kw['id']))] #if "id" in kw else []
        
#        id = kw["fact_id"] if "fact_id" in kw else kw["id"]
#        search_domain = [("facts_id","=",int(id))]         
        
        #search_domain = [("status_type","=","fact_integration")] #,("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        #search_domain = [("status_type","=","fact_integration"),("country_id", "=", int(params['country_id']))]        
        
        #if kw['id'] != None: 
        
        #Tomar informacion basado en el modelo y en el domain IDS
        students_record = students.search(search_domain)      

        #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior        
        students_values = students_record.read(["access_token","amount_total","date_invoice","date_due","payment_term_id","user_id","invoice_line_ids"])
        
        for record in students_values: 
            if record["date_invoice"]:
                record["date_invoice"] = record["date_invoice"].strftime('%m/%d/%Y')
            else:
                record["date_invoice"] = ''                

            if record["date_due"]:
                record["date_due"] = record["date_due"].strftime('%m/%d/%Y')
            else:
                record["date_due"] = ''                
                
            record["datosLinea"] = []
            
#            for lineas in invoice_line_id:           
             
                #crea una variable con el modelo desde donde se va a tomar la información
            datosLinea = http.request.env['account.invoice.line']        

                #filtro del modelo basados en parametros de la url 
            search_domain_attach = [("invoice_id","=",record["id"])] 

                #Tomar informacion basado en el modelo y en el domain IDS
            datosLinea_record = datosLinea.search(search_domain_attach)      

                #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
            datosLinea_values = datosLinea_record.read(["product_id","quantity"]) 
                
 #           record["datosLinea"] = json.dumps(datosLinea_values)         

            record["datosLinea"] = datosLinea_values
                

        return json.dumps(students_values)


#if(row[1] != None and row[2] != None):