#!/usr/bin/env bash

echo "Enter source language abbreviation"
read src
echo "Enter target language abbreviation"
read targ
echo "Enter abbreviated name of corpus"
read corpus
echo "Enter paralell corpus languages separated by a dash"
read paral

#unzip "/var/tmp/${corpus}-${paral}.txt.zip" -d /var/tmp

if [[ $corpus == "ep" ]];
then
    DATA_SRC="ep.${paral}.${src}.gz"
    DATA_TARG="ep.${paral}.${targ}.gz"
    URL_SRC="http://opus.lingfil.uu.se/download.php?f=Europarl/mono/Europarl.raw.${src}.gz"
    URL_TARG="http://opus.lingfil.uu.se/download.php?f=Europarl/mono/Europarl.raw.${targ}.gz"
    
elif [[ $corpus == "dgt" ]]; then
	#DATA_SOURCE="DGT.raw.${lang}.gz"
    DATA_SRC="dgt.${paral}.${src}.gz"
    DATA_TARG="dgt.${paral}.${targ}.gz"
    URL_SRC="http://opus.lingfil.uu.se/download.php?f=DGT/mono/DGT.raw.${src}.gz"
    URL_TARG="http://opus.lingfil.uu.se/download.php?f=DGT/mono/DGT.raw.${targ}.gz"
    
elif [[ $corpus == "os" ]]; then
    #DATA_SOURCE="/tmp/OpenSubtitles2016.raw.${lang}.gz"
    DATA_SRC="os.${paral}.${src}.gz"
    DATA_TARG="os.${paral}.${targ}.gz"
    URL_SRC="http://opus.lingfil.uu.se/download.php?f=OpenSubtitles2016/mono/OpenSubtitles2016.raw.${src}.gz"
    URL_TARG="http://opus.lingfil.uu.se/download.php?f=OpenSubtitles2016/mono/OpenSubtitles2016.raw.${targ}.gz"
else
    echo "Corpus not found!"
fi




# MORFESSOR_MODEL="morfessor-model-${corpus}.${lang}.bin"
# #TRAIN_CORPUS="/tmp/training-data-${corpus}.${lang}.gz"
# TRAIN_CORPUS="/var/tmp/training-data-${corpus}.${paral}.${lang}"
# LEXICON="lexicon-${corpus}.${paral}.${lang}.txt"
# PREDICT_LOG="morfessor-predict-${corpus}.${paral}.${lang}.log.txt"
# TRAIN_LOG="morfessor-train-${corpus}.${paral}.${lang}.log"
# SEGMENT_OUTPUT="segments-${corpus}.${paral}.${lang}.txt"
# RECONSTRUCTED_SENTS="output-segmented-${corpus}.${paral}.${lang}.txt"

# Download DATA
wget -O $DATA_SRC $URL_SRC
wget -O $DATA_TARG $URL_TARG

# Make shorter versions for testing
gunzip -kf ${DATA_SRC}
gunzip -kf ${DATA_TARG}

DATA_SRC=${DATA_SRC:0:-3}
DATA_TARG=${DATA_TARG:0:-3}

head -n 1000 $DATA_SRC > "${DATA_SRC}.sm"
head -n 1000 $DATA_TARG > "${DATA_TARG}.sm"

head -n 10000 $DATA_SRC > "${DATA_SRC}.md"
head -n 10000 $DATA_TARG > "${DATA_TARG}.md"

# Get alignments
python3 get_alignments.py "${DATA_SRC}.sm" "${DATA_TARG}.sm"
python3 get_alignments.py "${DATA_SRC}.md" "${DATA_TARG}.md"                
