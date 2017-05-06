
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 30.04.17
@author: Eric Lief
"""

import sys
import os
import glob

# STDIN contains the output segmented sentences separated by a delimiter
# resulting from the training task.

#head, tail = os.path.split("~/segmentor/output-segmented*")


def calc_splits(file):
    """
    Read each sentence and calculate the number of splits per word
    and total distribution of splits.
    :param file
    :return frequency of splits:
    """
    #print(file)
    split_counts = [0, 0, 0, 0]
    for segmented_sentence in file:
        #print(segmented_sentence)
        segmented_words = segmented_sentence.rstrip().split(" ◽ ")          # the ◽ cat s ◽ chas ed ◽ the ◽ mouse
        splits_per_word = [len(sw.split()) - 1 for sw in segmented_words]   # [0,     1,       1,       0,     1]
        #print(segmented_words)
        #print(splits_per_word)
        for i in splits_per_word:
            if i <= 2:
                split_counts[i] += 1
            elif i > 2:
                split_counts[3] += 1
                
    #print(split_counts)
    total_splits = sum(split_counts)
    
    #print("total splits = ", total_splits)
    freqs = [i / total_splits for i in split_counts]
    return freqs

# Read segment-output and write calculated split output to file
filenames = glob.glob('*output-segmented-*.*')
#print(filenames)
with open('output-stats.txt', 'w') as out:
    out.write("corpus\t0\t1\t2\t3+\n")
    for filename in filenames:
        with open(filename, 'rt') as output_segmented_file:
            #out.write(str(output_segmented_file))
            #out.write(str(calc_splits(output_segmented_file)))
            # out.write("corpus\t0\t1\t2\t3+\n")
            out.write(filename[-5:] + '\t')
            #for sentence in f:
            for freq in calc_splits(output_segmented_file):
                out.write(str(round(freq, 2)) + '\t')
            out.write('\n')


