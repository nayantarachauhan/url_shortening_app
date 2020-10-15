from url_shortening_api.routes import *
from url_shortening_api.views.search_api import Search


api.add_resource(Search, '/search')