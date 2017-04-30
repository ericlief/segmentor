#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 30.04.17
@author: Eric Lief
"""

import sys

# STDIN contains the segmented sentences separated by a delimiter
# Read each sentence and count the number of splits per word

split_counts = [0,0,0,0,0,0,0,0,0,0]
for segmented_sentence in sys.stdin:
    segmented_words = segmented_sentence.rstrip().split(" ◽ ")
    # print(segmented_words)
    splits_per_word = [len(segmented_word.split()) - 1 for segmented_word in segmented_words]
    # print(splits_per_word)
    for i in splits_per_word:
        split_counts[i] += 1
    # print(split_counts)
total_splits = sum(split_counts)
print("total splits = ", total_splits)
freqs = [i / total_splits for i in split_counts]
print(freqs)
