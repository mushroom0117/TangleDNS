from random import SystemRandom
from app.totangle.tld.tld_search import get_tld_content
from iota import *
import json
import os
import hashlib
import time

def IOTA_config(tld_owner_seed):
    global api
    global seed
    url = 'http://node.deviceproof.org:14266'
    seed = tld_owner_seed
    api = Iota(url,seed)

def generate_new_address(index):
    address =  api.get_new_addresses(index=index,checksum=True)[u'addresses'][0]

    print("Generate the new address for this TLD Name.")

    return  address

def send_transfer(tld_name,tld_address,tld_content):

    print("Upload the TLD content to Tangle .....")

    tld_content = json.dumps(tld_content)
    return api.send_transfer(
        depth = 3,
        transfers = [
            ProposedTransaction(
                address = Address(tld_address),
                value = 0,
                tag = Tag("ALP"+tld_name.upper()),
                message = TryteString.from_string(str(tld_content))
            )
        ],
        min_weight_magnitude = 14
    )

def modify_tld_content(tld_name):
    tld_address = generate_new_address()
    send_transfer(tld_name,tld_address)

def check_tld_owner(seed,tld_name):
    IOTA_config(seed)
    auth = hashlib.sha256()
    auth.update(seed.encode('utf-8'))
    key = auth.hexdigest()

    print("Get the certificate for this TLD name.")

    tld_content = get_tld_content(tld_name)[0]
    auth_code = tld_content['TLD_Content']['Signature']['Auth']

    print("Auth Code : " + str(auth_code))
    print("Check the auth Code is correct or not.")

    if key == auth_code:

        print("Correct !!")

        return True
    else:

        print("Uncorrect !!")

        return False

def tld_modify_run(seed,tld_name,new_domain,tld_content):
    IOTA_config(seed)
    new_index = tld_content['TLD_Content']['TLD_Info']['Index'] + 1
    tld_address = generate_new_address(new_index)
    tld_content['TLD_Content']['TLD_Info']['Index'] += 1
    tld_content['TLD_Content']['Domain_list'] = new_domain
    tld_content['TLD_Content']['TLD_Info']['Updated Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    send_transfer(tld_name,tld_address,tld_content)
    return tld_address