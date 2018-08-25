# segmentor

Morfessor 2.0 (Creutz 2002) employs an unsupervised probablistic Minimum Description Length (MDL) algorithm
(Creutz and Lagos 2002) for the induction the morphology of natural language. The recursive MDL method splits 
a corpus into segments (morphs). Segmentor is a tool for correcting incorrect Morfessor splits. It accomplishes 
this in an unsupervised fashion first by building lexicons of prefixes (p), stems (s), and suffixes (e) seeds, 
and then by iterating through the text and mapping words to morphological signature labels.

For instance,

```
un known → p-s (prefix-stem)
pre heat ing → p-s-e (prefix-stem-suffix)
sun tan → s-s (stem-stem)
```

Creutz and Lagos (2002) estimate accuracy for Finnish at around 49.6% (all correct splits),
with 20.6% incorrect splits (one or more errors) and 29.7% incomplete splits (no errors but missing splits). 
Segmentor addresses the issue of incorrect splits by shifting a *suspicious* morpheme boundary (leftward or rightward) 
until an already occurring morph can be matched and a wellformed signature can be assigned. For instance, 
if Morfessor outputs *un believa ble* (p-s-e) or *s un set* (p-p-s) and the morphs *able* and *sun* have already been seen, 
then the output would be corrected to *un belieb able* (p-s-e) and *sun set* (s-s). 

Segmentor also contains tools for tokenization of a text into Morfessor ready input, visualization of the splits, 
analysis of the distribution of the splits (statistics),  and classes encapsulating morphological information, 
which can be used for the machine translation (MT) of subword units.
