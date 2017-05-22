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
from collections import defaultdict
# from enum
# class Segments(enum)

class SubWordUnits:
    def __init__(self, segments_file_in):

        # self.filename = filename_in
        self.segments_file_in = segments_file_in
        self.all_words = defaultdict(int)       # {word: count}
        self.all_other_words = []
        self.no_split_words = []
        self.other_one_split_words = []
        self.prefixes = defaultdict(int)
        self.stems = defaultdict(int)
        self.suffixes = defaultdict(int)
        self.unknown = defaultdict(int)
        self._word_counts = defaultdict(int)
        self._signatures = defaultdict(list)    # {signature: [words]}
        self.processed_words = set([])
        self.adjusted_words = {}                # {orig_word: adjusted_word}
        self.LABELS = {'p': 'prefixes', 's': 'stems', 'e': 'endings', '?': 'unknown'}

    def process(self):
        """
        All words in the text are processed and a
        signature (label) assigned if one morpheme or
        segment is twice the size (2X) that of all others.
        If a segment twice the size of all
        other morphemes in the word is found, it is
        marked as the stem, and those morphemes occurring
        before it are marked as prefixes and those after
        as suffixes.

        :return:
        """

        # Regex pattern to find an alphabetic string
        # Includes:
        # No-split words/stems
        # 1+ split words
        p = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+\s)+$", re.M)

        # Whitespace
        W = re.compile("^\s+$")

        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                # Skip whitespace
                if re.match(W, word):
                    continue

                # Preprocess/normalize string:
                # remove spaces and capitalization
                word = word.lower()
                orig_word = '-'.join(word.split())

                # Hyphenate segments, e.g.
                # dis regard -> dis-regard
                self.all_words[orig_word] += 1       # total count of words

                # Already seen word, skip?
                if orig_word in self.processed_words:
                    continue

                # Is the split or non-split word of acceptable format?
                match = re.match(p, word)

                # not a single-split word, skip
                if not match:
                    continue

                # if match:
                #print("2+ split?")
                # groups = match2p.groups()
                # size = len(groups)
                # s = ''
                # print(size)
                # print(match2p[0])
                morphs = match[0].split()
                #print(morphs)
                # lengths = [(m, len(m)) for m in morphs]
                max_len_morph = max(morphs, key=len)  # this is stem
                max_len = len(max_len_morph)

                # print(max_len_morph)

                # Check if stem is 2X size of all other morphs in word
                is_stem_2X = True
                for m in morphs:
                    if m != max_len_morph and max(len(m) / max_len, max_len / len(m)) < 2:
                        is_stem_2X = False

                #print("stem 2X=", is_stem_2X)

                # TODO
                # Add word to signatures here also
                # and change affixes to defaultdict with counts?
                signature = ''
                if is_stem_2X:
                    print('stem is 2X for ', morphs)
                    max_i = morphs.index(max_len_morph)
                    for i, m in enumerate(morphs):
                        if i < max_i:
                            # self.prefixes.append(m)
                            self.prefixes[m] += 1
                            signature += '-p' if signature else 'p'
                            #print('prefix ', m)
                        elif i > max_i:
                            # self.suffixes.append(m)
                            self.suffixes[m] += 1
                            signature += '-e' if signature else 'e'

                            #print('suffix ', m)
                        else:
                            # self.stems.append(m)
                            self.stems[m] += 1
                            signature += '-s' if signature else 's'
                            #print('stem ', m)

                    # Add word to list of processed words
                    #hyphen_word = '-'.join(morphs)
                    self.signatures[signature].append(orig_word)
                    self.processed_words.add(orig_word)

        print('processed words ', self.processed_words)

    def process_known_one_split(self):

        # one split non-numeric morphs only
        p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*]+)$", re.M)

        # Iterate through one split words and map to signature
        # prefix-stem (p-s)
        # stem-suffix (s-e)

        with open(self.segments_file_in, 'rt') as f:
            for word in f:
                word = word.lower()

                # Already seen word, skip?
                if word in self.processed_words:
                    continue

                # Find 1-split words and add morphs to either prefix, suffix, etc.
                match1 = re.search(p1, word)

                if match1:
                    #print("found new one split")
                    m1 = match1.group(1)
                    #print("m1: ", repr(m1))

                    m2 = match1.group(2)
                    #print("m2: ", repr(m2))

                    morphs = [m1, m2]
                    hyphen_word = '-'.join(morphs)
                    if m1 in self.prefixes and m2 in self.stems:
                        self.signatures['p-s'].append(hyphen_word)
                        self.processed_words.add(word)
                        self.prefixes[m1] += 1
                        self.stems[m2] += 1
                        #print("found new p-s")

                    elif m1 in self.stems and m2 in self.suffixes:
                        self.signatures['s-e'].append(hyphen_word)
                        self.processed_words.add(word)
                        self.stems[m1] += 1
                        self.suffixes[m2] += 1
                        #print("found new s-e")

    # def reprocess_known_one_split(self):
    #
    #     # one split non-numeric morphs only
    #     p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)
    #
    #     # Iterate through one split words and map to signature
    #     # prefix-stem (p-s)
    #     # stem-suffix (s-e)
    #
    #     with open(self.segments_file_in, 'rt') as f:
    #         for word in f:
    #
    #             word = word.lower()
    #
    #             # Already seen word, skip
    #             if word in self.processed_words:
    #                 continue
    #
    #             # Find 1-split words and add morphs to either prefix, suffix, etc.
    #             match1 = re.search(p1, word)
    #
    #             if match1:
    #                 #2Aprint("found new one split")
    #                 m1 = match1.group(1)
    #                 #print("m1: ", repr(m1))
    #
    #                 m2 = match1.group(2)
    #                 #print("m2: ", repr(m2))
    #
    #                 morphs = [m1, m2]
    #                 hyphen_word = '-'.join(morphs)
    #                 if m1 in self.prefixes or m2 in self.stems:
    #                     self.signatures['p-s'].append(hyphen_word)
    #                     self.processed_words.add(word)
    #                     self.prefixes[m1] += 1
    #                     self.stems[m2] += 1
    #                     #print("found new p-s")
    #
    #                 elif m1 in self.stems or m2 in self.suffixes:
    #                     self.signatures['s-e'].append(hyphen_word)
    #                     self.processed_words.add(word)
    #                     self.stems[m1] += 1
    #                     self.suffixes[m2] += 1
    #                     #print("found new s-e")

    def reprocess_2plus_words(self):

        # One-split non-numeric morphs only
        p = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+\s)+$", re.M)
        # Whitespace
        W = re.compile("^\s+$")

        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                # Skip whitespace
                if re.match(W, word):
                    continue

                # Preprocess/normalize string:
                # remove spaces and capitalization
                word = word.lower()
                orig_word = '-'.join(word.split())

                # Already seen word, skip
                if orig_word in self.processed_words:
                    #print('skipping ', word)
                    continue

                # Find 2+ split words and add morphs to either prefix,
                match = re.match(p, word)

                if match:
                    #print('reprocessing ', word)
                    #print("2+ split?")
                    # groups = match2p.groups()
                    # size = len(groups)
                    # s = ''
                    # print(size)
                    # print(match2p[0])
                    morphs = match[0].split()
                    #print(morphs)

                    signature = self.add_signature(morphs)

                    # signature = ''
                    # for m in morphs:
                    #     if m in self.prefixes and \
                    #         's' not in signature and 'e' not in signature:
                    #         # self.prefixes.append(m)
                    #         self.prefixes[m] += 1
                    #         signature += '-p' if signature else 'p'
                    #         #print('prefix ', m)
                    #     elif m in self.suffixes:
                    #         # self.suffixes.append(m)
                    #         self.suffixes[m] += 1
                    #         signature += '-e' if signature else 'e'
                    #
                    #         #print('suffix ', m)
                    #     elif m in self.stems and \
                    #          'e' not in signature:
                    #         # self.stems.append(m)
                    #         self.stems[m] += 1
                    #         signature += '-s' if signature else 's'
                    #        # print('stem ', m)
                    #
                    #     else:       # morph not known, so mark with '?'
                    #         signature += '-?' if signature else '?'
                    #
                    # if 's' not in signature:
                    #     signature = 'no-stem'
                    #
                    # # Count unknowns ('?') in signature
                    # cnt = 0
                    # for ch in signature:
                    #     if ch == '?':
                    #         cnt += 1
                    #
                    # if cnt > 3:
                    #     signature = 'indeter'
                    #print(cnt)

                    # Add word to list of processed words
                    #hyphen_word = '-'.join(morphs)
                    self.signatures[signature].append(orig_word)
                    self.processed_words.add(orig_word)

    def add_signature_mod(self, morphs):
        """
        Get signature (morpheme labels) of
        a sequence of morphemes and then
        add the segments to their respective
        dictionaries.
        :param morphs:
        :return: signature
        """
        signature = ''
        for m in morphs:
            # if m in self.prefixes and \
            #                 's' not in signature and 'e' not in signature:
            #     # self.prefixes.append(m)
            #     self.prefixes[m] += 1
            #     signature += '-p' if signature else 'p'
            #     # print('prefix ', m)
            # elif m in self.suffixes:
            #     # self.suffixes.append(m)
            #     self.suffixes[m] += 1
            #     signature += '-e' if signature else 'e'
            #
            #     # print('suffix ', m)
            # elif m in self.stems and \
            #                 'e' not in signature:
            #     # self.stems.append(m)
            #     self.stems[m] += 1
            #     signature += '-s' if signature else 's'
            #     # print('stem ', m)
            #
            # else:  # morph not known, so mark with '?'
            #     signature += '-?' if signature else '?'

            if m in self.prefixes and \
                            's' not in signature and 'e' not in signature:
                # self.prefixes.append(m)
                #self.prefixes[m] += 1
                signature += 'p'
                # print('prefix ', m)
            if m in self.suffixes:
                # self.suffixes.append(m)
                #self.suffixes[m] += 1
                signature += 'e'

                # print('suffix ', m)
            if m in self.stems and \
                            'e' not in signature:
                # self.stems.append(m)
                #self.stems[m] += 1
                signature += 's'
                # print('stem ', m)

            # else:  # morph not known, so mark with '?'
            #     signature += '?'

            signature += '-'

        signature = signature[:-1]  # strip last '-'
        labels = signature.split('-')
        #num_labels = len(labels)
        new_sig = ''
        #for i in range(len(labels)):
        for i, label in enumerate(labels):
            new_lab = ''
            if len(label) > 1:  # more than one possible label, e.g. 'pse'
                if 's' in label:
                    if (i > 0 and labels[i - 1] == 's') or \
                            (i < len(labels) and labels[i + 1] == 's'):
                        new_lab = 's'
                        new_sig += new_lab

        n = len(labels)     # number of labels/length of signature
        for i in range(0, n):
            cur_label = labels[i]
            has_stem = False

            # Check forward
            for j in range(i, n):
                if 's' in labels[j]:
                    has_stem = True

            # Check backward
            for k in range(i, 0):
                pass




        if 's' not in signature:
            signature = 'no-stem'

        # Count unknowns ('?') in signature
        cnt = 0
        for ch in signature:
            if ch == '?':
                cnt += 1

        if cnt > 3:
            signature = 'indeter'

        return signature

    def add_signature(self, morphs):
        """
        :param morphs:
        :return: signature
        Get signature (morpheme labels) of
        a sequence of morphemes without
        adding the segments to their respective
        dictionaries (as previous method does)
        :param morphs:
        :return: signature
        """

        signature = ''
        for m in morphs:
            if m in self.prefixes and \
                            's' not in signature and 'e' not in signature:
                self.prefixes[m] += 1
                signature += '-p' if signature else 'p'
                # print('prefix ', m)
            elif m in self.suffixes:
                self.suffixes[m] += 1
                signature += '-e' if signature else 'e'

                # print('suffix ', m)
            elif m in self.stems and \
                            'e' not in signature:
                self.stems[m] += 1
                signature += '-s' if signature else 's'
                # print('stem ', m)

            else:  # morph not known, so mark with '?'
                signature += '-?' if signature else '?'
                self.unknown[m] += 1

        # Check if no stem present in signature.
        # If so, check if any morphs may also be stems,
        # and if so, reconstruct signature with the alternate
        # stem label(s), updating the dictionary.
        if 's' not in signature:
            #print("no stem present for ", morphs)
            #print('orig sig', signature)

            labels = signature.split('-')
            n = len(labels)     # number of labels/length of signature
            new_sig = ''
            for i in range(n):
                m = morphs[i]           # current morph
                label = self.LABELS[labels[i]]       # expand label name
                if m in self.stems:
                    #print('adding stem ', m)
                    new_sig += '-s' if new_sig else 's'
                    self.stems[m] += 1  # add to stems dict

                    #print(SubWordUnits.__getattribute__(self, label))

                    dict_ref = SubWordUnits.__getattribute__(self, label)
                    cur_morf_cnt = dict_ref[m]
                    #print('removing label ', label)
                    #print(cur_morf_cnt)
                    #print(dict_ref)

                    if cur_morf_cnt > 1:    # update dict for old label
                        #cur_morf_cnt -= 1
                        #SubWordUnits.__setattr__(self, label, cur_morf_cnt - 1)
                        dict_ref[m] -= 1
                    else:
                        #del self.stems[m]
                        del dict_ref[m]

                    #print(SubWordUnits.__getattribute__(self, label))

                else:           # keep label, update
                    new_sig += '-' + labels[i] if i > 0 else labels[i]
            signature = new_sig
            #print('new sig', new_sig)

        else:
            signature = 'no-stem'

        # Count unknowns ('?') in signature
        cnt = 0
        for ch in signature:
            if ch == '?':
                cnt += 1

        if cnt > 3:
            signature = 'indeter'

        return signature

    def get_signature(self, morphs):
        """
        :param morphs:
        :return: signature
        Get signature (morpheme labels) of
        a sequence of morphemes without
        adding the segments to their respective
        dictionaries (as previous method does)
        :param morphs:
        :return: signature
        """

        signature = ''
        for m in morphs:
            if m in self.prefixes and \
                            's' not in signature and 'e' not in signature:
                # self.prefixes.append(m)
                signature += '-p' if signature else 'p'
                # print('prefix ', m)
            elif m in self.suffixes:
                # self.suffixes.append(m)
                signature += '-e' if signature else 'e'

                # print('suffix ', m)
            elif m in self.stems and \
                            'e' not in signature:
                # self.stems.append(m)
                signature += '-s' if signature else 's'
                # print('stem ', m)

            else:  # morph not known, so mark with '?'
                signature += '-?' if signature else '?'

        if 's' not in signature:
            signature = 'no-stem'

        # Count unknowns ('?') in signature
        cnt = 0
        for ch in signature:
            if ch == '?':
                cnt += 1

        if cnt > 3:
            signature = 'indeter'

        return signature

    def adjust_boundary_one_split(self):

        print('adjusting boundary for one split')

        # Regex for one-split non-numeric morphs only
        # p = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)
        p = re.compile("^[^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+ [^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+$", re.M)

        # Whitespace
        W = re.compile("^\s+$")

        # Iterate through one split words and map to signature
        # prefix-stem (p-s)
        # stem-suffix (s-e)

        # for word in self.segments_file_in:
        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                # Skip whitespace
                if re.match(W, word):
                    continue

                # Find 1-split words
                match = re.search(p, word)

                # No match, slip
                if not match:
                    continue

                orig_word = word.lower()

                # Already seen word, skip
                if orig_word in self.processed_words:
                    #print('skipping word already processed')
                    continue

                # Already adjusted word
                if orig_word in self.adjusted_words:
                    #print('skipping word already adjusted')
                    adj_word = self.adjusted_words[orig_word]

                    # TODO
                    continue

                morphs = match[0].split()
                word = ''.join(morphs)
                i_m2 = len(morphs[0])  # pos of original morph 2 (m2)
                #i_m2 = len(m1)  # pos of original morph 2 (m2)
                signature = ''

                # Try shifting boundary to left
                #print("shifting boundary left")
                new_m1 = word[:i_m2 - 1]  # indices of new first morph
                new_m2 = word[i_m2 - 1:]  # indices of new second morph
                # stem_index = -1
                #print("new m1: ", new_m1)
                #print("new m2: ", new_m2)
                if new_m1 in self.stems and \
                   new_m2 in self.suffixes:
                    signature = 's-e'
                elif new_m1 in self.prefixes and \
                     new_m2 in self.stems:
                    signature = 'p-s'
                elif new_m1 in self.stems and \
                     new_m2 in self.stems:
                    signature = 's-s'

                # Try shifting boundary to right
                else:
                    #print("shifting boundary right")

                    new_m1 = word[:i_m2 + 1]  # indices of new first morph
                    new_m2 = word[i_m2 + 1:]  # indices of new second morph
                    #print("new m1: ", new_m1)
                    #print("new m2: ", new_m2)

                    # if new_m1 in self.stems:
                    #     signature = 's-'
                    # elif new_m1 in self.prefixes:
                    #     signature = 'p-'
                    # else:
                    #     signature = '?-'

                    if new_m1 in self.stems and \
                       new_m2 in self.suffixes:
                        signature = 's-e'
                    elif new_m1 in self.prefixes and \
                         new_m2 in self.stems:
                        signature = 'p-s'
                    else:
                        # signature = '?-?'  # unknown word
                        signature = self.add_signature(morphs)
                        new_m1, new_m2 = morphs[0], morphs[1]  # set boundaries back

                new_morphs = [new_m1, new_m2]
                new_word = '-'.join(new_morphs)

                # Augment corresponding dictionaries
                if signature == 'p-s':
                    self.prefixes[new_m1] += 1
                    self.stems[new_m2] += 1
                    self._signatures['p-s'].append(new_word)
                    # self.processed_words.add(orig_word)

                    #print("found new p-s")

                elif signature == 's-e':
                    self.stems[new_m1] += 1
                    self.suffixes[new_m2] += 1
                    self.signatures['s-e'].append(new_word)
                    # self.processed_words.add(orig_word)

                self.processed_words.add(orig_word)

                   # print("found new s-e")

                # TODO: ???? words: should we add or reprocess????
                # else:
                #     self._signatures['?-?'].append(hyphen_word)
                #     self.processed_words.add(word)


            print("final word", new_word, signature)

        print('adjusted\n', self.adjusted_words)

    def adjust_boundary(self):

        print('adjusting boundary for one split')

        # Regex for one-split non-numeric morphs only
        # p = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)
        p = re.compile("^[^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+ [^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+$", re.M)

        # Whitespace
        W = re.compile("^\s+$")

        # Iterate through one split words and map to signature
        # prefix-stem (p-s)
        # stem-suffix (s-e)

        # for word in self.segments_file_in:
        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                # Skip whitespace
                if re.match(W, word):
                    continue

                # Find 1-split words
                match = re.search(p, word)

                # No match, slip
                if not match:
                    continue

                orig_word = word.lower()

                # Already seen word, skip
                if orig_word in self.processed_words:
                    print('skipping word already processed')
                    continue

                # Already adjusted word
                if orig_word in self.adjusted_words:
                    print('skipping word already adjusted')
                    adj_word = self.adjusted_words[orig_word]

                    # TODO
                    continue

                # Shift boundary either left or right
                # in order to search for a potential
                # morpheme missed in the first pass
                morphs = match[0].split()
                num_morphs = len(morphs)
                word = ''.join(morphs)

                for i in range(num_morphs - 1):

                    # Shift left
                    m1 = morphs[i]
                    m2 = morphs[i + 1]
                    new_m1 = m1 + m2[0]
                    new_m2 = m2[1:]

                    # Shift right
                    new_m1 = m1[:-1]
                    new_m2 = m1[-1] + m2



                i_m2 = len(morphs[0])       # pos of original morph 2 (m2)



                # Try shifting boundary to left
                #print("shifting boundary left")
                new_m1 = word[:i_m2 - 1]    # indices of new first morph
                new_m2 = word[i_m2 - 1:]    # indices of new second morph
                # stem_index = -1
                #print("new m1: ", new_m1)
                #print("new m2: ", new_m2)

                signature = self.get_signature([new_m1, new_m2])
                if signature != 's-e' or \
                   signature != 'p-s' or \
                   signature != 's-s':

                # if new_m1 in self.stems and \
                #    new_m2 in self.suffixes:
                #     signature = 's-e'
                # elif new_m1 in self.prefixes and \
                #      new_m2 in self.stems:
                #     signature = 'p-s'

                # Try shifting boundary to right
                # else:
                    #print("shifting boundary right")

                    new_m1 = word[:i_m2 + 1]  # indices of new first morph
                    new_m2 = word[i_m2 + 1:]  # indices of new second morph
                    signature = self.get_signature([new_m1, new_m2])
                    if signature != 's-e' or \
                       signature != 'p-s' or \
                       signature != 's-s':

                    #print("new m1: ", new_m1)
                    #print("new m2: ", new_m2)

                    # if new_m1 in self.stems:
                    #     signature = 's-'
                    # elif new_m1 in self.prefixes:
                    #     signature = 'p-'
                    # else:
                    #     signature = '?-'

                    # if new_m1 in self.stems and \
                    #    new_m2 in self.suffixes:
                    #     signature = 's-e'
                    # elif new_m1 in self.prefixes and \
                    #      new_m2 in self.stems:
                    #     signature = 'p-s'
                    # else:
                        # signature = '?-?'  # unknown word
                        # signature = self.get_signature(morphs)
                        new_m1, new_m2 = morphs[0], morphs[1]  # set boundaries back

                new_morphs = [new_m1, new_m2]
                new_word = '-'.join(new_morphs)

                # Augment corresponding dictionaries
                if signature == 'p-s':
                    self.prefixes[new_m1] += 1
                    self.stems[new_m2] += 1
                    self._signatures['p-s'].append(new_word)
                    # self.processed_words.add(orig_word)

                    #print("found new p-s")

                elif signature == 's-e':
                    self.stems[new_m1] += 1
                    self.suffixes[new_m2] += 1
                    self.signatures['s-e'].append(new_word)
                    # self.processed_words.add(orig_word)

                self.processed_words.add(orig_word)

                   # print("found new s-e")

                # TODO: ???? words: should we add or reprocess????
                # else:
                #     self._signatures['?-?'].append(hyphen_word)
                #     self.processed_words.add(word)


            print("final word", new_word, signature)

        print('adjusted\n', self.adjusted_words)


    # def readjust_boundary_one_split(self):
    #     # TODO:= relax restriction that both morphs be in dictionary
    #     # after adjusting boundary
    #
    #     #print('readjusting one split')
    #
    #     # one split non-numeric morphs only
    #     p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)
    #
    #     # Iterate through one split words and map to signature
    #     # prefix-stem (p-s)
    #     # stem-suffix (s-e)
    #
    #     # for word in self.segments_file_in:
    #     with open(self.segments_file_in, 'rt') as f:
    #         for word in f:
    #
    #             # Already seen word, skip
    #             if word in self.processed_words:
    #                 continue
    #
    #             raw_word = word.lower()
    #
    #             # Find 1-split words and add morphs to either prefix, suffix, etc.
    #             match1 = re.search(p1, word)
    #
    #             if match1:
    #                 #print("found new one split")
    #                 m1 = match1.group(1)
    #                 #print("m1: ", repr(m1))
    #
    #                 m2 = match1.group(2)
    #                 #print("m2: ", repr(m2))
    #
    #                 morphs = [m1, m2]
    #                 word = ''.join(morphs)
    #                 i_m2 = len(m1)  # pos of original morph 2 (m2)
    #                 signature = ''
    #
    #                 # Try shifting boundary to left
    #                 #print("shifting boundary left")
    #
    #                 new_m1 = word[:i_m2 - 1]  # indices of new first morph
    #                 new_m2 = word[i_m2 - 1:]  # indices of new second morph
    #                 # stem_index = -1
    #                 #print("new m1: ", new_m1)
    #                 #print("new m2: ", new_m2)
    #                 if new_m1 in self.stems or \
    #                    new_m2 in self.suffixes:
    #                     signature = 's-e'
    #                 elif new_m1 in self.prefixes or \
    #                      new_m2 in self.stems:
    #                     signature = 'p-s'
    #
    #                 # Try shifting boundary to right
    #                 else:
    #                     #print("shifting boundary right")
    #
    #                     new_m1 = word[:i_m2 + 1]  # indices of new first morph
    #                     new_m2 = word[i_m2 + 1:]  # indices of new second morph
    #                     #print("new m1: ", new_m1)
    #                     #print("new m2: ", new_m2)
    #                     if new_m1 in self.stems or \
    #                        new_m2 in self.suffixes:
    #                         signature = 's-e'
    #                     elif new_m1 in self.prefixes or \
    #                          new_m2 in self.stems:
    #                         signature = 'p-s'
    #                     else:
    #                         signature = '?-?'  # unknown word
    #                         new_m1, new_m2 = morphs[0], morphs[1]  # set boundaries back
    #
    #                 morphs = [new_m1, new_m2]
    #                 hyphen_word = '-'.join(morphs)
    #
    #                 # Augment corresponding dictionaries
    #                 if signature == 'p-s':
    #                     self.prefixes[new_m1] += 1
    #                     self.stems[new_m2] += 1
    #                     self._signatures['p-s'].append(hyphen_word)
    #                     self.processed_words.add(raw_word)
    #
    #                     #print("found new p-s")
    #
    #                 elif signature == 's-e':
    #                     self.stems[m1] += 1
    #                     self.suffixes[m2] += 1
    #                     self.signatures['s-e'].append(hyphen_word)
    #                     self.processed_words.add(raw_word)
    #
    #                    # print("found new s-e")
    #
    #                 # TODO: ???? words: should we add or reprocess????
    #                 # else:
    #                 #     self._signatures['?-?'].append(hyphen_word)
    #                 #     self.processed_words.add(word)
    #
    #
    #                # print("final word", hyphen_word, signature)
    #

    @property
    def signatures(self):
        return self._signatures


    @ property
    def word_counts(self):
        return self._word_counts


    def write(self):
        # # Get all segments files
        # filenames = glob.glob('segments-*')
        # # print(filenames)
        #
        # for filename in filenames:
        #     with open(filename, 'rt') as f_in:
        #
        #         # process_tokens(f_in)
        #         process(f_in)

        dict_file_suffix = self.segments_file_in[8:]

        # Write no split words
        # with open('no-split' + dict_file_suffix, 'w') as f_out:
        #     for w in self.no_split_words:
        #         f_out.write(str(w) + '\n')

        # Write stems
        with open('stems' + dict_file_suffix, 'w') as f_out:
            for m, cnt in self.stems.items():
                f_out.write(str(cnt) + '\t' + m + '\n')

        # Write prefixes
        with open('prefixes' + dict_file_suffix, 'w') as f_out:
            for m, cnt in self.prefixes.items():
                f_out.write(str(cnt) + '\t' + m + '\n')

        # Write suffixes
        with open('suffixes' + dict_file_suffix, 'w') as f_out:
            for m, cnt in self.suffixes.items():
                f_out.write(str(cnt) + '\t' + m + '\n')

        # Write unknown
        with open('unknown' + dict_file_suffix, 'w') as f_out:
            for m, cnt in self.unknown.items():
                f_out.write(str(cnt) + '\t' + m + '\n')

        # Write signature (mapping)
        with open('signatures' + dict_file_suffix, 'w') as f_out:
            for signature, words in self.signatures.items():
                f_out.write('\n')
                f_out.write(str(signature) + '(' + str(words) + ')' + '\n')

        # Write lexicon (all words)
        with open('dictionary' + dict_file_suffix, 'w') as f_out:
            for word, freq in self.all_words.items():
                f_out.write(word + '\t' + str(freq) + '\n')

        # Write stats, type and token frequency-based
        with open('stats-type' + dict_file_suffix, 'w') as f_out:
            V = len(self.all_words)         # vocab size
            for signature, words in self.signatures.items():
                counts = len(words)
                freq = round(counts / V, 3)
                #f_out.write('\n')
                f_out.write(str(counts) + '\t' + str(freq) + '\t' + signature + '\n')
                #f_out.write('raw count: ' + str(n) + '\n')
                #f_out.write('out of total: ' + str(N) + '\n')
                #f_out.write('frequency: ' + str(freq) + '\n\n')

        with open('stats-token' + dict_file_suffix, 'w') as f_out:
            N = sum(self.all_words.values())     # text size/number of tokens
            for signature, words in self.signatures.items():
                counts = 0
                for word in words:
                    if word in self.adjusted_words:
                        word = self.adjusted_words[word]    # lookup original word before adjustment
                    counts += self.all_words[word]
                #counts = sum([self.all_words[w] for w in words])
                #raw_cnt = len(words)
                freq = round(counts / N, 3)
                #f_out.write('\n')
                f_out.write(str(counts) + '\t' + str(freq) + '\t' + signature + '\n')
                #f_out.write('raw count: ' + str(n) + '\n')
                #f_out.write('out of total: ' + str(N) + '\n')
                #f_out.write('frequency: ' + str(freq) + '\n\n')


