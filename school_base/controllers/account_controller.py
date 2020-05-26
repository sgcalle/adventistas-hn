# -*- coding: utf-8 -*-

from odoo import http 

import json
from datetime import datetime
from datetime import date

##
#controlador encargado de devolver data de estudiantes, para insertarlo en FACTS
class StudentController(http.Controller):
    
    #definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/account/dateTesting", auth="public", methods=["GET"], cors='*')
    # define una funcion principal
    def get_adm_uni(self, **params): 
        #crea una variable con el modelo desde donde se va a tomar la información 
        # adm_uni.application
        # status_type
        students = http.request.env['res.partner']#adm_uni.application']        
        
        #filtro del modelo basados en parametros de la url 
        search_domain = [] #("status_type","=","stage")]
        #search_domain = [("status_type","=","fact_integration")] #,("country_id", "=", int(params['country_id']))] if "country_id" in params else []
        #search_domain = [("status_type","=","fact_integration"),("country_id", "=", int(params['country_id']))] 
        
        #Tomar informacion basado en el modelo y en el domain IDS
        students_record = students.search(search_domain)      
        
        #Obtienes la información basada en los ids anteriores y tomando en cuenta los campos definifos en la funcion posterior
        students_values = students_record.read(["id"])#,"city","country_id","state_id", "street_address","zip","first_name","middle_name","last_name","name","email", "birthdate","gender","phone", "status_id","status_type","current_school","current_school_address","create_date","create_uid","write_date","write_uid"]) 
        
        #students_values.append("test")
        #pintar la información obtenida, esto lo utilizamos para parsearlo en el ajax.         
        return json.dumps(students_values) 