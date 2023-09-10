import azure.functions as func
import os
import json
from azure.storage.blob import BlobClient
from requests.auth import HTTPBasicAuth
import requests
import logging


def get_work_item_details(parent_work_item_id, pat_token, organization_name, project_name):
    username = "Mohamed Zain"  # Replace with your username
    auth = HTTPBasicAuth(username, pat_token)
    headers = {
        "Accept": "application/json"
    }
    url = f'https://dev.azure.com/{organization_name}/{project_name}/_apis/wit/workitems/{parent_work_item_id}?api-version=7.0&$expand=all'
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        work_item = response.json()
        return work_item
    return None



def get_work_item_state(child_work_item_id, pat_token, organization_name, project_name):
    username = "Mohamed Zain"  # Replace with your username
    auth = HTTPBasicAuth(username, pat_token)
    headers = {
        "Accept": "application/json"
    }
    url = f'https://dev.azure.com/{organization_name}/{project_name}/_apis/wit/workitems/{child_work_item_id}?api-version=7.0'
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        work_item = response.json()
        return work_item["fields"]["System.State"]
    return None



def update_work_item_state(parent_work_item_id, new_state, pat_token, organization_name, project_name):
    username = "Mohamed Zain" # Replace with your username
    auth = HTTPBasicAuth(username, pat_token)
    headers = {
       "Content-Type": "application/json-patch+json"
    }
    url = f'https://dev.azure.com/{organization_name}/{project_name}/_apis/wit/workitems/{parent_work_item_id}?api-version=7.0'
    data = [
        {
            'op': 'add',
            'path': '/fields/System.State',
            'value': new_state
        }
    ]
    response = requests.patch(url, json=data, headers=headers, auth=auth)
    return response.status_code




def Process_Webhook(req: func.HttpRequest) -> dict:
    try:
        req_body = req.get_json()
        organization_name = req_body['resourceContainers']['collection']['baseUrl'].split('/')[3]
        project_name = req_body['resourceContainers']['project']['id']
        pat_token = os.environ["pattoken"]
        
        work_item_id = req_body["resource"]["workItemId"]
        work_item_state = req_body["resource"]["fields"]["System.State"]
        work_item_type = get_work_item_type(work_item_id, pat_token, organization_name, project_name)
        relations = req_body["resource"]["revision"]["relations"]
        work_item = {
            "work item ID": work_item_id,
            "State": work_item_state['newValue'],
            "Type": work_item_type,
            "Parent": {},
            "Children": [],
        }
        logging.info("zain_1")
        for relation in relations:
            logging.info("zain_2")
            if relation["attributes"]["name"] == "Parent":
                logging.info("test1")
                if work_item["Type"] != "Epic":
                    logging.info("test2")
                    parent_id = relation.get("url").split("/")[-1]
                    parent_state = get_work_item_state(parent_id, pat_token, organization_name, project_name)
                    work_item["Parent"] = {
                    "ID": parent_id,
                    "State": parent_state,
                    }
                else:
                    work_item["Parent"] = {
                    "ID": None,
                    "State": None
                    }     
                logging.info(f"parent work item object is : {work_item['Parent']}")
                logging.info(f"work item object is : {work_item}")
            elif relation["attributes"]["name"] == "Child":
                child_id = relation.get("url").split("/")[-1]
                work_item["Children"].append(child_id)
        
        return work_item
    except ValueError:
        return func.HttpResponse("Invalid JSON data.", status_code=400)

    
    
    
    
    
    
def Fetch_Rules_From_Json_File():
    sas_token = os.environ.get("SAS_TOKEN", "")
    logging.info(f"sas_takoen is : {sas_token}")
    blob_url = os.environ.get("BLOB_URL", "")
    logging.info(f"blob url is : {blob_url}")
   # Get the mounted file share's name from environment variables
    storage_account_name = os.environ["STORAGE_ACCOUNT_NAME"]
    logging.info(f"storage_account_name is : {storage_account_name}")
    storage_account_key = os.environ["STORAGE_ACCOUNT_KEY"]
    logging.info(f"storage_account_key is : {storage_account_key}")
    # Get the connection string from your Azure Function's application settings
    connection_string = os.environ["AzureWebJobsStorage1"]
    logging.info(f"connectionstring is :{connection_string}")
    
    blob_client = BlobClient.from_blob_url(blob_url + "?" + sas_token)
    blob_data = blob_client.download_blob()
    file_contents = blob_data.readall()
    config = json.loads(file_contents)
    logging.info(f"config is : {config}")
    rules = config.get("rules", [])
    logging.info(f"rules:{rules}")
    
    
    return rules







def Matching_Rule(work_item, rules):
    logging.info("welcame zain in matching rule")
    work_item_state = work_item["State"]
    logging.info(f"work item state is : {work_item_state}")
    
    for rule in rules:
        logging.info("welcame in for loop")
        if rule["ifChildState"] == work_item_state:
            return rule
    
    return None