# MAIN
# Get all segments files
filenames = glob.glob('segments*')
for filename in filenames:
    morphs = SubWordUnits(filename)
    morphs.process()
    #print(morphs.signatures)
    #print(morphs.processed_words)
    #print(morphs.prefixes)
    #print(morphs.stems)
    #print(morphs.suffixes)

    # don't think necessary
    #morphs.process_known_one_split()

    #print(morphs.signatures)
    #print(morphs.processed_words)
    #print(morphs.prefixes)
    #print(morphs.stems)
    #print(morphs.suffixes)

    #morphs.adjust_boundary_one_split()

    #morphs.adjust_boundary()

    #print(morphs.signatures)
    #print(morphs.processed_words)
    #print(morphs.prefixes)
    #print(morphs.stems)
    #print(morphs.suffixes)

    # Lax condition that both morphs be
    # in dictionaries, to only one, e.g.
    # prefix or stem -> p-s
    # uncomment to use
    #morphs.reprocess_known_one_split()

    #print(morphs.signatures)
    #print(morphs.processed_words)
    #print(morphs.prefixes)
    #print(morphs.stems)
    #print(morphs.suffixes)

    # Uncomment here to lax boundary
    # adjustment
    #morphs.readjust_boundary_one_split()

    #print(morphs.signatures)
    #print(morphs.processed_words)
    #print(morphs.prefixes)
    #print(morphs.stems)
    #print(morphs.suffixes)

    morphs.reprocess_2plus_words()

    #print(morphs.signatures)
    #print(morphs.processed_words)

    morphs.write()
    #print(morphs.prefixes)
    #print(morphs.stems)
    #print(morphs.suffixes)

    #print('total word count/vocab')
    #print(morphs.all_words)

