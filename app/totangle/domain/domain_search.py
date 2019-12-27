from iota import *
import json
import requests

def get_tld_content(tld_name):
    IOTA_config()
    tld_name = "ALP"+tld_name.upper()

    print("Get the TAG for this TLD name.")

    hashes_list = api.find_transactions(tags=[tld_name])

    print("Get the Transaction Hash List for this TLD name.")
    print(hashes_list)

    count = 0
    trytes_length = []
    trytes_list = []
    if hashes_list['hashes']:
        for n in hashes_list['hashes']:

            print("Get the TLD name Trytes from Tangle")

            tld_content_trytes = api.get_trytes(hashes_list['hashes'])['trytes'][count]

            print(tld_content_trytes)

            trytes_length.append(len(str(tld_content_trytes).split('999')[0]))
            trytes_list.append(tld_content_trytes)
            count+=1
        latest = trytes_length.index(max(trytes_length))

        print("Get the currect Transaction Hash for this TLD name.")
        print(hashes_list['hashes'][latest])

        tld_content_string = Transaction.from_tryte_string(trytes_list[latest]).signature_message_fragment.decode('ignore')

        print("Convert the content from Trytes to String.")
        print(tld_content_string)

        tld_content_dict = json.loads(tld_content_string)
        tld_content_hash = hashes_list['hashes'][latest]
        return [tld_content_dict,tld_content_hash]
    else:

        return "Not Found !"

def IOTA_config():
    global api
    url = 'https://node1.puyuma.org:443'
    api = Iota(url)

def get_domain_root(tld_name,domain_name):
    tld_content_dict = get_tld_content(tld_name)
    if tld_content_dict == "Not Found !":
        return "Not Found"
    else:
        if tld_content_dict[0]['TLD_Content']['Domain_list'][domain_name]:
            mam_root = tld_content_dict[0]['TLD_Content']['Domain_list'][domain_name]
            return mam_root
        else:
            return "Not Found"

def get_domain_content(domain_root):
    data = domain_root
    headers = {'Content-Type': 'text/plain'}
    domain_content = requests.post("http://localhost:3000/search", data=data, headers=headers)
    return domain_content.text

def find_domain(url):
    IOTA_config()
    tld_name = url.split('.')[-1]
    domain_name = url.split('.')[-2]
    domain_root = get_domain_root(tld_name, domain_name)
    domian_content = get_domain_content(domain_root)
    return [domian_content,domain_root]
