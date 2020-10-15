import requests, json, re
from requests.auth import HTTPBasicAuth
# import datetime
from fuzzywuzzy import fuzz 



class find_make_model:


    make_model_config = json.load(open('adda_api/utility/vehicle_config.json'))   #make & model dictionary
    
    
    
    
    
    def get_clean_string(string): #to remove special characters from the string and make it lowercase
        
        string = re.sub('[^A-Za-z0-9 ]+', '', str(string))
        string = string[:len(string)].lower()
        
        
        return string
    
    
    
    
    
    def get_same_score_keys(val,score_dict): #used to find the list of dictionary keys which have same score
        keys = {}
        for key, value in score_dict.items(): 
             if val == value: 
                 keys[key] = value  
        return keys    
        
    
    
    
    
    def get_close_match(model,possibilities): #from the same score possible models find the closest matching string.
        result = {}
        model = find_make_model.get_clean_string(model)
        for key, entry in possibilities.items():
            key = find_make_model.get_clean_string(key)
            result[key] = fuzz.ratio(model,key)
        
        if result:
            max_score_key = max(result, key=result.get)
        return max_score_key    
    
    
    
    
    
    def get_details_from_regcheck(lp):  #to get the result from RegCheckOrg service
        
        url = f'https://www.carregistrationapi.com/api/camcom.aspx/vehicle/{lp}'
        username = 'camcomap'
        password = 'Gifto0709$'
        
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    
    
    
    
    
    def get_make(asis_make): #to find the make
        
        makes = find_make_model.make_model_config['makes']
        score_dict = {}
        result = {}
        for key,make in makes.items():
            score = fuzz.partial_ratio(find_make_model.get_clean_string(asis_make),find_make_model.get_clean_string(key))
            if score > 80:
                score_dict[key] = score
        if score_dict:    
            max_score_key = max(score_dict, key=score_dict.get)
            result['make'] = makes[max_score_key]
        
        
        return result
    
    
    
        
        
    def get_model(make, asis_model):  #to find the model
        models = find_make_model.make_model_config['models'][make]
        score_dict = {}
        result = {}
        for key, model in models.items():
            score = fuzz.partial_ratio(find_make_model.get_clean_string(asis_model),find_make_model.get_clean_string(key))

            if score > 65:
                score_dict[key] = score
        if score_dict:
            max_score_key = max(score_dict, key=score_dict.get)
            max_score_dict = find_make_model.get_same_score_keys(score_dict[max_score_key],score_dict)
            if len(max_score_dict) == 1:
                result['model'] = models[max_score_key]
            elif len(max_score_dict) > 1:
                max_score_key = find_make_model.get_close_match(asis_model,max_score_dict)
                result['model'] = models[max_score_key]
        
        return result
    
    
    
    
    
    def get_make_model_details(lp): #to get the final result to be used for ADDA
        result = {}
        # vehicle_type_list = [ 'lmv', 'lpv']
        vehicle_type_list =  [ 'Agricultural Tractor(LMV)',
                                 'L.M.V. (CAR)(LMV)',
                                 'Luxury Cab(LPV)',
                                 'Maxi Cab(LPV)',
                                 'Motor Cab(LPV)',
                                 'Motor Car(LMV)',
                                 'OMNI BUS(LMV)',
                                 'Omni Bus (Private Use)(LMV)',
                                 'Omni Bus(LMV)',
                                 'Private Service Vehicle (Individual Use)(LMV)',
                                 'Private Service Vehicle(LMV)']
        result['regcheck_res'] = find_make_model.get_details_from_regcheck(lp)
        
        
        # lp = {"Fuel": "PETROL", "Credits": "4063", "Location": "FEROZEPUR ZIRKHA, Haryana", "Engine No": "HA10AGKHD****5", "PUCC Upto": "", "RC Status": "ACTIVE", "Chassis No": "MBLHAW09XKHE****4", "Model Name": "SPLENDOR", "Owner Name": "MOIN KHAN", "MV Tax upto": "LTT", "Maker / Model": "HERO MOTOCORP LTD/SPLENDOR", "Vehicle Class": "M", "Emission norms": "BHARAT STAGE IV", "Insurance Upto": "", "Fitness/REGN Upto": "", "Manufacturer Name": "HERO MOTOCORP LTD", "Registration Date": "28-Jun-2019", "Registration Number": "HR28J3910", "Registering Authority": "FEROZEPUR ZIRKHA, Haryana"}
        # result['regcheck_res'] = lp
        
        result['make_logic'] = False
        result['model_logic'] = False
        result['service'] = False
        result['car'] = False
        result['make'] = None
        result['model'] = None
        
        
        if len(result['regcheck_res']) < 15:
            
            return result
        
        else :
            
            # for vehicle_type in vehicle_type_list:
            #     vehicle_type_score = fuzz.partial_ratio(find_make_model.get_clean_string(vehicle_type), find_make_model.get_clean_string(result['regcheck_res']['Vehicle Class']))
            #     if vehicle_type_score == 100:
            #         result['car'] = True
            if result['regcheck_res']['Vehicle Class'] in vehicle_type_list:
                result['car'] = True
                    
            if result['car']:
            
                if result['regcheck_res']['Maker / Model']:
                    # asis_make_model = result['regcheck_res']['Maker / Model'].split('/')
                    # asis_make = asis_make_model[0].strip()
                    # asis_model = (' '.join(map(str,asis_make_model[1:]))).strip()
                    
                    
                    asis_make_model = result['regcheck_res']['Maker / Model']
                    asis_make = asis_make_model
                    asis_model = asis_make_model
                    
                
                '''
                
                Don't delete this, it can be used in future for VIN & Registration
                
                
                if result['regcheck_res']['Registration Date']:
                    registration_year = datetime.datetime.strptime(result['Registration Date'],'%d-%b-%Y').strftime('%Y')
                    result['registration_year'] = registration_year
                if result['regcheck_res']['Chassis No']:
                    vin = result['Chassis No'].strip()
                    result['vin'] = vin
                    
                '''
                
                
                make_result = find_make_model.get_make(asis_make)
                
                if make_result:
                    make = make_result['make']
                    result['make_logic'] = True
                    
                    model_result = find_make_model.get_model(make,asis_model)
                    if model_result:
                        model = model_result['model']
                        result['model_logic'] = True
                        
                    else:
                        model = asis_model.title()
                    
                    
                    
                else:
                    make = asis_make.title()
                    model = asis_model.title()
            
            
                result['make'] = make
                result['model'] = model
                result['service'] = True
            
       
        return result
