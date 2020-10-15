from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


from url_shortening_api.routes.urls_routes import *
from url_shortening_api.routes.search_routes import *


