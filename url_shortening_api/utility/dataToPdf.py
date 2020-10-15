import os, json, shutil, math
import pandas as pd
import urllib.request
from fpdf import FPDF
from flask import request, Request,send_file
from flask_restful import Resource
from flask import jsonify
import logging
from flask_restful import reqparse
from adda_api import *
from adda_api.configuration.api_access_config import *
from adda_api.views.user_registerNlogin import checkAccessLevel
from adda_api.utility.common_db_functions import DB_query
from adda_api.models.insurance_vehicle import insurance_vehicle
from adda_api.models.insurance_part import insurance_part
from adda_api.models.insurance_damage import insurance_damage
from adda_api.models.insurance_carimage import insurance_carimage
from adda_api.models.claimsummaryindividual import claim_summary_individual
from adda_api.models.uploads import uploads_table
from adda_api.models.assess_final import assess_final
from adda_api.models.vehicleassess_parthistory import vehicle_assessment_part_history


def DataToPDF(ref_num, source_name):
    try:
        if ref_num is not None:
            vehicle_results = db.session.query(insurance_vehicle).filter(insurance_vehicle.ref_num == ref_num).first()
            
            if vehicle_results:

                make = vehicle_results.make
                model = vehicle_results.model
                num_plate = vehicle_results.num_plate
                created_at = str(vehicle_results.created_at)
                source_name = vehicle_results.source_name
                claim_state = vehicle_results.claim_state
                user_id = vehicle_results.user_id
                image_count = vehicle_results.image_count
                print("data==========",make, model,num_plate,created_at,claim_state,user_id,image_count)

                claim_state_dict = {"0" : "Initiated", "1" : "In Process", "2" : "Initial Assessment", "3" : "Completed", "4": "Updated", "5" : "Under Review", "6": "Failed", "7": "Closed", "8" : "Review Completed"}
                for key,val in  claim_state_dict.items():
                    if claim_state == key:
                        claim_state = val


                if claim_state == "Review Completed":
                    assessFinal_df = pd.DataFrame(columns=["action", "Part_name"])
                    parthistory_df = pd.DataFrame(columns=["action", "Part_name"])

                    carimage_results = db.session.query(insurance_carimage).filter(insurance_carimage.ref_num == ref_num).all()
                    if carimage_results:
                        
                        data_result = {}
                        get_name = {}
                        roi_image_list = []

                        for res in carimage_results:
                            data_result[res.picture] = res.side
                            get_name[res.name] = res.side
                            roi_image_list.append(res.name)

                        print("get_name================",get_name)


                        print("carimage data for review completed claim====================",data_result)
                
                        sides_list = []
                        for val in data_result.values():
                            if val in ('front', 'rear', 'left', 'right', 'frontLeft', 'frontRight', 'rearLeft', 'rearRight'):
                                sides_list.append(val)
                        sides_list = set(sides_list)
                        print("list of sides============", sides_list)
                        sides_count = len(sides_list)
                        print(sides_count)


                        claimsumindividual_results = db.session.query(claim_summary_individual).filter(claim_summary_individual.ref_num == ref_num).first()
                        if claimsumindividual_results:
                            relevant_images = claimsumindividual_results.roi
                            parts_identified = claimsumindividual_results.parts_identified

                        print("claim summary data=============",relevant_images,parts_identified )

                        assessFinalData = db.session.query(assess_final.action, insurance_part.full_name,assess_final.intensity).filter(assess_final.ref_num == ref_num, assess_final.part_id == insurance_part.id).all()
                        VehicleAssessPartHistoryData = db.session.query(vehicle_assessment_part_history.action, insurance_part.full_name,vehicle_assessment_part_history.intensity).filter(vehicle_assessment_part_history.ref_num == ref_num, vehicle_assessment_part_history.part_id == insurance_part.id).all()
                        print("*************VehicleAssessPartHistoryData*********", VehicleAssessPartHistoryData)
                        if assessFinalData:
                            for item in assessFinalData:
                                print(item)
                        assessFinal_df = pd.concat([assessFinal_df, pd.DataFrame(list(assessFinalData), columns=["action", "Part_name", "Intensity"])])
                        assessFinal_df = assessFinal_df.sort_values('action', ascending=False)
                        print("arranging alphabetwise final=======================",assessFinal_df)

                        assessFinal_df = assessFinal_df.drop_duplicates(subset=["Part_name"], keep = "first")
                        assessFinal_df = assessFinal_df.reset_index().drop("index", axis=1)
                        assessFinal_df["Part_name"] = assessFinal_df["Part_name"].str.lower()
                        assessFinal_df["action"] = assessFinal_df["action"].str.lower()

                        assessFinal_df = assessFinal_df[~assessFinal_df["Part_name"].isin(["rear", "text", "front", "rear number plate", "front number plate", "front logo", "rear logo"])]
                        assessFinal_df = assessFinal_df.reset_index().drop("index", axis=1)
                        print("assess_final df=======================",assessFinal_df)


                        if VehicleAssessPartHistoryData:
                            parthistory_df = pd.concat([parthistory_df, pd.DataFrame(list(VehicleAssessPartHistoryData), columns=["action", "Part_name", "Intensity"])])


                        if not parthistory_df.empty:
                            parthistory_df = parthistory_df.drop_duplicates(subset=["Part_name"], keep="last")
                            parthistory_df["Part_name"] = parthistory_df["Part_name"].str.lower()
                            parthistory_df["action"] = parthistory_df["action"].str.lower()

                            assessFinal_df = pd.concat([assessFinal_df, parthistory_df])
                            assessFinal_df = assessFinal_df.reset_index().drop("index", axis=1)
                            assessFinal_df = assessFinal_df.drop_duplicates(subset=["Part_name"], keep="last")
                            assessFinal_df = assessFinal_df.reset_index().drop("index", axis=1)

                            print("after merged and final with part hist =====================", assessFinal_df)


                        print("final=======================",assessFinal_df)
                        part_table = assessFinal_df.copy()
                        part_table.Intensity = part_table.Intensity.astype(int)
                        print("part_table==============",part_table)
                        part_table = part_table.sort_values('Intensity', ascending=False)
                        print("part_table after sorting ==============",part_table)
                        part_table = part_table.reset_index().drop("index", axis=1)

                        intensity_list = list(part_table["Intensity"])
                        partfullname_list = list(part_table["Part_name"])
                        action_list = list(part_table["action"])
                        print("actionnnnnnnnnnnnn",action_list)
                        print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",intensity_list)
                        print("partttttttttttttttttttttttttttttt",partfullname_list)

                        part_int_action_dict = {}
                        for ind, item in enumerate(partfullname_list):
                            part_int_action_dict[item] = intensity_list[ind]
                        print("part_int_action_dict==================", part_int_action_dict)

                        assessFinal_df.drop(assessFinal_df[ assessFinal_df['action'] == "no damage"].index, inplace=True)
                        print("after dropping no damage  =====================", assessFinal_df)

                        count_row = assessFinal_df.shape[0] 
                        print("count of damaged parts=====", count_row)


                        damage_results = db.session.query(insurance_damage.file_name, insurance_damage.picture).filter(insurance_damage.ref_num == ref_num).distinct()
                        if damage_results:
                            damaged_result = {}
                            damaged_image_list = []

                            for res in damage_results:
                                damaged_result[res.picture] = res.file_name
                                damaged_image_list.append(res.file_name)

                            print("carimage data for review completed claim====================",damaged_result)
                            print("damaged image list====================",damaged_image_list)

                        diff_list = (list(set(roi_image_list) - set(damaged_image_list)))
                        print("diff_list===============",diff_list)

                        partsIdenfied_in_parttable = db.session.query(insurance_part.full_name).filter(insurance_part.ref_num == ref_num).distinct()
                        print("*********************partsIdenfied_in_parttable******************", partsIdenfied_in_parttable)

                        parts_inparttable = []
                        for parts in partsIdenfied_in_parttable:
                            parts_inparttable.append(parts.full_name)
                        print("*********************partsIdenfied_in_parttable******************", parts_inparttable)

                        partfullname_list = [part.title() for part in partfullname_list]

                        print("**************************************", partfullname_list)

                        extraparts_list = list(set(parts_inparttable) - set(partfullname_list))
                        print("*********************************************************")
                        print("*********************************************************")
                        print("*********************************************************")
                        print("*********************************************************")
                        print("*********************************************************")
                        print(extraparts_list)

                        unwanted = ["Front","Rear","Left","Right","Front Logo","Rear Logo", "Front Number Plate", "Rear Number Plate", "Number Plate", "Logo", "Text"]

                        remaining_partlist = list(set(extraparts_list) - set(unwanted))

                        Remaining_parts_dict = {}

                        for ind,item in enumerate(remaining_partlist):
                            Remaining_parts_dict[item] = 0

                        print("Remaining_parts_dict=================",Remaining_parts_dict)


                        if not os.path.exists('/root/media_staging/html_page'):
                            os.makedirs('/root/media_staging/html_page')

                        for k,v in damaged_result.items():
                            print("k,v==========",k,v)
                            sidename_value = get_name[v]
                            damaged_result[k] = sidename_value

                        print("damaged_result after change==========",damaged_result)

                        roi_table = {}
                        roi_table.update(damaged_result)

                        print("************************", data_result)
                        print("************************", diff_list)

                        diff_list_dict = {}
                        for k,v in data_result.items():
                            k1 = k.split("/")[-1]
                            if k1 in diff_list:
                                diff_list_dict[k] = v

                        print("diff_list_dict==========",diff_list_dict)

                        roi_table.update(diff_list_dict)
                        print("roi_table ==========",roi_table)                            
                        
                        table_forming_dict = {}
                        table_forming_dict.update(part_int_action_dict)
                        table_forming_dict.update(Remaining_parts_dict)
                        print("table dict================", table_forming_dict)

                        try:
                            table_forming_dict.pop("front")
                        except:
                            pass

                        try:
                            table_forming_dict.pop("rear")
                        except:
                            pass

                        try:
                            table_forming_dict.pop("Front")
                        except:
                            pass

                        try:
                            table_forming_dict.pop("Rear")
                        except:
                            pass



                        table1 = dict(list(table_forming_dict.items())[len(table_forming_dict)//2:])
                        table2 = dict(list(table_forming_dict.items())[:len(table_forming_dict)//2])

                        print("table1===========", table1)
                        print("table2===========", table2)

                        sidename_correction_dict = {"front" : "Front", "rear": "Rear", "rearRight" : "Rear Right", "rearLeft" : "Rear Left", "frontRight" : "Front Right", "frontLeft" : "Front Left", "left" : "Left", "right" : "Right", "frontleft" : "Front Left", "frontright" : "Front Right", "rearleft" : "Rear Left", "rearright" : "Rear right"}
                        


                        bl_p_w = {"bonnet" : 8.50,"dickie" : 8.50,"front bumper":1.36, "rear bumper" :1.36,"left front door" :6.80, "right front door" : 6.80,"left rear door" : 6.80,"right rear door" :6.80,"left fender" :5.10,"right fender" :5.10,"left quarter panel" :5.10,"right quarter panel" :5.10,"grill" :1.36,"left head lamp" : 0.68,"right head lamp" :0.68,"left running board" :3.40,"right running board" :3.40,"left tail lamp" : 0.68,"right tail lamp" :0.68,"front windshield" :4.08,"rear windshield" :4.08,"left front window" :      2.72,"left rear window" :2.72,"right front window" :2.72,"right rear window" :2.72, "left mirror" : 0.68, "right mirror" : 0.68, "left fog lamp" : 0.68, "right fog lamp" :        0.68}

                        bl_i_s = {10: 40, 9: 40, 8: 30, 7:30, 6:30, 5:20, 4:20, 3:20, 2:10, 1: 10, 0: 0}

                        table_forming_dict = {k.lower() : v for k,v in table_forming_dict.items()}
                        print("table_forming_dict after lowercase============", table_forming_dict)

                        averageOfparts = []
                        for k,v in table_forming_dict.items():
                            if k in bl_p_w.keys() and v > 0:
                                averageOfparts.append((bl_i_s[table_forming_dict[k]] + bl_p_w[k])/2)

                        print("averageOfparts==========",averageOfparts)

                        total_average = 0
                        for items in range(0,len(averageOfparts)):
                            total_average = total_average + averageOfparts[items]

                        total_average = total_average / len(averageOfparts)

                        final_health_score = math.ceil(100 - total_average)

                        print("final_health_score=============", final_health_score)

                        print("diff_list===============",diff_list)
                        
                        q = 0
                        new_a = ''
                        for k,v in roi_table.items():
                            print("********* roi images ********", k)
                            q += 1
                            if q == 1:
                                new_a +="<tr>"
                            new_a +='<td><div style="width:image width px; text-align:center;"><img src = "'+k+'" alt="alternate text"  style="padding-bottom:0.5em; width:60%;  margin-top : 100px"/><p><span  style = "font-size : 20px;">'+ sidename_correction_dict[v] +'</span></p></div></td>'
                            if q == 2:
                                new_a += "</tr>"
                                q = 0


                        action_table = ''
                        for k,v in table1.items():
                            k = k.title()
                            if int(v) > 10:
                                v = 10
                            if int(v) >= 5:
                                action_table+='<tr class="table-active" style = "width:38%;background:none;"><td style = "text-align:left; padding : 4px;width: 100%; background:none;"><div style="-webkit-box-shadow: 3px 3px 3px 3px #ccc; -moz-box-shadow: 3px 3px 3px 3px #ccc; box-shadow: 3px 3px 3px 3px #ccc; position: relative; width: 98%; height: 45px; margin-bottom: 10px;"><div style="float:left; width:46%; padding-left:3%;margin-top:2%;margin-bottom:4%; font-size:16px;">'+k+'</div><div style="float:right; width:50%; padding:2%;"><div class="progress" style="position:relative;height:1.6rem;"><div style="font-size:12px;text-align:right;margin-top:2.5%;position: absolute;font-weight: bold;right: 10px;">Major damage</div><div class="progress-bar bg-danger" role="progressbar" style="width: '+str(v * 10)+'%" aria-valuenow="'+str(v)+'" aria-valuemin="0" aria-valuemax="10"></div></div></div></div></td></tr>'
                            if int(v) < 5 and int(v) > 0:
                                action_table+='<tr class="table-active" style = "width:38%;background:none;"><td style = "text-align:left; padding : 4px;width: 100%;background:none;"><div style="-webkit-box-shadow: 3px 3px 3px 3px #ccc; -moz-box-shadow: 3px 3px 3px 3px #ccc; box-shadow: 3px 3px 3px 3px #ccc; position: relative; width: 98%; height: 45px; margin-bottom: 10px;"><div style="float:left; width:46%; padding-left:3%;margin-top:2%;margin-bottom:4%; font-size:16px;">'+k+'</div><div style="float:right; width:50%; padding:2%;"><div class="progress" style="position:relative;height:1.6rem;"><div style="font-size:12px;text-align:right;margin-top:2.5%;position: absolute;font-weight: bold;right: 10px;">Minor damage</div><div class="progress-bar bg-warning" role="progressbar" style="width: '+str(v * 10)+'%" aria-valuenow="'+str(v)+'" aria-valuemin="0" aria-valuemax="10"></div></div></div></div></td></tr>'
                            if int(v) <= 0:
                                action_table+='<tr class="table-active" style = "width:38%;background:none;"><td style = "text-align:left; padding : 4px;width: 100%;background:none;"><div style="-webkit-box-shadow: 3px 3px 3px 3px #ccc; -moz-box-shadow: 3px 3px 3px 3px #ccc; box-shadow: 3px 3px 3px 3px #ccc; position: relative; width: 98%; height: 45px; margin-bottom: 10px;"><div style="float:left; width:46%; padding-left:3%;margin-top:2%;margin-bottom:4%; font-size:16px;">'+k+'</div><div style="float:right; width:50%; padding:2%;"><div class="progress" style="position:relative;height:1.6rem;"><div style="font-size:12px;text-align:right;margin-top:2.5%;position: absolute;font-weight: bold;right: 10px;">Good</div><div class="progress-bar bg-success" role="progressbar" style="width:100%" aria-valuenow="10" aria-valuemin="0" aria-valuemax="10"></div></div></div></div></td></tr>'

                        action_table2 = ''
                        for k,v in table2.items():
                            k = k.title()
                            if int(v) > 10:
                                v = 10
                            if int(v) >= 5:
                                action_table2+='<tr class="table-active" style = "width:38%;background:none;"><td style = "text-align:left; padding : 4px;width: 100%;background:none;"><div style="-webkit-box-shadow: 3px 3px 3px 3px #ccc; -moz-box-shadow: 3px 3px 3px 3px #ccc; box-shadow: 3px 3px 3px 3px #ccc; position: relative; width: 98%; height: 45px; margin-bottom: 10px;"><div style="float:left; width:46%;padding-left:3%; margin-top:2%;margin-bottom:4%; font-size:16px;">'+k+'</div><div style="float:right; width:50%; padding:2%;"><div class="progress" style="position:relative;height:1.6rem;"><div style="font-size:12px;text-align:right;margin-top:2.5%;position: absolute;font-weight: bold;right: 10px;">Major damage</div><div class="progress-bar bg-danger" role="progressbar" style="width: '+str(v * 10)+'%" aria-valuenow="'+str(v)+'" aria-valuemin="0" aria-valuemax="10"></div></div></div></div></td></tr>'
                            if int(v) < 5 and int(v) > 0:
                                action_table2+='<tr class="table-active" style = "width:38%;background:none;"><td style = "text-align:left; padding : 4px;width: 100%;background:none;"><div style="-webkit-box-shadow: 3px 3px 3px 3px #ccc; -moz-box-shadow: 3px 3px 3px 3px #ccc; box-shadow: 3px 3px 3px 3px #ccc; position: relative; width: 98%; height: 45px; margin-bottom: 10px;"><div style="float:left; width:46%; padding-left:3%;margin-top:2%;margin-bottom:4%; font-size:16px;">'+k+'</div><div style="float:right; width:50%; padding:2%;"><div class="progress" style="position:relative;height:1.6rem;"><div style="font-size:12px;text-align:right;margin-top:2.5%;position: absolute;font-weight: bold;right: 10px;">Minor damage</div><div class="progress-bar bg-warning" role="progressbar" style="width: '+str(v * 10)+'%" aria-valuenow="'+str(v)+'" aria-valuemin="0" aria-valuemax="10"></div></div></div></div></td></tr>'
                            if int(v) <=  0:
                                action_table2+='<tr class="table-active" style = "width:38%;background:none;"><td style = "text-align:left; padding : 4px;width: 100%;background:none;"><div style="-webkit-box-shadow: 3px 3px 3px 3px #ccc; -moz-box-shadow: 3px 3px 3px 3px #ccc; box-shadow: 3px 3px 3px 3px #ccc; position: relative; width: 98%; height: 45px; margin-bottom: 10px;"><div style="float:left; width:46%;padding-left:3%; margin-top:2%;margin-bottom:4%; font-size:16px;">'+k+'</div><div style="float:right; width:50%; padding:2%;"><div class="progress" style="position:relative;height:1.6rem;"><div style="font-size:12px;text-align:right;margin-top:2.5%;position: absolute;font-weight: bold;right: 10px;">Good</div><div class="progress-bar bg-success" role="progressbar" style="width:100%" aria-valuenow="10" aria-valuemin="0" aria-valuemax="10"></div></div></div></div></td></tr>'


                        frontimg = ''
                        if "front" in data_result.values():
                            for k,v in data_result.items():
                                if v == "front":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        elif "frontRight" in data_result.values():
                            for k,v in data_result.items():
                                if v == "frontRight":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        elif "frontLeft" in data_result.values():
                            for k,v in data_result.items():
                                if v == "frontLeft":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        elif "left" in data_result.values():
                            for k,v in data_result.items():
                                if v == "left":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        elif "right" in data_result.values():
                            for k,v in data_result.items():
                                if v == "right":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        elif "rear" in data_result.values():
                            for k,v in data_result.items():
                                if v == "rear":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        elif "rearLeft" in data_result.values():
                            for k,v in data_result.items():
                                if v == "rearLeft":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        elif "rearRight" in data_result.values():
                            for k,v in data_result.items():
                                if v == "rearRight":
                                    frontimg = '<td style="width:50%;height:100%;"><img src = "'+k+'"  width = "100%" height= "400px" style="margin-top:-16px;"/></td>'

                        f = open('/root/media_staging/html_page/helloworld.html','w')

                        message = """<html>
                        <head>
                        <link rel="stylesheet" href="/root/adda/demo_portal/adda_portal/adda_portal/static/css/bootstrap.min.css">
                        </link>
                        <link rel="stylesheet" href="/root/adda/demo_portal/adda_portal/adda_portal/static/css/reportpdf.css">
                        </link>
                        </head>
                        <body>
                        <table style="width : 96%; margin: 2%; border-bottom-style: solid;">
                            <tr>
                                <td>
                                    <img src = "/root/adda/hil_api/hil_api/hil_api/static/images/camcom_logo.png" height = "100px">
                                </td>
                                <td>
                                    <p style="margin-top : 70px; font-size : 12px;margin-left : 20px;">Camcom hi-tech AI platform, provides assessment for claims and break-in by just clicking pictures of the automobile. This self-inspection process is non-subjective and generates accurate, instant defect reports/quotes, ensuring hassle-free spot settlements and renewals.</p>
                                </td>
                            </tr>
                        </table>
                        <table style="width : 96%; margin: 2%; height:100px;">
                            <tr>    
                                <td style="width:50%;">
                                    <h4 style = "font-weight:bolder; font-size:1.2em">Inspection ID : <b>{ref_num}</b><h4>
                                </td>
                                <td style="width:25%;text-align: right" align="right">
                                    <h4 style="font-weight: bolder;margin-top:20px; font-size:1.2em">Health Score</h4>
                                </td>
                                <td style="width:10%;"><div class="set-size charts-container" style="transform: scale(0.7);"><div class="pie-wrapper progress-"""+str(final_health_score)+""" "style="margin-left:40px">
                                    <span class="label">"""+str(final_health_score)+"""<span class="smaller">%</span></span>
                                    <div class="pie">
                                      <div class="left-side half-circle"></div>
                                      <div class="right-side half-circle"></div>
                                    </div>
                                  </div></div>
                                </td>
                            </tr>
                        </table>
                        <table style = "width : 96%;margin: 0 auto; margin-top:2%;">
                            <tr>""" +frontimg+ """
                                <td>
                                    <table style = "width:100%;">
                                        <tr>
                                            <td>
                                                <div class="card bg-light mb-3" style="height : 200px; width : 100%; float : left; margin-bottom: 0 !important;">
                                                  <div class="card-body" style = "font-size: 12px; text-align : left;margin-left:6%;margin-top:8%;margin-bottom:6%;">
                                                    <p class="card-text">Make : <b>{make}</b></p>
                                                    <p class="card-text">Model : <b>{model}</b></p>
                                                    <p class="card-text">Registration No. : <b>{num_plate}</b></p>                                     
                                                  </div>                                        
                                                </div>
                                            </td>
                                            <td>
                                                <div class="card text-white bg-primary mb-3" style="height : 200px; width : 100%; float : right;margin-bottom: 0 !important;">
                                                  <div class="card-body" style = "font-size: 12px; text-align : left; margin-left:6%;margin-top:8%;margin-bottom:6%;">
                                                    <p class="card-text">Inspection ID : <b>{ref_num}</b></p>
                                                    <p class="card-text">Created on : <b>{created_at}</b></p>
                                                    <p class="card-text">Status : <b>{claim_state}</b></p>
                                                  </div>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <div class="card text-white bg-primary mb-3" style="height : 200px; width : 100%;float : left;">
                                                  <div class="card-body" style = "font-size: 12px; text-align : left;margin-left:6%;margin-top:8%;margin-bottom:6%;">
                                                    <p class="card-text">Uploaded Images : <b>{image_count}</b></p>
                                                    <p class="card-text">Relevant Images : <b>{relevant_images_count}</b></p>
                                                    <p class="card-text">Sides Identified : <b>{sides_count}</b></p>                                     
                                                </div>
                                            </td>
                                            <td >
                                                <div class="card bg-light mb-3" style="height : 200px; width : 100%; float : right;">
                                                  <div class="card-body" style = "font-size: 12px; text-align : left; margin-left:6%;margin-top:8%;margin-bottom:6%;">
                                                    <p class="card-text">Parts Identified : <b>{parts_identified}</b></p>
                                                    <p class="card-text">Parts Not Identified : <b>{parts_not_identified}</b></p>
                                                    <p class="card-text">Damaged Parts : <b>{damaged_parts}</b></p>                                     
                                                  </div>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </td>            
                            </tr>    
                        </table>
                        
                        <table class="table" style="margin-left:2%;margin-right:2%; width: 96%;border-collapse: collapse;background:#eee;">
                            <tr>
                                <td><h4 style = "font-weight : bolder; border-bottom-style: solid; padding-bottom:0.5em; "> <b>Vehicle Assessment</b></h4></td>        
                            </tr>
                            <table style = "width : 40%; float: right; margin :2%;border-collapse: collapse;">
                              <thead>
                                <tr>
                                  <th scope="col" style="margin : 1%;font-size:18px;"><p style="width:50%;float:left;text-align:left;padding-left:3%">Part Name</p> <p style="width:50%;float:right;text-align:right;padding-right:3%">Health</p></th>                               
                                </tr>
                              </thead>
                              <tbody>"""+ action_table+"""
                                
                              </tbody>
                            </table>
                            <table style = "width : 40%; float: left; margin :2%; border-collapse: collapse;">
                              <thead>
                                <tr>
                                  <th scope="col" style="margin : 1%;font-size:18px;"><p style="width:50%;float:left;text-align:left;padding-left:3%">Part Name</p> <p style="width:50%;float:right;text-align:right;padding-right:3%">Health</p></th>                                  
                                </tr>
                              </thead>
                              <tbody>"""+ action_table2+"""
                                
                              </tbody>
                            </table>
                        </table>
                        <table class="damdetc1" style = "margin-top : 1500px; width: 96%;margin:2%;">
                            <tr style="border-bottom-style: solid;">
                                <th style="font-size: x-large; text-align : left;"><h4 style = "font-weight:bolder;"><b>Vehicle Exterior Images</b></h4></th>
                            </tr>""" + new_a + """
                        </table>
                        <table style = "width: 96%; margin:2%;">
                            <tr><div style = "margin-left: 45%; margin-top: 4%"><button type="button" class="btn btn-primary btn-sm"><b>Disclaimer</b></button></div></tr>
                            <tr><p style = "text-align: center; margin-top: 20px;font-size:14px;">This Evalution Report Is Based on Computer Vision Solution by Camcom.ai</p></tr>
                        </table>
                        <hr size="30">
                        </body>
                        </html>"""

                        
                        new_message = message.format(ref_num = ref_num, created_at = created_at, claim_state = claim_state, image_count = image_count, relevant_images_count = relevant_images, sides_count= sides_count , parts_identified = parts_identified, parts_not_identified = 29 - int(parts_identified), damaged_parts = count_row, make = make.title(), model = model.title(), num_plate = num_plate )
                        f.write(new_message)
                        f.close()

                        
                        import pdfkit 
                        pdfkit.from_file('/root/media_staging/html_page/helloworld.html', '/root/media_staging/output.pdf') 


                        if os.path.exists("/root/media_staging/html_page"):
                            shutil.rmtree("/root/media_staging/html_page")


            else:
                return jsonify({"Message" : "No such claim_id found in database"})



        else:
            return jsonify({"Message" : "Enter valid ref_num"})


    except Exception as e:
        logger.debug("\n------- Something went wrong -------\n")
        logger.exception(str(e))
        return {"Error" : str(e)}