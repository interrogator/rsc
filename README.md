# Royal Society Corpus: parsing and interrogating

This directory/repository is a [`corpkit`](https://www.github.com/interrogator/corpkit) project, which contains a parsed version of the Royal Society Corpus (`data/rsc-annual-parsed.tar.gz`), and some figures (`images/`) created during preliminary investigation.

## The Corpus

The parsed RSC was created with [Stanford CoreNLP](http://stanfordnlp.github.io/CoreNLP/) and `corpkit`. The data from `v1.19` was unzipped, and fed to `convert_xml_to_corpkit.py`. Coreference resolution was not performed, copula was treated as `root` where possible, and *collapsed, CC-processed dependencies* are used.

The corpus has annual subfolders. Each folder contains files in a [`CONLL-U`](http://universaldependencies.org/format.html)-like format, with filenames the same as in the original bundle, plus the `.conll` extension. All original metadata is preserved, plus `engprob`, which gives a probability that a file contains English text, and `lang`, which gives the most likely language. Some sentences also have `tags=root_verb` as metadata, indicating that the `root` lemma was found in VerbNet.

## Preliminary investigation

The first attempt to extract information from the corpus is documented in a Jupyter Notebook [here](https://github.com/interrogator/rsc/blob/master/notebook.ipynb).

## Using `corpkit` to explore the corpus

`corpkit` is an API, interpreter and GUI for corpus linguistic research, written in Python. Documentation for the API and interpreter are [here](http://corpkit.readthedocs.io). Documentation for the GUI is [here](http://interrogator.github.io/corpkit/).

If you want to use `corpkit` to explore the data, you need to have Python (2.7 or 3.x) and `pip`. Then, you can install it with:

```bash
$ pip install corpkit
```

Once `corpkit` is installed, `cd` into this directory. You can then choose how you'd like to use the tool:

1. GUI: `python -m corpkit.gui`
2. API: `python` or `ipython`; `from corpkit import *`
3. Interpreter: `corpkit`

The sections below show how a basic workflow might look using the API or the interpreter. Head to [ReadTheDocs](http://corpkit.readthedocs.io/en/latest/) for more detailed examples.

### API Example

Import module:

```python
>>> from corpkit import *
>>> from corpkit.dictionaries import *
```

Model corpus and set up filters:

```python
>>> filt = {'engprob': '^1', 'tags': 'root_verb'}
>>> corpus = Corpus('rsc-annual-parsed', just=filt)
```

Get lemma forms of grammatical participants:

```python
>>> query = {F: roles.participant, GF: roles.process}
### conc=True turns on concordancing, which can be slow
>>> part = corpus.interrogate(query, show=L, conc=True)
```

Make relative frequencies and sort: 

```python
>>> rel = part.edit('%', SELF, sort_by='increase', keep_stats=True)
```

Visualise some results:

```python
>>> rel.visualise(kind='line', subplots=True, layout=(3,3)).show()
```

View concordance:

```python
>>> res.concordance
```

### Interpreter example

Setting and searching the corpus:

```bash
> set rsc-annual-parsed as corpus
> search corpus for function matching roles.participant and \
... governor-function matching roles.process \
... showing lemma
```

Editing, sorting and visualising the result:

```bash
> calculate result as percentage of self
> sort edited by increase
> plot edited as line chart with subplots and layout as (3,3)
```

Please report any issues via GitHub. `corpkit` errors should go to the [corpkit repo](https://www.github.com/interrogator/corpkit), and RSC-related things to the [RSC repo](https://www.github.com/interrogator/rsc).
