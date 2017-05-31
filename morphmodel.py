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

class MorphModel:
    def __init__(self, segments_file_in):

        # self.filename = filename_in
        self.segments_file_in = segments_file_in
        self.alphabetic_words = defaultdict(int)       # {word: count}
        self.words = []
        self.all_other_words = []
        self.no_split_words = []
        self.other_one_split_words = []
        self.prefixes = defaultdict(int)
        self.stems = defaultdict(int)
        self.suffixes = defaultdict(int)
        self.unknown = defaultdict(int)
        self.ambig_words = {}
        self._word_counts = defaultdict(int)
        self._signatures = defaultdict(list)    # {signature: [words]}
        self.processed_words = set([])
        self.adjusted_words = {}                # {orig_word: adjusted_word}
        self.LABELS = {'p': 'prefixes', 's': 'stems', 'e': 'suffixes', '?': 'unknown'}
        self.changed_signature = {}
        self.words_to_segments = {}

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
            for split_word in f:

                # Skip whitespace
                if re.match(W, split_word):
                    continue

                # Are we dealing with an alphabetic word of acceptable format?
                match = re.match(p, split_word)
                if not match:
                    continue

                # Preprocess/normalize string:
                # remove spaces and capitalization
                split_word = split_word.lower()
                orig_word = ''.join(split_word.split())
                split_word = '-'.join(split_word.split())

                # Hyphenate segments, e.g.
                # dis regard -> dis-regard
                self.alphabetic_words[split_word] += 1       # total count of seen words

                # Already seen word, skip?
                if split_word in self.processed_words:
                    continue

                morphs = split_word.split('-')
                max_len_morph = max(morphs, key=len)  # this is stem
                max_len = len(max_len_morph)

                # Check if stem is 2X size of all other morphs in word
                is_stem_2X = True
                for m in morphs:
                    if m != max_len_morph and max(len(m) / max_len, max_len / len(m)) < 2:
                        is_stem_2X = False

                signature = ''
                if is_stem_2X:
                    #print('stem is 2X for ', morphs)
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

                    # Add word to lists of processed words
                    self.signatures[signature].append(split_word)
                    self.processed_words.add(split_word)
                    self.words_to_segments[orig_word] = morphs
                    #print(split_word, morphs)

        #print('processed words ', self.processed_words)

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

    def reprocess_known_one_split(self):

        # one split non-numeric morphs only
        p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)

        # Iterate through one split words and map to signature
        # prefix-stem (p-s)
        # stem-suffix (s-e)

        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                word = word.lower()

                # Already seen word, skip
                if word in self.processed_words:
                    continue

                # Find 1-split words and add morphs to either prefix, suffix, etc.
                match1 = re.search(p1, word)

                if match1:
                    #2Aprint("found new one split")
                    m1 = match1.group(1)
                    #print("m1: ", repr(m1))

                    m2 = match1.group(2)
                    #print("m2: ", repr(m2))

                    morphs = [m1, m2]
                    hyphen_word = '-'.join(morphs)
                    if m1 in self.prefixes or m2 in self.stems:
                        self.signatures['p-s'].append(hyphen_word)
                        self.processed_words.add(word)
                        self.prefixes[m1] += 1
                        self.stems[m2] += 1
                        #print("found new p-s")

                    elif m1 in self.stems or m2 in self.suffixes:
                        self.signatures['s-e'].append(hyphen_word)
                        self.processed_words.add(word)
                        self.stems[m1] += 1
                        self.suffixes[m2] += 1
                        #print("found new s-e")

    def reprocess(self):

        # Alphabetic/on-numeric morphs only
        p = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+\s)+$", re.M)
        # Whitespace
        W = re.compile("^\s+$")

        with open(self.segments_file_in, 'rt') as f:
            for split_word in f:

                # Skip whitespace
                if re.match(W, split_word):
                    continue

                # Are we dealing with an alphabetic word of acceptable format?
                match = re.match(p, split_word)
                if not match:
                    continue

                # Preprocess/normalize string:
                # remove spaces and capitalization
                split_word = split_word.lower()
                morphs = split_word.split()
                orig_word = ''.join(morphs)
                split_word = '-'.join(morphs)

                # Already seen word, skip
                if split_word in self.processed_words:
                    #print('skipping ', word)
                    continue

                # Get the signature of the morphs
                #morphs = match[0].split()
                morphs = split_word.split('-')

                #print('reproc morphs', morphs)
                signature = self.add_signature(morphs)

                # Update data structs/Add word to list of processed words
                self.signatures[signature].append(split_word)
                self.processed_words.add(split_word)
                #w = Word(orig_word, morphs, signature)
                self.words_to_segments[orig_word] = morphs

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
        a sequence of morphemes and then
        add the segments to their respective
        dictionaries (as previous method does)
        :param morphs:
        :return: signature
        """

        signature = ''
        word = '-'.join(morphs)
        n = len(morphs)
        for i, m in enumerate(morphs):
            if m in self.prefixes and \
                    's' not in signature and \
                    'e' not in signature and \
                    i < n - 1:
                self.prefixes[m] += 1
                signature += '-p' if signature else 'p'
            elif m in self.suffixes and \
                    i != 0:
                self.suffixes[m] += 1
                signature += '-e' if signature else 'e'
            elif m in self.stems and \
                    'e' not in signature:
                self.stems[m] += 1
                signature += '-s' if signature else 's'
            else:  # morph not known, so mark with '?'
                signature += '-?' if signature else '?'
                self.unknown[m] += 1

        # Check if no stem present in signature.
        # If so, check if any morphs may also be stems,
        # and if so, reconstruct signature with the alternate
        # stem label(s), updating the dictionary.
        if 's' not in signature:
            # print("no stem present for ", morphs)
            # print('orig sig', signature)

            labels = signature.split('-')
            n = len(labels)     # number of labels/length of signature
            new_sig = ''
            has_stem = False
            for i in range(n):
                m = morphs[i]           # current morph
                label = self.LABELS[labels[i]]       # expand label name
                prefix_to_right = False
                for j in range(i + 1, n):
                    other_label = labels[j]
                    if 'p' in other_label and 's' not in other_label:
                        prefix_to_right = True
                        # print("prefix to rt for ", word)
                if not has_stem and m in self.stems and not prefix_to_right:

                    # Change label to stem
                    # if not prefix_to_right:

                    #print('adding stem ', m)
                    new_sig += '-s' if new_sig else 's'
                    self.stems[m] += 1  # add to stems dict
                    has_stem = True

                    #print(SubWordUnits.__getattribute__(self, label))

                    dict_ref = MorphModel.__getattribute__(self, label)
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

            #print('new sig', new_sig)

            # if not has_stem:
            #     new_sig = 'no-stem'
            # self.changed_signature[word] = signature + '->' + new_sig

            signature = new_sig

        # Count unknowns ('?') in signature
        cnt = 0
        for ch in signature:
            if ch == '?':
                cnt += 1

        # Add to list of unknown/ambiguous words
        if cnt >= 1:
            self.ambig_words[word] = signature

            # # TODO: Change the signature to indeterminate if more than three '?s' ???
            # if cnt > 3:
            #     new_sig = 'indeter'
            #     self.changed_signature[word] = signature + '    ->    ' + new_sig
            #


        # # Count unknowns ('?') in signature
        # cnt = 0
        # for ch in signature:
        #     if ch == '?':
        #         cnt += 1
        #
        # if cnt > 3:
        #     signature = 'indeter'

        # print('final added sig', signature)
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
        #word = '-'.join(morphs)
        n = len(morphs)
        for i, m in enumerate(morphs):
            if m in self.prefixes and \
                            's' not in signature and \
                            'e' not in signature:
                signature += '-p' if signature else 'p'
                # print('prefix ', m)
            elif m in self.suffixes and \
                            i != 0:
                signature += '-e' if signature else 'e'

                # print('suffix ', m)
            elif m in self.stems and \
                            'e' not in signature:
                signature += '-s' if signature else 's'
                # print('stem ', m)

            else:  # morph not known, so mark with '?'
                signature += '-?' if signature else '?'

        # if 's' not in signature:
        #     signature = 'no-stem'

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

    def shift_boundary(self):
        """
        Shift/adjust boundary and try to
        force segmentation of previously undefined/
        unkown sequences, containing one or more ?s.
        :return:
        """
        #print('adjusting boundary')
        #print(self.ambig_words)
        #print(self.unknown)

        ambig = list(self.ambig_words.keys())
        #print(ambig)
        for word in ambig:
            #print(word)
            old_morphs = word.split('-')
            # print(old_morphs)
            n = len(old_morphs)
            #word = ''.join(morphs)
            new_morphs = [old_morphs[0]]
            has_shift = False
            for i in range(0, n - 1):
                # print("new interation: ", new_morphs)

                is_valid = False
                # Original morphs
                m1 = new_morphs.pop()
                m2 = old_morphs[i + 1]
                # print("old m1: ", m1)
                # print("old m2: ", m2)
                # print(new_morphs)

                # Do not alter if the signature if the current
                # candidate morphs is valid
                # if m1 not in self.unknown and m2 not in self.unknown:
                #candidates = new_morphs + [m1, m2]
                candidates = self.get_candidates(m1, m2, new_morphs)
                if self.valid_shift(candidates[:-1]):
                    new_morphs = list(candidates)
                    is_valid = True
                    continue
                #cand_sig = self.get_signature(candidates)
                #
                # print(candidates, cand_sig)
                # if '?' not in cand_sig:
                #     new_morphs = list(candidates)
                #     continue

                # Otherwise, shift morpheme boundary left
                # print('shifting left')
                has_shift = True
                new_m1 = m1 + m2[0]
                new_m2 = m2[1:]
                # print("new m1: ", new_m1)
                # print("new m2: ", new_m2)

                # candidates = new_morphs + [new_m1, new_m2]

                # Get candidates
                candidates =self.get_candidates(new_m1, new_m2, new_morphs)
                # Is this a valid shift (are both morphs now known)?
                # If so, do shift and add both morphs to the stack
                if self.valid_shift(candidates[:-1]):
                    is_valid = True
                    new_morphs = list(candidates)
                    continue

                # Otherwise, try shifting right
                # print('shifting rt')
                new_m1 = m1[:-1]
                new_m2 = m1[-1] + m2
                # print("new m1: ", new_m1)
                # print("new m2: ", new_m2)

                # Get candidates
                candidates =self.get_candidates(new_m1, new_m2, new_morphs)
                # print('last chance for cands ', candidates)

                # Is this a valid shift (are both morphs now known)?
                # If so, do shift and add both morphs to the stack

                new_morphs = list(candidates)
                if self.valid_shift(candidates[:-1]):
                    is_valid = True
                    # print('is valid for ', new_morphs)
                    continue

                # Otherwise, keep old morphs and abort for this word
                else:
                    # print('aborting shift')
                    break


            if has_shift and is_valid and self.valid_shift(new_morphs):


                # Add new signature, update dicts
                new_signature = self.get_signature(new_morphs)
                adj_word = '-'.join(new_morphs)
                orig_word = ''.join(new_morphs)
                word_count = self.alphabetic_words[word]
                # print('a valid shift found for ', new_morphs)
                # print("final word", adj_word, new_signature)

                self.signatures[new_signature].append(adj_word)
                self.adjusted_words[adj_word] = word
                self.alphabetic_words[adj_word] = word_count
                self.words_to_segments[orig_word] = new_morphs

                new_labels = new_signature.split('-')
                n = len(new_labels)
                for i in range(n):
                    m = new_morphs[i]  # current morph
                    label = self.LABELS[new_labels[i]]  # expand label name
                    dict_ref = MorphModel.__getattribute__(self, label)
                    dict_ref[m] += word_count

                # Delete old signature
                old_signature = self.ambig_words[word]
                dict_list_ref = self.signatures[old_signature]
                dict_list_ref.remove(word)
                if len(dict_list_ref) == 0:
                    del dict_list_ref
                del self.ambig_words[word]

                # Delete old morphs from respective dicts
                del self.alphabetic_words[word]
                old_labels = old_signature.split('-')
                # print(old_labels)
                n = len(old_labels)  # number of labels/length of signature
                for i in range(n):
                    m = old_morphs[i]  # current morph
                    label = self.LABELS[old_labels[i]]  # expand label name

                    # print(SubWordUnits.__getattribute__(self, label))

                    dict_ref = MorphModel.__getattribute__(self, label)
                    cur_morf_cnt = dict_ref[m]
                    # print('removing label ', label)
                    # print(cur_morf_cnt)
                    # print(dict_ref)

                    if cur_morf_cnt > 1:  # update dict for old label
                        # print('decrem')
                        # cur_morf_cnt -= 1
                        # SubWordUnits.__setattr__(self, label, cur_morf_cnt - 1)
                        dict_ref[m] -= word_count
                    else:
                        # del self.stems[m]
                        # print('deleting')
                        del dict_ref[m]

    def valid_shift(self, candidates):
        """
        Validate the potential shift.
        :param m1:
        :param m2:
        :param new_morphs:
        :return: boolean
        """

        cand_sig = self.get_signature(candidates)
        #print(candidates, cand_sig)
        if '?' not in cand_sig:
            return True

        return False

        #continue


        # elif not m2 and m1 not in self.unknown:
        #     new_morphs.append(m1)
        #     return True
        #
        # # If both morphs are not known, both are valid
        # elif not (m1 in self.unknown and m2 in self.unknown):
        #     print('m1 and m2 not in unkown')
        #     new_morphs.extend([m1, m2])
        #     return True
        #
        # return False

    def get_candidates(self, m1, m2, new_morphs):
        """
        Validate the potential shift.
        :param m1:
        :param m2:
        :param new_morphs:
        :return: boolean
        """

        # #candidates = new_morphs + [m1, m2]
        # cand_sig = self.get_signature(candidates)
        # print(candidates, cand_sig)
        # if '?' not in cand_sig:
        #     new_morphs = list(candidates)
        #     continue

        # If m1 or m2 is an empty string '' and the other
        # morph is not unknown, keep the adjustment/shift
        if m1:
            if m2:
                candidates = new_morphs + [m1, m2]
            else:
                candidates = new_morphs + [m1]
        else:
            if m2:
                candidates = new_morphs + [m2]
        # print('cands ', candidates)
        return candidates


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


    @property
    def word_counts(self):
        return self._word_counts

    def segment_word(self, word):
        if word in self.words_to_segments:
            segments = self.words_to_segments[word]
            #print(segments)
        else:
            segments = [word]
        return segments

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
        abbrev_fn = self.segments_file_in[9:-3]
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

        # Write shifted
        with open('shifted' + dict_file_suffix, 'w') as f_out:
            for adj, orig in self.adjusted_words.items():
                f_out.write(adj + '\t' + orig + '\n')

        # Write changed log
        with open('changed' + dict_file_suffix, 'w') as f_out:
            for word, signature_change in self.changed_signature.items():
                f_out.write(word + '\t\t' + signature_change + '\n')

        # Write signature (mapping)
        with open('signatures' + dict_file_suffix, 'w') as f_out:
            for signature, words in self.signatures.items():
                f_out.write('\n')
                f_out.write(str(signature) + '(' + str(words) + ')' + '\n')

        # Write lexicon (all words)
        with open('dictionary' + dict_file_suffix, 'w') as f_out:
            for word, freq in self.alphabetic_words.items():
                f_out.write(word + '\t' + str(freq) + '\n')

        # Write stats, type and token frequency-based
        with open('stats-type' + dict_file_suffix, 'w') as f_out:
            V = len(self.alphabetic_words)         # vocab size
            f_out.write('1' + '\t' + abbrev_fn + '\n')
            for signature, words in self.signatures.items():
                counts = len(words)
                freq = round(counts / V, 3)
                #f_out.write(str(counts) + '\t' + str(freq) + '\t' + signature + '\n')
                f_out.write(str(freq) + '\t' + signature + '\n')
                #f_out.write('raw count: ' + str(n) + '\n')
                #f_out.write('out of total: ' + str(N) + '\n')
                #f_out.write('frequency: ' + str(freq) + '\n\n')
                #print(signature, V)

        with open('stats-token' + dict_file_suffix, 'w') as f_out:
            N = sum(self.alphabetic_words.values())     # text size/number of tokens
            # print('total tokens', N)
            f_out.write('1' + '\t' + abbrev_fn + '\n')
            for signature, words in self.signatures.items():
                counts = 0
                for word in words:
                    if word in self.adjusted_words:
                        word = self.adjusted_words[word]    # lookup original word before adjustment
                    counts += self.alphabetic_words[word]
                #print(signature, counts)
                #counts = sum([self.all_words[w] for w in words])
                #raw_cnt = len(words)
                freq = round(counts / N, 3)
                #f_out.write('\n')
                f_out.write(str(freq) + '\t' + signature + '\n')
                #f_out.write(str(counts) + '\t' + str(freq) + '\t' + signature + '\n')
                #f_out.write('raw count: ' + str(n) + '\n')
                #f_out.write('out of total: ' + str(N) + '\n')
                #f_out.write('frequency: ' + str(freq) + '\n\n')


