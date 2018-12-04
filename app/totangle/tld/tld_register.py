# coding=utf-8
from app.totangle.get_info.get_info import seed_storage
from iota import *
from random import SystemRandom
from pprint import pprint
import json
import os
import hashlib
import time


def generate_new_seed():
    alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    generator = SystemRandom()
    seed = str(u''.join(generator.choice(alphabet) for _ in range(81)))

    print("Generate the seed for this TLD Name.")
    print("Seed : " + str(seed))

    return seed

# IOTA API config 
def IOTA_config(seed):
    global api
    url = 'http://node.deviceproof.org:14266'
    api = Iota(url,seed)

def IOTA_config_noseed():
    global api
    url = 'http://node.deviceproof.org:14266'
    api = Iota(url)

def generate_new_address():
    address =  api.get_new_addresses(index=0,checksum=True)[u'addresses'][0]

    print("Generate the address for this TLD Name.")

    return  address

def send_transfer(tld_name,tld_address,message):

    print("Upload the TLD content to Tangle .....")

    return api.send_transfer(
        depth = 3,
        transfers = [
            ProposedTransaction(
                address = Address(tld_address),
                value = 0,
                tag = Tag("ALP"+tld_name.upper()),
                message = TryteString.from_string(message)
            )
        ],
        min_weight_magnitude = 14
    )

def create_owner_auth(seed):
    auth = hashlib.sha256()
    auth.update(seed.encode('utf-8'))
    key = auth.hexdigest()

    print("Generate the certificate for this TLD Name.")
    print("Auth Code : " + key)

    return key

def create_tld_content(tld_name,admin_name,admin_email,admin_phone,key):
    tld_content = "{\
        \"TLD_Content\": {\n\
        \"TLD_Info\": {\n\
        \"Index\":0,\n\
        \"TLD Name\":"+"\""+tld_name+"\""+",\n\
        \"Admin Name\":"+"\""+admin_name+"\""+",\n\
        \"Admin Email\":"+"\""+admin_email+"\""+",\n\
        \"Admin Phone\":"+"\""+str(admin_phone)+"\""+",\n\
        \"Creation Date\":"+"\""+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\""+"\n\
        },\n\
        \"Domain_list\":{ \n\
        },\n\
        \"Signature\":{\n\
        \"Auth\":"+"\""+key+"\"\n\
        }\n}\n}"
    
    print("Prepare the TLD content for upload to Tangle.")
    print("TLD content : ")
    pprint(tld_content)

    return tld_content

def check_tld_exist(tld_name):

    print("Check if the TLD name is exist:")
    print("TLD name : " + str(tld_name))

    IOTA_config_noseed()
    _tld_name = "ALP"+tld_name.upper()
    search_tags_result = api.find_transactions(tags=[_tld_name])
    if search_tags_result[u'hashes'] == []:
        return False
    else:
        return True

def generate_tld_content(tld_name,message,seed):
    IOTA_config(seed)
    tld_address = generate_new_address()
    send_transfer(tld_name,tld_address,message)
    seed_storage(tld_name,seed)

    print("Upload success !!")
    print("Your TLD content is storage at this address on Tangle : ")
    print(str(tld_address))

    return([str(seed),str(tld_address)])
