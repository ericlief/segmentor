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


def counts(f):
    """
    Read each sentence and calculate the number of splits per word
    and total distribution of splits.
    :param f:
    :return frequency of splits:
    """

    split_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for segmented_sentence in sys.stdin:
        segmented_words = segmented_sentence.rstrip().split(" ◽ ")
    # print(segmented_words)                                                                                                                          splits_per_word = [len(segmented_word.split()) - 1 for segmented_word in segmented_words]
    # print(splits_per_word)
    for i in splits_per_word:
        if i < 10:
            split_counts[i] += 1
    # print(split_counts)                                                                                                                         total_splits = sum(split_counts)
    print("total splits = ", total_splits)
    freqs = [i / total_splits for i in split_counts]
    return freqs


# Read segment-output and write calculated split output to file
filenames = glob.glob('*output-segmented*')
for filename in filenames:
    with open(filename, 'r') as f:
        with open('output-stats.txt', 'wa') as out:
            for sentence in f:
                out.write("file:", filename)
                out.write(str(counts(filename)))


