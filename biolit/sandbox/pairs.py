from biolit.esquery import termcounts
from biolit.npmi import scores
from biolit.sandbox.terms import read_terms, term_esquery
import json

def pairs(terms1, rnode1, terms2, rnode2, index='pmc'):
    r = list()
    for i in terms1[rnode1]['children'].union({rnode1}):
        cname = terms1[i]['name']
        cq = term_esquery(terms1, i)
        xpm = termcounts(cq, index=index)
        for j in terms2[rnode2]['children'].union({rnode2}):
            dname = terms2[j]['name']
            dq = term_esquery(terms2, j)
            s = scores(cq, dq, index=index, x=xpm)
            if s is not None:
                r.append({
                    'pair': (i, j),
                    'name': (cname, dname),
                    'score': s
                })
    return r

def test_do_pairs():
    do = read_terms("../../../ontrepository/doid.obo")
    assert len(do['DOID:874']['children']) == 6   # bacterial pneumonia
    assert len(do['DOID:8469']['children']) == 2  # influenza
    assert len(do['DOID:0060519']['children']) == 5  # beta-lactam allergy
    r = pairs(do, 'DOID:874', do, 'DOID:8469', index='pubmed')
    print(json.dumps(r, indent=4))
    assert len(r) == 11
    r = pairs(do, 'DOID:874', do, 'DOID:8469')
    print(json.dumps(r, indent=4))
    assert len(r) == 11
    r = pairs(do, 'DOID:874', do, 'DOID:0060519', index='pubmed')
    assert len(r) == 4
    r = pairs(do, 'DOID:874', do, 'DOID:0060519')
    assert len(r) == 4

def test_do_concepts_with_many_children():
    do = read_terms("../../../ontrepository/doid.obo")
    # drug allergy, respiratory system disease
    r = pairs(do, 'DOID:0060500', do, 'DOID:1579')
    assert len(r) == 180
