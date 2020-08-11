

- Incubation project for concept associations in biomedical literature
- Concepts will be collected from biomedical ontologies


### Example command line

```bash

python setup.py install

biolit findpairs data/chebi_lite.obo CHEBI:83630 data/doid.obo DOID:874

```

### Literature indexes

PMC and PubMed articles were indexed with using the scripts of the [`nosql-biosets`](
https://bitbucket.org/hspsdb/nosql-biosets/src/master/nosqlbiosets/pubmed/) project

For development, we use a non public Elasticsearch server for PMC and PubMed queries.
If you index PMC and PubMed articles in your Elasticsearch server update the
Elasticsearch URL in `biolit/esquery.py` file to point the queries to your server.
