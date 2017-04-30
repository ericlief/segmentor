#!/usr/bin/env bash

DATA_SOURCE="Europarl.raw.en.gz"
TRAIN_CORPUS="training-data-ep.en"
MORFESSOR_MODEL="morfessor-model.en.bin"

# Download DATA
wget -O 'Europarl.raw.en.gz' 'http://opus.lingfil.uu.se/download.php?f=Europarl/mono/Europarl.raw.en.gz'

# tokenizer.py:
chmod u+x tokenizer.py

# reconstruct-sentences.py:
chmod u+x reconstruct-sentences.py

# training-data-ep-%.gz: $(DATA_SOURCE)
#	gunzip -ckv $(TRAIN_CORPUS-$*) | ./tokenizer.py "$<" > "$@"
#DATA_SOURCE='Europarl.raw.en.gz'
#TRAIN_CORPUS='training-data-ep.en.gz'
gunzip -ckv $DATA_SOURCE | python3 tokenizer.py > $TRAIN_CORPUS
gzip -f $TRAIN_CORPUS
TRAIN_CORPUS+=".gz"
echo $TRAIN_CORPUS

#morfessor-model-%.bin: $(DATA_SOURCE)
ulimit -t unlimited && nice -n 19 morfessor -t $TRAIN_CORPUS -s $MORFESSOR_MODEL -x  "lexicon.en" --logfile "morfessor-train-log.en"

# Run Morfessor on the input, save a mapping from words to segments.
#segments.%: $(MORFESSOR_MODEL)-%.bin $(DATA_SOURCE)

#TODO strip all punctuation and uninteresting words from the input.
#gunzip -ckv $(TRAIN_CORPUS-$*) | sed -e 's/ /\n/g' | sort -u | nice -n 19 morfessor -l "$<" -T - --logfile "morfessor-predict-$*-log.txt" > "$@"
ulimit -t unlimited && gunzip -ckv $TRAIN_CORPUS | sed -e 's/ /\n/g' | sort -u | nice -n 19 morfessor -l $MORFESSOR_MODEL -T - --logfile "morfessor-predict-log.en" > "segments-ep.en"

#output-segmented-ep.%: segments-ep.% $(DATA_SOURCE)
#output-segmented-ep-%.txt: segments-ep-%.txt training-data-ep-%.gz
gunzip -ckv $TRAIN_CORPUS | ./reconstruct-sentences.py < "segments-ep.en" > "output-segmented-ep.en"

