from url_shortening_api.routes import *
from url_shortening_api.views.urls_api import UrlShortening,Visits


api.add_resource(UrlShortening,'/url_shortening')
api.add_resource(Visits, '/<short_url>')

