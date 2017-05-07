#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 07.05.17
@author: Eric Lief
"""

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 30.04.17
@author: Eric Lief
"""

import sys
import os
import glob


def process_tokens(segments_file):

    for word in segments_file:
        morphs = word.rstrip().split()
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


# Get all segments files
filenames = glob.glob('segments-*')
# print(filenames)

for filename in filenames:
    with open(filename, 'rt') as f_in:

        no_split_words = set([])
        prefixes = set([])
        stems = set([])
        suffixes = set([])

        # Read segments files, process morphemes and assign to
        # dictionary, and write to file
        process_tokens(f_in)
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


