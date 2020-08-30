from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

es = Elasticsearch('http://borgdb.cbrc.kaust.edu.sa:9200/', timeout=440)

def termcounts(terms, index='pubmed', default_field="abstract"):
    query = {
        "query": {
            "query_string": {
                "default_field": default_field,
                "query": terms
            }
        }
    }
    r = es.count(index=index, body=query)['count']
    return r

def escapereserved(query):
    r = query.replace('"', '\\"')
    return r

def test_termcounts():
    tests = [("cough", 36089, 52272, 5906, 35010),
             ("sars", 6992, 8895, 962, 6356),
             ("mers", 3660, 4062, 1035, 8344),
             ("cough AND sars", 134, 142, 10, 462),
             ("cough AND mers", 44, 46, 15, 240)]
    for q, n, m, i, j in tests:
        assert termcounts(q) == n
        assert termcounts(q, default_field='*') == m
        assert termcounts(q, index='pmc') == i
        assert termcounts(q, index='pmc', default_field='*') == j
