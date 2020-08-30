from pronto import *
from biolit.esquery import escapereserved
'''
Term stanzas constitute the nodes in an ontology graph.
Formally a Term stanza is equivalent to a Class declaration in OWL.
https://owlcollab.github.io/oboformat/doc/GO.format.obo-1_4.html
'''

MAX_CHILDREN = 180000

def read_terms(ontfile):
    o = Ontology(ontfile)
    terms = dict()
    for term_ in o.terms():
        c = set([t.id for t in term_.subclasses() if t.id != term_.id])
        if term_.obsolete or len(c) > MAX_CHILDREN:
            continue
        trm = {
            '_id': term_.id,
            'name': term_.name,
            # 'definition': term_.definition,
            'alt_ids': [a for a in term_.alternate_ids],
            'synonyms': [s.description for s in term_.synonyms],
            'leaf': term_.is_leaf(),
            'isa': set([t.id for t in term_.superclasses()]),
            'children': c
        }
        terms[term_.id] = trm
    return terms

def term_esquery(terms, tid):
    q = [escapereserved(terms[tid]['name'])]
    for i in terms[tid]['children']:
        q.append(escapereserved(terms[i]['name']))
        for a in ['alt_ids', 'synonyms']:
            for trm in terms[i][a]:
                q.append(escapereserved(trm))
    q = "\"" + "\" OR \"".join(q) + "\""
    return q

def test_term_esquery():  # ~4s
    terms = read_terms("../../../ontrepository/doid.obo")
    r = term_esquery(terms, 'DOID:0060519')
    assert '"beta-lactam allergy"' in r
    assert '"amoxicillin allergy"' in r
    assert '"penicillin G allergy"' in r

def test_do():  # ~4s
    terms = read_terms("../../../ontrepository/doid.obo")
    assert len(terms) == 10194  # 12639
    leafs = {i['name'] for i in terms.values() if i['leaf']}
    assert len(leafs) == 7963  # 10408
    assert "anaerobic pneumonia" in leafs
    assert "bacterial pneumonia" not in leafs  # DOID:874
    assert "DOID:874" in terms['DOID:873']['isa']
    assert "DOID:0050204" in terms['DOID:1884']['children']

def test_chebi():
    # ~22s,  chebi-lite ~10s   when isa/children attributes not calculated
    # ~1m30s,  when isa/children attributes are calculated
    r = read_terms("../../../ontrepository/chebi_lite.obo")
    assert len(r) == 125748  # 125808
