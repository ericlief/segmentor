
.PHONY: all clean

# Never ever remove any intermediate files
.SECONDARY:

MORFESSOR_MODEL::=morfessor-model

DATA_SOURCE::=Europarl.raw.en.gz

TRAIN_CORPUS-%::=training-data-ep.%.gz

all: tokenizer.py reconstruct-sentences.py output-segmented-ep.en

output-segmented-ep.%: segments-ep.% $(DATA_SOURCE)
	#output-segmented-ep-%.txt: segments-ep-%.txt training-data-ep-%.gz
	gunzip -ckv $(TRAIN_CORPUS-$*) | ./reconstruct-sentences.py "$<" > "$@"

# Run Morfessor on the input, save a mapping from words to segments.
segments.%: $(MORFESSOR_MODEL)-%.bin $(DATA_SOURCE)

	#TODO strip all punctuation and uninteresting words from the input.
	#gunzip -ckv $(TRAIN_CORPUS-$*) | sed -e 's/ /\n/g' | sort -u | nice -n 19 morfessor -l "$<" -T - --logfile "morfessor-predict-$*-log.txt" > "$@"
	ulimit -t unlimited && gunzip -ckv $(TRAIN_CORPUS-$*) | sed -e 's/ /\n/g' | sort -u | nice -n 19 morfessor -l "$<" -T - --logfile "morfessor-predict-log.$*" > "$@"

morfessor-model-%.bin: $(DATA_SOURCE)
	#chmod u+x tokenizer.py
	#gunzip -ckv $(TRAIN_CORPUS-$*) | ./tokenizer.py
	#morfessor -t $(TRAIN_CORPUS-$*) -s "$@" -x "lexicon-$*.txt" --logfile "morfessor-train-$*-log.txt"
	ulimit -t unlimited && nice -n 19 morfessor -t $(TRAIN_CORPUS-$*) -s "$@" -x "lexicon.$*" --logfile "morfessor-train-log.$*"

tokenizer.py:
	chmod u+x tokenizer.py

reconstruct-sentences.py:
	chmod u+x tokenizer.py

Europarl.raw.%.gz:
	wget -O "$@" 'http://opus.lingfil.uu.se/download.php?f=Europarl/mono/Europarl.raw.$*.gz'

training-data-ep-%.gz: $(DATA_SOURCE)
	gunzip -ckv $(TRAIN_CORPUS-$*) | ./tokenizer.py "$<" > "$@"


Europarl.raw.%: Europarl.raw.%.gz
#	gunzip -kv "$<"

Europarl.raw.%: Europarl.raw.%.gz
#	gunzip -ckv $(TRAIN_CORPUS-$*) | ./tokenizer.py

clean:
	rm -rf Europarl.raw.* Europarl.raw.*.gz
	rm -f morfessor-model-*.bin segments-*.txt output-segmented-*.txt lexicon-*.txt morfessor-*-log.txt

