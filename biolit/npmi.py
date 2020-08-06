from math import log, sqrt, isclose
from biolit.esquery import termcounts

def npmi(total, x, y, xy):
    px = x / total
    py = y / total
    pxy = xy / total
    pmi = log(pxy / (px * py))
    return pmi / (-1 * log(pxy))


def tscore(total, x, y, xy):
    return (xy - (x * y / (total * total))) / sqrt(xy)


def zscore(total, x, y, xy):
    return (xy - (x * y / (total * total))) / sqrt(x * y / (total * total))


def lmi(total, x, y, xy):
    return xy * log(total * xy / (x * y))


def scores(a, b, index='pubmed', x=None):
    ndocs = 30676436 if index == 'pubmed' else 2741994

    xy = termcounts("(%s) AND (%s)" % (a, b))
    if isclose(xy, 0, abs_tol=1e-10):
        return None
    if x is None:
        x = termcounts(a)
    y = termcounts(b)
    r = [npmi(ndocs, x, y, xy), tscore(ndocs, x, y, xy),
         zscore(ndocs, x, y, xy), lmi(ndocs, x, y, xy)]
    return r

def test_scores():
    import numpy as np
    np.testing.assert_array_almost_equal(scores('cough', 'sars'),
                                         [0.22611963521065218, 11.575836879626198,
                                          258774.55192848947,
                                          373.93770052987713]
                                         )
    np.testing.assert_array_almost_equal(scores('cough', 'mers'),
                                         [0.17274359060591227, 6.633249559550599,
                                          117443.66889940212,
                                          102.26625990274695]
                                         )
