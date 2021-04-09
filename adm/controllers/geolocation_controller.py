from odoo import http
import json


class BaseController(http.Controller):

    @http.route("/adm/geolocation", auth="public", methods=["GET"])
    def get_location(self, **params):
        response = http.request.make_response(data=json.dumps(http.request.session.get('geoip', {})), headers=[('Content-Type', 'application/json')])
        return response