# print(filenames)

# for filename in filenames:
#     with open(filename, 'rt') as f_in:
#
#         # process_tokens(f_in)
#         #process(filename, f_in)
#         morphs = SubWordUnits(f_in, filename)
#         morphs.process()
#         morphs.process_one_split()
#         #morphs.get_signature_one_split()
#         morphs.write_dicts()
#         print(morphs.signatures)


# pos = 0
# if stem_index > 0:
#
#     while pos < stem_index:
#         if morphs[pos] in self.prefixes:
#             signature += 'p'
#             pos += 1
#             while morphs[pos] in self.prefixes and os < number_of_morphs - 1:
#                 signature += 'p'
#                 pos += 1
#             if morphs[pos] in self.stems:
#                 signature += 's'
#             else:
#                 print
#

#
# for m in morphs:
#
#     if m in self.prefixes:
#         signature += 'p'
#
#         while elif m in self.stems:
#         signature += 's'
#
#     elif m in self.suffixes:
#         signature += 'e'
#
# if signature == 'p':

# print('all other words')
# for word in self.all_other_words:
#     print(word)
#

# Read segments files, process morphemes and assign to
# dictionary, and write to file

# morphs = word.rstrip().split()
# signature = ''

# # Find position (index i) of stem
# # if stem is already in dictionary
# number_of_morphs = len(morphs)
# stem_index = -1
# affix_index = -1
# for i in range(number_of_morphs):
#     if morphs[i] in self.stems or \
#                     morphs[i] in self.no_split_words:  # should consider no split here?
#         stem_index = i
#
# # No stem, find affixes and infer stem
# if stem_index < 0:
#     if morphs[0] in self.prefixes or morphs[1] in self.suffixes:
#         signature = 'p-s'
#     # elif stem_index < 0 and number_of_morphs == 2:
#     #     # for i in range(number_of_morphs):
#     # elif morphs[1] in self.suffixes:
#     #         # prefix_index = i
#     #     signature = 'p-s'
#
#     # Alter boundaries of morphs by one pos in order
#     # to guess new morpheme and check if in dictionaries
#     else:
#         word = ''.join(morphs)
#         i_m2 = len(morphs[0])  # pos of original morph 2 (m2)
#
#         # Try shifting boundary to left
#         new_m1 = word[:i_m2 - 1]  # indices of new first morph
#         new_m2 = word[i_m2 - 1:]  # indices of new second morph
#         # stem_index = -1
#         print("new m1: ", new_m1)
#         print("new m2: ", new_m2)
#         if new_m1 in self.stems or \
#                         new_m2 in self.suffixes or \
#                         new_m1 in self.no_split_words:  # ??
#             signature = 's-e'
#         elif new_m1 in self.prefixes or \
#                         new_m2 in self.stems or \
#                         new_m2 in self.no_split_words:  # ??
#             signature = 'p-s'
#
#         # Try shifting boundary to right
#         else:
#             new_m1 = word[:i_m2 + 1]  # indices of new first morph
#             new_m2 = word[i_m2 + 1:]  # indices of new second morph
#             if new_m1 in self.stems or \
#                             new_m2 in self.suffixes or \
#                             new_m1 in self.no_split_words:  # ??
#                 signature = 's-e'
#             elif new_m1 in self.prefixes or \
#                             new_m2 in self.stems or \
#                             new_m2 in self.no_split_words:  # ??
#                 signature = 'p-s'
#             else:
#                 signature = '?-?'  # unknown word
#                 new_m1, new_m2 = morphs[0], morphs[1]  # set boundaries back
#
#         morphs = [new_m1, new_m2]
#
# else:
#     if stem_index == 0:
#         signature = 's-e'
#     else:
#         signature = 'p-s'

