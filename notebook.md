# Searching and visualising the Roal Society Corpus

> In this notebook, we use [`corpkit`](https://www.github.com/interrogator/corpkit)'s API to search the RSC, to edit search results, and to visualise what we find.

## Setup

Below, we import the `corpkit` module and instantiate our corpus:

```python
%matplotlib inline
from corkit import *
corpus = Corpus('rsc-annual-parsed')
```

It can then be searched using the `interrogate()` method:

```python
# this is the default search: count words in each subcorpus
lexicon = corpus.interrogate(W, ANY, show=W)
```

## Filtering data

The issue, however, is that this searches every sentence in the corpus, which includes non-English, bad OCR, and so on. So, we might like to instantiate the corpus while setting a filter on the `engprob` metadata, which used `langdetect` to assign a probability that each text was English. Most often, it assigned a probability of `1.0` to English documents, so we can use that:

```python
filt = {'engprob': '^1'}
corpus = Corpus('rsc-annual-parsed', just=filt)
```

There is still a lot of messy data, however. If we concordance a subcorpus, we can see the problem:

```python
# get just function matching root
conc = corpus[10].concordance(F, 'root')
conc
```

## Adding annotations through searching

To deal with this problem, we might like to add a metadata tag to the sentences in the corpus whose root lemma is a verb. Annotation requires that we switch `conc` to `True`.

> This tagging has in fact already been done! It's shown here for educational purposes.

```python
from corpkit.dictionaries.verblist import allverbs
v_root = corpus.interrogate({F: 'root', L: allverbs}, conc=True)
# add a new tag called verb_root
corpus.annotate(v_root, 'verb_root')
```

To protect the data a little, you need to turn off `dry_run` to actually annotate the corpus:

```python
corpus.annotate(v_root, 'verb_root', dry_run=False)
```

Adding a tag is nice, but we might like to actually add the verb itself as a metadata field that we can use as a filter. To do that, we pass in a dict, with the metadata field as the key, and 'm' (i.e. middle concordance column) as the value.

```python
corpus.annotate(v_root, {'verb_root': 'm'})
```

So, with this metadata added, we can create a second filter:
```python
corpus.just['tags'] = 'verb_root'
# or, reinstantiate
# filt = {'engprob': '^1', 'tags': 'verb_root'}
# corpus = Corpus('rsc-annual-parsed', just=filt)
```

Alright. Now we have a corpus and some useful filters in place. Let's get searching!

## General features

`corpkit` has a very simple method for counting a number of frequencies (words, clauses, process types, etc.) and storing everything within a single DataFrame:

```python
# this can take a very long time!
feat = corpus.features
feat
```

We can also get some general counts for POS tags and word classes:

```python
pos = corpus.postags
wc = corpus.wordclasses
wc
```

> `corpkit` will save these calculations to file so that they are available next time without rerunning the search.

## Deriving statistics

We can use these general frequencies to calculate interesting stuff:

```python
import pandas as pd
derived = {'Characters per word': feat['Characters'] / feat['Words'],
           'Words per sentence': feat['Words'] / feat['Sentences'],
           'Words per clause': feat['Words'] / feat['Clauses'],
           'Clauses per sentence': feat['Clauses'] / feat['Sentences'],
           'Open class per closed class': feat['Open class words'] / feat['Closed class words'],
           'Passive per clause': feat['Passives'] / feat['Clauses']}
df = pd.DataFrame(derived)
df
```

## Visualising results

`corpkit` has a `visualise()` method. You could also use Pandas` `plot()` method, which is similar.

```python
plt = df.visualise()
plt.show()
```

This isn't too helpful---we can't see much change within each statistic. So, let's use subplots:

```python
plt = df.visualise(x_label='Year', subplots=True, layout=(2,3))
plt.tight_layout()
plt.show()
```

Better!

## Participants and processes

We can use the dependency annotations to approximate a distinction between participants and processes.

```python
# thing is the head of the participant group
part = corpus.interrogate({F: roles.thing}, show=L)
```

```python
# event is the head of the process group (the predicator)
# make sure the process is a verb!
proc = corpus.interrogate({F: roles.event, L: allverbs}, show=L)
```

`corpkit` can calculate relative frequencies, and sort results based on their trajectory:

```python
rel_part_i = part.edit('%', SELF, sort_by='increase', keep_stats=True)
rel_proc_i = proc.edit('%', SELF, sort_by='increase', keep_stats=True)
rel_part_d = part.edit('%', SELF, sort_by='decrease', keep_stats=True)
rel_proc_d = proc.edit('%', SELF, sort_by='decrease', keep_stats=True)
rel_proc_i.results
```

### Multiplotting

There is a `multiplot` method, which shows both subplots and overall frequencies. To use it, we select a layout, which corresponds to the number of subplots to show.

```python
plt = rel_part_i.multiplot(layout=9)
plt.tight_layout()
plt.show()
```

For greater control over the plots, we can pass in two dictionaries, corresponding to the main plot and the subplots:

```python
d1 = {'stacked': False, 'x_label': 'Year', y_label='Percentage of all results'}
plt = rel_part_i.multiplot(d1, {'grid': False}, layout=9)
plt.tight_layout()
plt.show()
```

Finally, it's possible to pass in different data for the main and the subplots. Below, we show keyness vs. relative frequency

```python
keyness = part.edit(K, SELF)
plt = keyness.multiplot({}, {'data': rel_part_i})
plt.tight_layout()
plt.show()
```

So, let's plot our participants and processes, increasing and decreasing:

```python
to_plot = [(rel_part_i, 'increasing', 'Participants'),
           (rel_proc_i, 'increasing', 'Processes'),
           (rel_part_d, 'decreasing', 'Participants'),
           (rel_proc_d, 'decreasing', 'Processes')]
for data, direction, name in to_plot:
    ylab = 'Percentage of all %s' % name
    title = '%s, %s' % (name, direction)
    plt = to_plot.multiplot({title=title, x_label='year', y_label=ylab}, layout=9)
    plt.tight_layout()
    plt.show()
```

### Searching for feature pairs

So far, each time we've searched the corpus, we've just outputted a single value, such as the lemma form, the word class or the POS tag. We can get multiple values at the same time, however:

```python
# get wordclass and dependency role
# pos is messy because of mistakes in NN/NNP annotation
wc_fnc = corpus.interrogate(show=[X, F])
inc = wc_fnc.edit('%', SELF, sort_by='increase')
dec = wc_fnc.edit('%', SELF, sort_by='decrease')
```

```python
plt = inc.visualise(subplots=True, layout=(2, 3))
plt.show()
```

```python
plt = dec.visualise(subplots=True, layout=(2, 3))
plt.show()
```