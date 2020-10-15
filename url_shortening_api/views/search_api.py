import os, json, re
from datetime import date, timedelta, datetime
from flask import request, Request, current_app
from flask_restful import Resource
from flask import jsonify
import logging
from flask_restful import reqparse
from url_shortening_api import *
from url_shortening_api.models.urls import url_details


class Search(Resource):
    
    def get(self):

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('url_content', type=str, help='url_content is needed!', required = True)
            
            args = parser.parse_args()
            print(args)

            if args["url_content"]:
                url_content = args["url_content"]

            results = db.session.query(url_details).filter(url_details.original_url.contains(url_content))
            
            final_response = {}

            if results.first():

                for index, res in enumerate(results):
                    final_response[index] = {
                    "id": res.id,
                    "original_url": res.original_url,
                    "short_url": res.short_url
                    }

                logger.info("final_response============%s" % final_response)

                return jsonify(final_response)

            else:

                return jsonify({"Message" : "Nothing exists regarding the text you searched for."})


        except Exception as e:
            return {"error" : str(e)}