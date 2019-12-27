from iota import *
from app.totangle.get_info.get_info import get_seed
from app.totangle.tld.tld_search import get_tld_content
from app.totangle.domain.domain_search import find_domain
import json
import requests
import shutil
import time
import hashlib

def IOTA_config(tld_owner_seed):
    global api
    url = 'https://node1.puyuma.org:443'
    seed = tld_owner_seed
    api = Iota(url,seed)

def IOTA_config_non_seed():
    global api
    url = 'https://node1.puyuma.org:443'
    api = Iota(url)
            
def generate_new_address():
    address =  api.get_new_addresses(index=index+1,checksum=True)[u'addresses'][0]
    return  address

def send_to_mam(domain_json,start_count,domain_seed):

    domain_json = json.dumps(domain_json)

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

def modify_domain_content(domain_content,new_index,answer_section):
    domain_content['Domain_Info']['Index'] = str(new_index)
    domain_content['Domain_Info']['Updated Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    domain_content['AnswerSection'] = answer_section
    print(domain_content)
    return domain_content

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

def check_domain_owner(seed,url):
    IOTA_config_non_seed()
    auth = hashlib.sha256()
    auth.update(seed.encode('utf-8'))
    key = auth.hexdigest()
    domain_content = find_domain(url)[0]
    domain_content = json.loads(domain_content)
    auth_code = domain_content['Signature']['Auth']
    print(auth_code)
    if key == auth_code:
        return True
    else:
        return False

def domain_update_to_tangle(url,domain_json,start_count,domain_seed):#,tld_owner_seed):
    new_root_address = send_to_mam(domain_json,start_count,domain_seed)
    return new_root_address