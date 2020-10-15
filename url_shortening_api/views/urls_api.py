import os, json, string
from random import choices
from datetime import datetime, timedelta, date
from flask import request, Request, redirect
from sqlalchemy.sql import func
from flask_restful import Resource
from flask import jsonify
import logging
from flask_restful import reqparse
from url_shortening_api import *
from url_shortening_api.models.urls import url_details
from url_shortening_api.models.visits import visits_table


############################ client_config ####################################
def generateShortUrl():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(choices(characters, k=3))
    return short_url

class UrlShortening(Resource):
    
    def post(self):

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('url', type=str, help='url is needed', required = True)

            args = parser.parse_args()
            logger.info(args)
            print("arguments passed============> ", args)

            if args["url"] is not None:
                url = args["url"]
                print("url===================", url)

            from_date = datetime.combine(date.today(), datetime.min.time())
            to_date = datetime.combine(date.today(), datetime.max.time())

            print("from_date==============",from_date)
            print("to_date================",to_date)



            results = db.session.query(url_details).filter(url_details.original_url == url)

            response = {}
           
            if not results.first():

                print("First time url is coming")
                short_url = generateShortUrl()
                shorturl_result = db.session.query(url_details).filter(url_details.short_url == short_url)
                if shorturl_result.first():
                    short_url = generateShortUrl()

                print("short_url================", short_url)


                new_data = url_details(original_url = url, short_url = short_url,visits =1)
                db.session.add(new_data)
                db.session.commit()
                print("data submitted in url_details")

                visits_new_data = visits_table(original_url = url)
                db.session.add(visits_new_data)
                db.session.commit()
                print("data submitted in visits")



                urls_results = db.session.query(url_details).filter(url_details.original_url == url)

                visits_result = db.session.query(func.HOUR(visits_table.created_at).label('date_hour'),visits_table.original_url,func.count(visits_table.original_url).label('count')).filter(visits_table.original_url == url, visits_table.created_at >= from_date, visits_table.created_at <= to_date).group_by('date_hour',visits_table.original_url)
            
                print("visits_result===================", visits_result)

                visit_response = {}
                final_response = {}

                if visits_result.first():

                    for index, res in enumerate(visits_result):
                        visit_response[res.date_hour] = {
                        "count" : res.count
                        }

                for index, res in enumerate(urls_results):
                    final_response[index] = {
                    "original_url" : res.original_url,
                    "short_url" : res.short_url,
                    "total_visits" : res.visits,
                    "hourly_visits" : visit_response
                    }



                return jsonify(final_response)


            
            elif results.first():
                print("Url already exsists===========>")


                for res in results:
                    visits = int(res.visits)

                visits +=1

                print("visits===============",visits)


                db.session.query(url_details).filter(url_details.original_url == url).update({"visits" : visits})
                db.session.commit()
                print("data submitted in url_details")

                visits_new_data = visits_table(original_url = url)
                db.session.add(visits_new_data)
                db.session.commit()
                print("data submitted in visits")



            
                visits_result = db.session.query(func.HOUR(visits_table.created_at).label('date_hour'),visits_table.original_url,func.count(visits_table.original_url).label('count')).filter(visits_table.original_url == url, visits_table.created_at >= from_date, visits_table.created_at <= to_date).group_by('date_hour',visits_table.original_url)
                
                print("visits_result===================", visits_result)

                visit_response = {}
                final_response = {}

                if visits_result.first():

                    for index, res in enumerate(visits_result):
                        visit_response[res.date_hour] = {
                        "count" : res.count
                        }
                

                urls_results = db.session.query(url_details).filter(url_details.original_url == url)


                for index, res in enumerate(urls_results):
                    final_response[index] = {
                    "original_url" : res.original_url,
                    "short_url" : res.short_url,
                    "total_visits" : int(res.visits),
                    "hourly_visits" : visit_response
                    }


                return jsonify(final_response)

                

        except Exception as e:

            logger.info("************** Error ******************")
            logger.exception(e)

            return {"Error" : str(e)}



class Visits(Resource):
    
    def get(self,short_url):

        try:
            s_url = short_url
            
            result = db.session.query(url_details).filter_by(short_url = s_url).first()

            if result:

                original_url = result.original_url

                return redirect(original_url)
            
            else:

                return jsonify({"Message" :  "No such short_url exists"})


        except Exception as e:

            logger.info("************** Error ******************")
            logger.exception(e)

            return {"Error" : str(e)}



