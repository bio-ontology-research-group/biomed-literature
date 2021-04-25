#!/usr/bin/env python
import gzip
import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from elasticsearch.helpers import streaming_bulk
from nosqlbiosets.pubmed.index_pubmed_articles import IndexPubMedArticles
from nosqlbiosets.pubmed.query import QueryPubMed

es = Elasticsearch('http://borgdb.cbrc.kaust.edu.sa:9200/', timeout=440)
dir_ = os.path.dirname(os.path.abspath(__file__))

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

def index_pairs(infile):
    if infile.endswith(".gz"):
        inf = gzip.open(infile, 'rt')
    else:
        inf = open(infile, 'r')
    r = json.load(inf)
    return es_index_pairs(r)

def test_index_pairs():
    r = "../data/do-cpairs.json"
    index_pairs(r)

DATA="/data/referencedbs/"

def read_uniprotidmapping(infile=DATA+"HUMAN_9606_idmapping.dat"):
    r = dict()
    for line in open(infile):
        a = line.split('\t')
        if len(a) != 3:
            print("Line has more or less than 3 fields: %s" % line)
            exit(-1)
        if a[1] == 'GI' or a[1] == 'GeneID':
            gid = int(a[2])
            if gid not in r:
                r[gid] = set()
            r[gid].add(a[0])
    return r

def test_read_uniprotidmapping():
    c = read_uniprotidmapping()
    assert len(c) == 894201
    assert 672 in c  # BRCA1

def read_pubtator(infile=DATA + "mutation2pubtatorcentral",
                  genes=False):
    r = [dict(),dict()] if genes else dict()
    for line in open(infile):
        a = line.split('\t')
        if len(a) != 5:
            print("Line has more or less than 5 fields: %s" % line)
            exit(-1)
        pmid = int(a[0])
        if genes:
            if pmid not in r[0]:
                r[0][pmid] = set()
                r[1][pmid] = set()
            if len(a[3]) > 0:
                r[0][pmid].update(a[3].split('|'))
            for i in a[2].split(';'):
                if i != 'None' and len(i) > 0:
                    r[1][pmid].add(int(i))
        else:
            if pmid not in r:
                r[pmid] = set()
            r[pmid].update(a[2].split('|'))
    return r

class IndexPubMedArticlesR(IndexPubMedArticles):

    def __init__(self, db, index, **kwargs):
        esindxcfg = {  # Elasticsearch index configuration
            "index.number_of_replicas": 0,
            "index.number_of_shards": 5}
        super(IndexPubMedArticles, self).__init__(db, index,
                                                  es_indexsettings=esindxcfg,
                                                  **kwargs)
        self.qry = QueryPubMed(db, index, **kwargs)
        self.variantreferences = read_pubtator()
        self.genereferences, self.gids = \
            read_pubtator(DATA + "gene2pubtatorcentral", True)
        self.uniprot = read_uniprotidmapping()

    def es_index(self, articles):
        def annotatearticle(r):
            if r['_id'] in self.variantreferences:
                r['variants'] = list(self.variantreferences[r['_id']])
            if r['_id'] in self.genereferences:
                r['genes'] = list(self.genereferences[r['_id']])
                r['geneids'] = list(self.gids[r['_id']])
                r_ = [self.uniprot[gid]
                      for gid in self.gids[r['_id']]
                      if gid in self.uniprot
                      ]
                r__ = list()
                for i in r_:
                    for j in i:
                        r__.append(j)
                r['uniprotids'] = r__
            _id = str(r['_id'])

        def preparearticles():
            for r in articles:
                if 'references' in r:
                    del r['references']
                annotatearticle(r)
                yield r
        for ok, result in parallel_bulk(
                self.es, preparearticles(),
                thread_count=14, queue_size=1400,
                index=self.index, chunk_size=140
        ):
            if not ok:
                action, result = result.popitem()
                doc_id = '/%s/commits/%s' % (self.index, result['_id'])
                print('Failed to %s document %s: %r' % (action, doc_id, 'result'))


def index_pubmed(infile, index, db="Elasticsearch", host='localhost', port=9200,
                 recreateindex=False):
    dbc = IndexPubMedArticlesR(db, index,
                               mdbcollection="Elasticsearch only for now",
                               host=host, port=port,
                               recreateindex=recreateindex)
    dbc.read_and_index_articles(infile)
    dbc.close()

if __name__ == '__main__':
    import argh
    argh.dispatch_commands([
        index_pubmed, index_pairs
    ])
