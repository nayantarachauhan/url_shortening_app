from flask_restful import reqparse
from adda_api import *
from sqlalchemy import func
import json
from datetime import date, timedelta, datetime


####################### DATABASE FUNCTIONS ######################################


class DB_query:
    
    def get(table):
        parser = reqparse.RequestParser()
        parser.add_argument('ref_num', type=str, help='ref_num is needed!', required = True)
        parser.add_argument('source_name', type=str, help='source_name is needed!', required = True)
        args = parser.parse_args()

        source_name    = current_app.config['SOURCE_NAME']

        if 'source_name' in args and args['source_name']:
            source_name = args['source_name'].split(',')

        results = db.session.query(table).filter(table.ref_num == args['ref_num'], table.source_name.in_(source_name))
        return results

    
    def getFromVehicle(table, status):
        parser = reqparse.RequestParser()
        parser.add_argument('source_name', type=str, help='source_name is needed!', required = True)
        parser.add_argument('start_date', type=str)
        parser.add_argument('stop_date', type=str)
        args = parser.parse_args()

        if args['start_date'] is None and args['stop_date'] is None:
            results = db.session.query(table).filter(table.source_name == args['source_name'], table.claim_state == status)
        
        elif args['stop_date'] is None:
            results = db.session.query(table).filter(table.source_name == args['source_name'], table.claim_state == status, table.created_at >= args['start_date'])

        else:
            results = db.session.query(table).filter(table.source_name == args['source_name'], table.claim_state == status, table.created_at >= args['start_date'],  table.created_at <= args['stop_date'] )

        return results

    

    def getAssessReport(table):
        parser = reqparse.RequestParser()
        parser.add_argument('source_name', type=str, help='source_name is needed!', required = True)
        parser.add_argument('start_date', type=str)
        parser.add_argument('stop_date', type=str)
        args = parser.parse_args()

        if args['start_date'] is None and args['stop_date'] is None:
            results = db.session.query(func.sum(table.total_claims), func.sum(table.completed), func.sum(table.failed) ).filter(table.source_name == args['source_name']).order_by(table.created_at.desc())
        
        elif args['stop_date'] is None:
            results = db.session.query(func.sum(table.total_claims), func.sum(table.completed), func.sum(table.failed)).filter(table.source_name == args['source_name'], table.created_at >= args['start_date'])

        else:
            stop_date = args['stop_date']
            stop_date = datetime.strftime(datetime.strptime(stop_date, "%Y-%m-%d") + timedelta(days=1), "%Y-%m-%d")

            results = db.session.query(func.sum(table.total_claims), func.sum(table.completed), func.sum(table.failed)).filter(table.source_name == args['source_name'], table.created_at >= args['start_date'],  table.created_at <= stop_date )

        return results

    

    def put(_id, table):
        parser = reqparse.RequestParser()
        parser.add_argument('keyValue', type=str, help='column_name is needed!', required = True)
        # parser.add_argument('column_value', type=str, help='column_value is needed!', required = True)
        args = parser.parse_args()

        args = json.loads(args["keyValue"])

        logger.info("args----%s" % args)
        print("args----%s" % args)

        for key, value in args.items():
            db.session.query(table).filter_by(id = _id).update({key: value})
        
        db.session.commit()

    def corpDetailsPut(_id, table):
        parser = reqparse.RequestParser()
        parser.add_argument('keyValue', type=str, help='column_name is needed!', required = True)
        # parser.add_argument('column_value', type=str, help='column_value is needed!', required = True)
        args = parser.parse_args()

        args = json.loads(args["keyValue"])

        logger.info("args----%s" % args)
        print("args----%s" % args)

        for key, value in args.items():
            db.session.query(table).filter_by(client_details_id = _id).update({key: value})
        
        db.session.commit()

    def client_reset_pass_put(universal_id, table):
        parser = reqparse.RequestParser()
        parser.add_argument('keyValue', type=str, help='column_name is needed!', required = True)
        # parser.add_argument('column_value', type=str, help='column_value is needed!', required = True)
        args = parser.parse_args()

        args = json.loads(args["keyValue"])

        logger.info("args----%s" % args)
        print("args----%s" % args)

        for key, value in args.items():
            if key == "flag":
                value = int(value)
            db.session.query(table).filter_by(universal_id = universal_id).update({key: value})
        
        db.session.commit()

    def clientuser_put(u_id, table):
        parser = reqparse.RequestParser()
        parser.add_argument('keyValue', type=str, help='column_name is needed!', required = True)
        # parser.add_argument('column_value', type=str, help='column_value is needed!', required = True)
        args = parser.parse_args()

        args = json.loads(args["keyValue"])

        logger.info("args----%s" % args)
        print("args----%s" % args)

        for key, value in args.items():
            if key == "password":
                print("coming inside if")
                print(value)
                value = flask_bcrypt.generate_password_hash(value).decode("utf8")
                print(value)
                
            db.session.query(table).filter_by(id = u_id).update({key: value})
        
        db.session.commit()
        


    def AssessPut(_id, table, data):

        logger.info("args----%s" % data)
        print("args----%s" % data)

        for key, value in data.items():
            db.session.query(table).filter_by(part_id = _id).update({key: value})
        
        db.session.commit()

    

    def delete(table):
        parser = reqparse.RequestParser()
        parser.add_argument('ref_num', type=str, help='ref_num is needed!', required = True)
        parser.add_argument('source_name', type=str, help='source_name is needed!', required = True)
        args = parser.parse_args()

        db.session.query(table).filter(table.ref_num == args['ref_num'], table.source_name == args['source_name']).delete(synchronize_session=False)
        db.session.commit()