def change_parent_state(rule, parent_work_item_id, pat_token, organization_name, project_name):
    # Extract the required data from the rule
    all_children_completed = rule["allChildren"]
    new_parent_state = rule["setParentStateTo"]
    if_completed_state = os.environ["ifcompletedstate"]
    logging.info(if_completed_state)
    
    parent_work_item_details = get_work_item_details(parent_work_item_id, pat_token, organization_name, project_name)
    # Fetch all child work items and their states
    child_work_item_relations = parent_work_item_details.get("relations", [])
    all_children_in_same_state = True
    
    for relation in child_work_item_relations:
        if relation["attributes"]["name"] == "Child" and relation.get("url"):
            child_work_item_id = int(relation["url"].split("/")[-1])
            child_state = get_work_item_state(child_work_item_id, os.environ["pattoken"], organization_name, project_name)
            if child_state != if_completed_state:
                all_children_in_same_state = False
                break
    
    if all_children_completed == all_children_in_same_state:
        response_code = update_work_item_state(parent_work_item_id, new_parent_state, pat_token, organization_name, project_name)
        logging.info(f"Update Response Code: {response_code}")
        return func.HttpResponse(f"Parent work item updated to {rule['setParentStateTo']}.")  
    else:
        return None
    
    
    
    
    
    
    
def get_work_item_type(work_item_id, pat_token, organization_name, project_name):
    username = "YourUsername"  # Replace with your username
    auth = HTTPBasicAuth(username, pat_token)
    headers = {
        "Accept": "application/json"
    }
    url = f'https://dev.azure.com/{organization_name}/{project_name}/_apis/wit/workitems/{work_item_id}?api-version=7.0'
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        work_item = response.json()
        return work_item["fields"]["System.WorkItemType"]
    return None







def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Function started.")

    try:
               #---------------------------section1-------------------------------#
        logging.info("hi zain")       
        req_body = req.get_json()
        
        # Log the request body
        logging.info('Received request content:')
        logging.info(req.get_body().decode('utf-8'))
        logging.info("zain is free")
        new_state = req_body["resource"]["fields"]["System.State"]
        logging.info(f"New State: {new_state['newValue']}")
        organization_name = req_body['resourceContainers']['collection']['baseUrl'].split('/')[3]
        logging.info(f"organization_name:{organization_name}")
        project_name = req_body['resourceContainers']['project']['id']
        logging.info(f"project:{project_name}")
        pat_token = os.environ["pattoken"]
        logging.info(f"Paresonal Access Token:{pat_token}")
        
        # Get the mounted file share's name from environment variables
        storage_account_name = os.environ["STORAGE_ACCOUNT_NAME"]
        logging.info(f"storage_account_name is : {storage_account_name}")
        storage_account_key = os.environ["STORAGE_ACCOUNT_KEY"]
        logging.info(f"storage_account_key is : {storage_account_key}")
        # Get the connection string from your Azure Function's application settings
        connection_string = os.environ["AzureWebJobsStorage1"]
        logging.info(f"connectionstring is :{connection_string}")
        
        
        #------------------------section2-------------------------#
         # Call Process_Webhook to get the work_item dictionary
        work_item = Process_Webhook(req)
        # Fetch the work item type using get_work_item_type function
        # Now you can use the work_item dictionary in the main function
        logging.info(f"Received work item: {work_item}")
        
        work_item_type = work_item["Type"]
        logging.info(f"work item type is : {work_item_type}")
        # Get the parent ID from the generated work item
        
        
        #------------------------section3--------------------------#
        
        rules = Fetch_Rules_From_Json_File()   # Fetch the rules from the rule.json file in the file share
        logging.info(f"rules are :{rules}")
        matching_rule = Matching_Rule(work_item, rules)   # Find the matching rule for the work item
        logging.info(f"matching_rule is {matching_rule}")
        not_parent_states = matching_rule.get("notParentStates", [])
        logging.info(f"not_parent_states is :{not_parent_states}")
        
        
        #--------------------------section4-------------------------#
        if work_item_type != "Epic":
            parent_id = work_item["Parent"]["ID"]
            logging.info(f"my parent id is : {parent_id}")
            parent_state = get_work_item_state(parent_id, pat_token, organization_name, project_name)
            logging.info(f"Parent work item state: {parent_state}")
            if parent_state not in not_parent_states:
                change_parent_state_result = change_parent_state(matching_rule, parent_id, os.environ["pattoken"], organization_name, project_name)
                logging.info(f"Update Response Code: {change_parent_state_result}")
                
                
        
        return func.HttpResponse("No action taken.")     
    
    
    
    
    
    
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
    
    
    
    
    