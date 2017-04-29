#!/usr/bin/env bash


# Download DATA
wget -O "$@" 'http://opus.lingfil.uu.se/download.php?f=Europarl/mono/Europarl.raw.en.gz'

# tokenizer.py:
chmod u+x tokenizer.py

# reconstruct-sentences.py:
chmod u+x reconstruct-sentences.py

# training-data-ep-%.gz: $(DATA_SOURCE)
#	gunzip -ckv $(TRAIN_CORPUS-$*) | ./tokenizer.py "$<" > "$@"
DATA_SOURCE='Europarl.raw.en.gz'
TRAIN_CORPUS='training-data-ep.en.gz'
gunzip -ckv $(DATA_SOURCE) | ./tokenizer.py > $(TRAIN_CORPUS)

