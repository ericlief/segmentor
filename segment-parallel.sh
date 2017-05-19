#!/usr/bin/env bash

echo "Enter language abbreviation"
read lang
echo "Enter abbreviated name of corpus"
read corpus
echo "Enter paralell corpus languages separated by a dash"
read paral

unzip "/var/tmp/${corpus}-${paral}.txt.zip" -d /var/tmp

if [[ $corpus == "ep" ]];
then
    DATA_SOURCE="/var/tmp/Europarl.${paral}.${lang}"
	#DATA_SOURCE="Europarl.raw.${lang}.gz"
    URL="http://opus.lingfil.uu.se/download.php?f=Europarl/mono/Europarl.raw.${lang}.gz"
elif [[ $corpus == "dgt" ]]; then
	#DATA_SOURCE="DGT.raw.${lang}.gz"
    DATA_SOURCE="/var/tmp/DGT.${paral}.${lang}"
	URL="http://opus.lingfil.uu.se/download.php?f=DGT/mono/DGT.raw.{lang}.gz"
elif [[ $corpus == "os" ]]; then
    #DATA_SOURCE="/tmp/OpenSubtitles2016.raw.${lang}.gz"
	DATA_SOURCE="/var/tmp/OpenSubtitles2016.${paral}.${lang}"
    URL="http://opus.lingfil.uu.se/download.php?f=OpenSubtitles2016/mono/OpenSubtitles2016.raw.{lang}.gz"
else
    echo "Corpus not found!"
fi


MORFESSOR_MODEL="morfessor-model-${corpus}.${lang}.bin"
#TRAIN_CORPUS="/tmp/training-data-${corpus}.${lang}.gz"
TRAIN_CORPUS="/var/tmp/training-data-${corpus}.${paral}.${lang}"
LEXICON="lexicon-${corpus}.${paral}.${lang}.txt"
PREDICT_LOG="morfessor-predict-${corpus}.${paral}.${lang}.log.txt"
TRAIN_LOG="morfessor-train-${corpus}.${paral}.${lang}.log"
SEGMENT_OUTPUT="segments-${corpus}.${paral}.${lang}.txt"
RECONSTRUCTED_SENTS="output-segmented-${corpus}.${paral}.${lang}.txt"

# Download DATA
#wget -O $DATA_SOURCE $URL
#wget -O- $URL > dev/null 2>&1 | python3 tokenizer.py > $TRAIN_CORPUS

# tokenizer.py:
chmod u+x tokenizer.py

# reconstruct-sentences.py:
chmod u+x reconstruct-sentences.py

# training-data-ep-%.gz: $(DATA_SOURCE)
#if [[ $DATA_SOURCE == *"tar.gz"* ]];
#then
#    tar -xOzf $DATA_SOURCE | python3 tokenizer.py > $TRAIN_CORPUS
    #wget -O- $URL > dev/null 2>&1 | python3 tokenizer.py > $TRAIN_CORPUS#
#else
#    gunzip -ckv $DATA_SOURCE | python3 tokenizer.py > $TRAIN_CORPUS
  # wget -O- $URL > dev/null 2>&1 | python3 tokenizer.py > $TRAIN_CORPUS
#fi
#wget -O- $URL > dev/null 2>&1 | python3 tokenizer.py > $TRAIN_CORPUS

cat $DATA_SOURCE | python3 tokenizer.py > $TRAIN_CORPUS

#gzip -f $TRAIN_CORPUS
#TRAIN_CORPUS+=".gz"

#morfessor-model-%.bin: $(DATA_SOURCE)
ulimit -t unlimited && nice -n 19 morfessor -t $TRAIN_CORPUS -s $MORFESSOR_MODEL -x $LEXICON --logfile $TRAIN_LOG

# Run Morfessor on the input, save a mapping from words to segments
#segments.%: $(MORFESSOR_MODEL)-%.bin $(DATA_SOURCE)

#TODO strip all punctuation and uninteresting words from the input.
ulimit -t unlimited && cat $TRAIN_CORPUS | sed -e 's/ /\n/g' | sort -u | nice -n 19 morfessor -l $MORFESSOR_MODEL -T - --logfile $PREDICT_LOG > $SEGMENT_OUTPUT

#output-segmented-ep.%: segments-ep.% $(DATA_SOURCE)
cat $TRAIN_CORPUS | ./reconstruct-sentences.py $SEGMENT_OUTPUT > $RECONSTRUCTED_SENTS
