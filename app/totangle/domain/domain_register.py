from iota import *
from app.totangle.get_info.get_info import get_seed
from app.totangle.tld.tld_search import get_tld_content
from random import SystemRandom
import hashlib
import json
import requests
import shutil
import time

def IOTA_config(tld_owner_seed):
    global api
    url = 'http://node.deviceproof.org:14266'
    seed = tld_owner_seed
    api = Iota(url,seed)

def IOTA_config_non_seed():
    global api
    url = 'http://node.deviceproof.org:14266'
    api = Iota(url)

def generate_new_seed():
    alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    generator = SystemRandom()
    seed = str(u''.join(generator.choice(alphabet) for _ in range(81)))

    print("Generate the seed for this TLD Name.")
    print("Seed : " + str(seed))

    return seed
            
def generate_new_address():
    address =  api.get_new_addresses(index=index+1,checksum=True)[u'addresses'][0]
    return  address

def get_tld_content_dict(tld_name):
    tld_content_dict = get_tld_content(tld_name)[0]
    global index
    index = tld_content_dict['TLD_Content']['TLD_Info']['Index']
    return tld_content_dict

def send_to_mam(domain_json,domain_seed):
    start_count = 0
    headers_json = {'Content-Type': 'application/json'}
    headers_text = {'Content-Type': 'text/plain'}
    mam_seed = requests.post("http://localhost:3000/seed1", data=domain_seed, headers=headers_text)
    print(mam_seed.text)
    mam_index = requests.post("http://localhost:3000/index", data=str(start_count), headers=headers_text)
    print(mam_index.text)
    mam_root = requests.post("http://localhost:3000/update", data=domain_json, headers=headers_json)
    print(mam_root.text)
    return mam_root.text

def send_transfer(tld_name,tld_address,tld_added_dict):
    #The json file is jsut for demo use
    tld_added_json = json.dumps(tld_added_dict)
    return api.send_transfer(
        depth = 3,
        transfers = [
            ProposedTransaction(
                address = Address(tld_address),
                value = 0,
                tag = Tag("ALP"+tld_name.upper()),
                message = TryteString.from_string(tld_added_json)
            )
        ],
        min_weight_magnitude = 14
    )

def modify_tld_content(tld_name,tld_content_dict,domain_name,new_domain_root):
    tld_address = generate_new_address()
    tld_content_dict['TLD_Content']['TLD_Info']['Index'] += 1
    tld_content_dict['TLD_Content']['Domain_list'][domain_name] = new_domain_root 
    tld_content_dict['TLD_Content']['TLD_Info']['Updated Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    send_transfer(tld_name,tld_address,tld_content_dict)
    return tld_address

def check_domain_exist(url):
    IOTA_config_non_seed()
    tld_name = url.split('.')[-1]
    domain_name = url.split('.')[-2]
    search_tags_result = get_tld_content(tld_name)
    if search_tags_result == "Not Found !":
        return "tld_not_found"
    else:
        if domain_name in search_tags_result[0]['TLD_Content']['Domain_list']:
            return "domain_exist"
        else:
            return "domain_available"

def create_owner_auth(seed):
    auth = hashlib.sha256()
    auth.update(seed.encode('utf-8'))
    key = auth.hexdigest()
    return key

def create_domain_content(admin_email,admin_phone,key):
    domain_content = "{\n\"Domain_Info\": {\n\"Index\":"+"\""+"0"+"\""+",\n\"Creation Date\":"+"\""+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\""+",\n\"Admin Email\":"+"\""+admin_email+"\""+",\n\"Admin Phone\":"+"\""+str(admin_phone)+"\"\n},\n\"AnswerSection\":[{ \n}],\n\"Signature\":{\n\"Auth\":"+"\""+key+"\"\n}}"
    return domain_content

def domain_register_to_tangle(url,domain_json,domain_seed):#,tld_owner_seed):
    tld_name = url.split('.')[-1]
    domain_name = url.split('.')[-2]
    tld_owner_seed = get_seed(tld_name)
    IOTA_config(tld_owner_seed)
    tld_content_dict = get_tld_content_dict(tld_name)
    root_info = send_to_mam(domain_json,domain_seed)
    mam_address = root_info
    new_address = modify_tld_content(tld_name,tld_content_dict,domain_name,mam_address)
    return([str(domain_seed),str(mam_address),str(new_address)])