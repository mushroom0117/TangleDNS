from pprint import pprint
from iota import *
import json

def IOTA_config():
    global api
    url = 'https://node1.puyuma.org:443'
    api = Iota(url)

def seed_storage(tld_name,seed):
    seed_file = open('./app/totangle/storage/seed', 'a+')
    seed_file.write(str({tld_name:seed})+"\n")
    seed_file.close

def get_seed(tld_name):
    seed_file = open('./app/totangle/storage/seed')
    for seed in seed_file:
        seedline = seed.split("\n")[0].replace("'", '"')
        seeddict = json.loads(seedline)
        if tld_name in seeddict:
            return seeddict.get(tld_name)