# def get_signature_one_split(self):
#     # TODO:=
#     # Add regex here for single split
#     # and add sigs
#     # Then process all other words again check if in sig dict
#     # and add morphs and sigs
#     #
#
#     # print('all words')
#     # for word in self.all_words:
#     #     print(word)
#
#     print('other one split')
#     # Iterate through one split words and map to signature
#     # prefix-stem (p-s)
#     # stem-suffix (s-e)
#     for word in self.other_one_split_words:
#
#         print("orig word: ", word)
#         morphs = word.rstrip().split()
#         signature = ''
#
#         # Find position (index i) of stem
#         # if stem is already in dictionary
#         number_of_morphs = len(morphs)
#         stem_index = -1
#         affix_index = -1
#         for i in range(number_of_morphs):
#             if morphs[i] in self.stems or \
#                             morphs[i] in self.no_split_words:  # should consider no split here?
#                 stem_index = i
#
#         # No stem, find affixes and infer stem
#         if stem_index < 0:
#             if morphs[0] in self.prefixes or morphs[1] in self.suffixes:
#                 signature = 'p-s'
#             # elif stem_index < 0 and number_of_morphs == 2:
#             #     # for i in range(number_of_morphs):
#             # elif morphs[1] in self.suffixes:
#             #         # prefix_index = i
#             #     signature = 'p-s'
#
#             # Alter boundaries of morphs by one pos in order
#             # to guess new morpheme and check if in dictionaries
#             else:
#                 word = ''.join(morphs)
#                 i_m2 = len(morphs[0])  # pos of original morph 2 (m2)
#
#                 # Try shifting boundary to left
#                 new_m1 = word[:i_m2 - 1]  # indices of new first morph
#                 new_m2 = word[i_m2 - 1:]  # indices of new second morph
#                 # stem_index = -1
#                 print("new m1: ", new_m1)
#                 print("new m2: ", new_m2)
#                 if new_m1 in self.stems or \
#                                 new_m2 in self.suffixes or \
#                                 new_m1 in self.no_split_words:  # ??
#                     signature = 's-e'
#                 elif new_m1 in self.prefixes or \
#                                 new_m2 in self.stems or \
#                                 new_m2 in self.no_split_words:  # ??
#                     signature = 'p-s'
#
#                 # Try shifting boundary to right
#                 else:
#                     new_m1 = word[:i_m2 + 1]  # indices of new first morph
#                     new_m2 = word[i_m2 + 1:]  # indices of new second morph
#                     if new_m1 in self.stems or \
#                                     new_m2 in self.suffixes or \
#                                     new_m1 in self.no_split_words:  # ??
#                         signature = 's-e'
#                     elif new_m1 in self.prefixes or \
#                                     new_m2 in self.stems or \
#                                     new_m2 in self.no_split_words:  # ??
#                         signature = 'p-s'
#                     else:
#                         signature = '?-?'  # unknown word
#                         new_m1, new_m2 = morphs[0], morphs[1]  # set boundaries back
#
#                 morphs = [new_m1, new_m2]
#
#         else:
#             if stem_index == 0:
#                 signature = 's-e'
#             else:
#                 signature = 'p-s'
#
#         # Augment corresponding dictionaries
#         if signature == 'p-s':
#             self.prefixes.append(morphs[0])
#             self.stems.append(morphs[1])
#         elif signature == 's-e':
#             self.stems.append(morphs[0])
#             self.suffixes.append(morphs[1])
#
#         # Add signature (mapping) and update word counts
#         word = '-'.join(morphs)
#         self._word_counts[word] += 1
#         self.signatures[word] = signature
#         print("final word", word, signature)


