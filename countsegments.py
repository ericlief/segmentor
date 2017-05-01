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


def counts(file):
    """
    Read each sentence and calculate the number of splits per word
    and total distribution of splits.
    :param file
    :return frequency of splits:
    """
    #print(file)
    split_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for segmented_sentence in file:
        #print(segmented_sentence)
        segmented_words = segmented_sentence.rstrip().split(" ◽ ")          # the ◽ cat s ◽ chas ed ◽ the ◽ mouse
        splits_per_word = [len(sw.split()) - 1 for sw in segmented_words]   # [0,     1,       1,       0,     1]
        #print(segmented_words)
        #print(splits_per_word)
        for i in splits_per_word:
            if i < 10:
                split_counts[i] += 1
    #print(split_counts)
    total_splits = sum(split_counts)
    #print("total splits = ", total_splits)
    freqs = [i / total_splits for i in split_counts]
    return freqs

# Read segment-output and write calculated split output to file
filenames = glob.glob('*output-segmented-*.*')
#print(filenames)
with open('output-stats.txt', 'w') as out:
    for filename in filenames:
        with open(filename, 'rt') as f:
            out.write("Filename: " + filename + '\n')
            #for sentence in f:
            out.write(str(counts(f)) + '\n')


