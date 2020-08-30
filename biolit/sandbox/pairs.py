import json

from biolit.esindex import es_index_pairs
from biolit.esquery import termcounts
from biolit.npmi import scores
from biolit.sandbox.terms import read_terms, term_esquery


def pairs(terms1, rnode1, terms2, rnode2, index='pmc', max_children=1400):
    r = list()
    for i in terms1[rnode1]['children'].union({rnode1}):
        if len(terms1[i]['children']) > max_children:
            continue
        cname = terms1[i]['name']
        cq = term_esquery(terms1, i)
        xpm = termcounts(cq, index=index)
        for j in terms2[rnode2]['children'].union({rnode2}):
            if len(terms2[j]['children']) > max_children:
                continue
            dname = terms2[j]['name']
            dq = term_esquery(terms2, j)
            s = scores(cq, dq, index=index, x=xpm)
            if s is not None:
                x, y, xy, npmi, ts, zs, lmi = s
                r.append({
                    'concept1': i,
                    'concept2': j,
                    'name1': cname,
                    'name2': dname,
                    'npmi': npmi,
                    'tscore': ts,
                    'zscore': zs,
                    'lmi': lmi,
                    'x': x,
                    'y': y,
                    'xy': xy
                })
    return r

def cpairs(ontology1, root1, ontology2, root2, index='pmc', max_children=1400):
    terms1 = read_terms(ontology1)
    terms2 = read_terms(ontology2)
    return pairs(terms1, root1, terms2, root2, index=index,
                 max_children=max_children)

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

def test_do_concepts_with_many_children():  # ~16m, 8m with MAX_CHILDREN 1400
    do = read_terms("../../../ontrepository/doid.obo")
    # drug allergy, respiratory system disease
    r = pairs(do, 'DOID:0060500', do, 'DOID:1579', max_children=14)
    es_index_pairs(r)
    assert len(r) == 52

def test_concept_pairs_with_two_ontology():
    from biolit.esindex import es_index_pairs
    do = "../../../ontrepository/doid.obo"
    chebi = "../../../ontrepository/chebi_lite.obo"
    # homopolymer, respiratory system disease
    # 10 mc, 16m, 5 pairs;  30 mc, 14m, 8 pairs; 140 mc, 52m, 26 pairs
    r = cpairs(chebi, 'CHEBI:60029', do, 'DOID:1579', max_children=140)
    print(json.dumps(r, indent=4))
    print(json.dump(r, open("../../data/do-chebi-pairs.json", "w"), indent=4))
    es_index_pairs(r)
    assert len(r) == 26

def get_cytoscape_graph(pairs_, name=None):
    import networkx as nx
    graph = nx.DiGraph(name=name)
    for i in pairs_:
        u = i['concept1']
        v = i['concept2']
        graph.add_node(u, type=u.split(':')[0],
                       shared_name=i['name1'],
                       label=i['name1'],
                       viz_color='lightgreen')
        graph.add_node(v, type=v.split(':')[0],
                       name=i['name2'],
                       label=i['name2'],
                       viz_color='honeydew')
        graph.add_edge(u, v, npmi=i['npmi'], name='test')
    return graph

def view_withcytoscape(inf):
    from py2cytoscape.data.cyrest_client import CyRestClient
    from py2cytoscape.data.style import Style
    crcl = CyRestClient()
    r = json.load(open(inf))
    g = get_cytoscape_graph(r, name=inf)
    cyn = crcl.network.create_from_networkx(g)
    crcl.layout.apply('kamada-kawai', network=cyn)
    crcl.style.apply(Style('default'), network=cyn)

def test_cyview_pairs():
    inf = "../../data/do-chebi-pairs.json"
    view_withcytoscape(inf)
