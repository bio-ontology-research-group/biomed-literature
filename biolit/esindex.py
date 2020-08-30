from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import json
import gzip

es = Elasticsearch('http://borgdb.cbrc.kaust.edu.sa:9200/', timeout=440)

def read_pairs(pairs):
    for pair in pairs:
        pair["_id"] = pair['concept1']+pair['concept2']
        yield pair

def es_index_pairs(pairs, index='pairs'):
    r = 0
    for ok, result in streaming_bulk(
            es,
            read_pairs(pairs),
            index=index,
            chunk_size=256
    ):
        action, result = result.popitem()
        if not ok:
            print('Failed to %s document: %r' % (action, result))
        else:
            r += 1
    return r

def es_index_pairsfile(infile):
    if infile.endswith(".gz"):
        inf = gzip.open(infile, 'rt')
    else:
        inf = open(infile, 'r')
    r = json.load(inf)
    return es_index_pairs(r)

def test_index_pairs():
    r = "../data/do-cpairs.json"
    es_index_pairsfile(r)