# self.all_other_words = set([])
# prefixes = set([])
# stems = set([])
# self.suffixes = set([])


# def process_tokens(segments_file):
#     all_words = []
#     all_other_words = []
#     self.all_other_words = []
#     other_one_split_words = []
#     prefixes = []
#     stems = []
#     self.suffixes = []
#     for word in segments_file:
#         morphs = word.lower().rstrip().split()
#         if len(morphs) == 1:
#             no_split_words.add(morphs[0])
#         elif len(morphs) == 2:
#             m1 = morphs[0]
#             m2 = morphs[1]
#             if max(len(m1)/len(m2), len(m2)/len(m1)) >= 2:
#                 if len(m1) > len(m2):
#                     stem = m1
#                     suffix = m2
#                     stems.add(stem)
#                     self.suffixes.add(suffix)
#
#                 else:
#                     prefix = m1
#                     stem = m2
#                     prefixes.add(prefix)
#                     stems.add(stem)


# if match0:
                #     m = match0.group(0)
                #     print("no split: ", repr(m))
                #     self.no_split_words.append(m)

                # suffix, or stem dictionaries,
                # only if the size of one of the morphs is at least
                # twice as large as the other
                # elif match1:
                #     print("found one split")
                #     m1 = match1.group(1)
                #     print("m1: ", repr(m1))
                #
                #     m2 = match1.group(2)
                #     print("m2: ", repr(m2))
                #
                # # morphs = word.rstrip().split()
                # # if len(morphs) == 1:
                # #     self.all_other_words.add(morphs[0])
                # # elif len(morphs) == 2:
                # #     m1 = morphs[0]
                # #     m2 = morphs[1]
                #     if max(len(m1) / len(m2), len(m2) / len(m1)) >= 2:
                #         if len(m1) > len(m2):
                #             stem = m1
                #             suffix = m2
                #             # self.stems.add(stem)
                #             # self.suffixes.add(suffix)
                #             self.stems.append(stem)
                #             self.suffixes.append(suffix)
                #         else:
                #             prefix = m1
                #             stem = m2
                #             # self.prefixes.add(prefix)
                #             # self.stems.add(stem)
                #             self.prefixes.append(prefix)
                #             self.stems.append(stem)
                #
                #     else:   # affix not long enough
                #         self.other_one_split_words.append(word)      # add one-split word to process later
