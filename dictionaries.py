#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 07.05.17
@author: Eric Lief
"""


import sys
import os
import glob
import regex as re


def process_tokens(segments_file):

    for word in segments_file:
        morphs = word.lower().rstrip().split()
        if len(morphs) == 1:
            no_split_words.add(morphs[0])
        elif len(morphs) == 2:
            m1 = morphs[0]
            m2 = morphs[1]
            if max(len(m1)/len(m2), len(m2)/len(m1)) >= 2:
                if len(m1) > len(m2):
                    stem = m1
                    suffix = m2
                    stems.add(stem)
                    suffixes.add(suffix)

                else:
                    prefix = m1
                    stem = m2
                    prefixes.add(prefix)
                    stems.add(stem)


def process(segments_file):
    p0 = re.compile("^[^0-9_\-@#\$\*<>»¿\s]+$", re.M)                         # no split non-numeric morphs only
    p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s]+) ([^0-9_\-@#\$\*<>»¿\s]+)$", re.M)   # one split non-numeric morphs only

    for word in segments_file:
        word = word.lower()
        # Find no-split words and add to dictionary
        r = re.search(p0, word)
        if r:
            m = r.group(0)
            print("no split: ", repr(m))
            no_split_words.append(m)
            # no_split_words.add(m)

        # Find 1-split words and add morphs to either prefix,
        # suffix, or stem dictionaries,
        # only if the size of one of the morphs is at least
        # twice as large as the other
        r = re.search(p1, word)
        if r:
            m1 = r.group(1)
            print("m1: ", m1)

            m2 = r.group(2)
            print("m2: ", repr(m2))

        # morphs = word.rstrip().split()
        # if len(morphs) == 1:
        #     no_split_words.add(morphs[0])
        # elif len(morphs) == 2:
        #     m1 = morphs[0]
        #     m2 = morphs[1]
            if max(len(m1) / len(m2), len(m2) / len(m1)) >= 2:
                if len(m1) > len(m2):
                    stem = m1
                    suffix = m2
                    # stems.add(stem)
                    # suffixes.add(suffix)
                    stems.append(stem)
                    suffixes.append(suffix)
                else:
                    prefix = m1
                    stem = m2
                    # prefixes.add(prefix)
                    # stems.add(stem)
                    prefixes.append(prefix)
                    stems.append(stem)
        # elif len(morphs) == 1:
        #     no_split_words.add(word.rstrip().split()[0])

# Get all segments files
filenames = glob.glob('segments-*')
# print(filenames)

for filename in filenames:
    with open(filename, 'rt') as f_in:

        # no_split_words = set([])
        # prefixes = set([])
        # stems = set([])
        # suffixes = set([])
        no_split_words = []
        prefixes = []
        stems = []
        suffixes = []
        # Read segments files, process morphemes and assign to
        # dictionary, and write to file


        # process_tokens(f_in)
        process(f_in)

        dict_file_suffix = filename[8:]

        # Write no split
        with open('no-split' + dict_file_suffix, 'w') as f_out:
            for w in no_split_words:
                f_out.write(str(w) + '\n')

        # Write stems
        with open('stems' + dict_file_suffix, 'w') as f_out:
            for w in stems:
                f_out.write(str(w) + '\n')

        # Write prefixes
        with open('prefixes' + dict_file_suffix, 'w') as f_out:
            for w in prefixes:
                f_out.write(str(w) + '\n')

        # Write suffixes
        with open('suffixes' + dict_file_suffix, 'w') as f_out:
            for w in suffixes:
                f_out.write(str(w) + '\n')


