import sys
reload(sys)
sys.setdefaultencoding('utf8')

import mwclient as mw
from cassandra.cluster import Cluster

import redis

def store_rosettacode_cassandra():
    site = mw.Site('rosettacode.org', path='/mw/')
    cluster = Cluster(['127.0.0.1'])  # localhost
    session = cluster.connect()  # default key space
    session.set_keyspace('rosettacode')

    for page in site.Pages['Category:Programming Tasks']:
        print page.page_title
        iwlinks = set([el[1] for el in page.iwlinks()])
        categories = set([el.page_title for el in page.categories()])
        session.execute("INSERT INTO rosettacode (page_title, categories, iwlinks, text) VALUES (%s, %s, %s, %s)", [page.page_title, categories, iwlinks, page.text()])

store_rosettacode_cassandra()

def store_label_redis():
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    labelfile = open('labelfile.txt')
    for line in labelfile:
        (task_name, algo_name, is_algo) = line.split('\t')
        if is_algo == 'y':
            rd.sadd('rosettacode-label-isalgo', task_name)
        rd.hset('rosettacode-label-algoname', task_name, algo_name)