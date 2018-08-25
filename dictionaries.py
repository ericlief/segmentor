
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


class SubWordUnits:
    def __init__(self, segments_file_in):

        # self.filename = filename_in
        self.segments_file_in = segments_file_in
        self.all_words = defaultdict(int)
        self.all_other_words = []
        self.no_split_words = []
        self.other_one_split_words = []
        self.prefixes = defaultdict(int)
        self.stems = defaultdict(int)
        self.suffixes = defaultdict(int)
        self._word_counts = defaultdict(int)
        self._signatures = defaultdict(list)
        self.processed_words = set([])

    def process(self):

        # no split non-numeric morphs only
        p0 = re.compile("^[^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+$", re.M)
        # one split non-numeric morphs only
        p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)
        # 2 plus non-numeric morphs only
        p2p = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+\s)+$", re.M)

        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                # Preprocess/normalize string:
                # remove spaces and capitalization
                word = word.lower()
                orig_word = '-'.join(word.split())
                self.all_words[orig_word] += 1       # total count of words

                # Already seen word, skip?
                if word in self.processed_words:
                    continue
                #
                # # Find no-split words and add to dictionary
                # match0 = re.search(p0, word)
                #
                # # Find 1-split words and add morphs to either prefix,
                # match1 = re.search(p1, word)

                # Find all split and non-split words
                match2p = re.match(p2p, word)


                if match2p:
                    #print("2+ split?")
                    # groups = match2p.groups()
                    # size = len(groups)
                    # s = ''
                    # print(size)
                    # print(match2p[0])
                    morphs = match2p[0].split()
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
                        hyphen_word = '-'.join(morphs)
                        self.signatures[signature].append(hyphen_word)
                        self.processed_words.add(word)

            # print(self.signatures)
            # print(self.processed_words)

            # print(morphs)
            # for i in range(size):
            #     s += '{1[{%d}]} ' % i
            # print(s)
            # for m in groups:
            #     print(m)
            #     print("2+ split?")
            # print(m.expandf(s))

            # else:
            #     self.all_other_words.append(word)


            # elif len(morphs) == 1:
            #     self.all_other_words.add(word.rstrip().split()[0])


            # get_signature(self.all_words, self.all_other_words, no_split_words, self.other_one_split_words,
            #               self.prefixes, self.stems,self.suffixes)
            #
            # write_dicts(self.all_words, self.all_other_words, no_split_words, self.other_one_split_words,
            #               self.prefixes, stems,self.suffixes)

    def process_known_one_split(self):
        # TODO:=
        # Add regex here for single split
        # and add sigs???
        # Then process all other words again check if in sig dict
        # and add morphs and sigs
        #

        #print('processing one split')

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
        # TODO:=
        # Add regex here for single split
        # and add sigs???
        # Then process all other words again check if in sig dict
        # and add morphs and sigs
        #

        #print('reprocessing one split')

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

    def reprocess_2plus_words(self):

        # one split non-numeric morphs only
        p2p = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+\s)+$", re.M)

        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                word = word.lower()

                # Already seen word, skip
                if word in self.processed_words or word == '\n':
                    continue

                # Find 2+ split words and add morphs to either prefix,
                match2p = re.match(p2p, word)

                if match2p:
                    #print("2+ split?")
                    # groups = match2p.groups()
                    # size = len(groups)
                    # s = ''
                    # print(size)
                    # print(match2p[0])
                    morphs = match2p[0].split()
                    #print(morphs)

                    signature = ''
                    for m in morphs:
                        if m in self.prefixes and \
                            's' not in signature and 'e' not in signature:
                            # self.prefixes.append(m)
                            self.prefixes[m] += 1
                            signature += '-p' if signature else 'p'
                            #print('prefix ', m)
                        elif m in self.suffixes:
                            # self.suffixes.append(m)
                            self.suffixes[m] += 1
                            signature += '-e' if signature else 'e'

                            #print('suffix ', m)
                        elif m in self.stems and \
                             'e' not in signature:
                            # self.stems.append(m)
                            self.stems[m] += 1
                            signature += '-s' if signature else 's'
                           # print('stem ', m)

                        else:       # morph not known, so mark with '?'
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
                    #print(cnt)
                    # Add word to list of processed words
                    hyphen_word = '-'.join(morphs)
                    self.signatures[signature].append(hyphen_word)
                    self.processed_words.add(word)



    def adjust_boundary_one_split(self):
        # TODO:=
        # Add regex here for single split
        # and add sigs???
        # Then process all other words again check if in sig dict
        # and add morphs and sigsv
        #

        #print('adjusting boundary for one split')

        # one split non-numeric morphs only
        p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)

        # Iterate through one split words and map to signature
        # prefix-stem (p-s)
        # stem-suffix (s-e)

        # for word in self.segments_file_in:
        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                # Already seen word, skip
                if word in self.processed_words:
                    continue

                raw_word = word.lower()

                # Find 1-split words and add morphs to either prefix, suffix, etc.
                match1 = re.search(p1, word)

                if match1:
                    #print("found new one split")
                    m1 = match1.group(1)
                    #print("m1: ", repr(m1))

                    m2 = match1.group(2)
                    #print("m2: ", repr(m2))

                    morphs = [m1, m2]
                    word = ''.join(morphs)
                    i_m2 = len(m1)  # pos of original morph 2 (m2)
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

                    # Try shifting boundary to right
                    else:
                        #print("shifting boundary right")

                        new_m1 = word[:i_m2 + 1]  # indices of new first morph
                        new_m2 = word[i_m2 + 1:]  # indices of new second morph
                        #print("new m1: ", new_m1)
                        #print("new m2: ", new_m2)
                        if new_m1 in self.stems and \
                           new_m2 in self.suffixes:
                            signature = 's-e'
                        elif new_m1 in self.prefixes and \
                             new_m2 in self.stems:
                            signature = 'p-s'
                        else:
                            signature = '?-?'  # unknown word
                            new_m1, new_m2 = morphs[0], morphs[1]  # set boundaries back

                    morphs = [new_m1, new_m2]
                    hyphen_word = '-'.join(morphs)

                    # Augment corresponding dictionaries
                    if signature == 'p-s':
                        self.prefixes[new_m1] += 1
                        self.stems[new_m2] += 1
                        self._signatures['p-s'].append(hyphen_word)
                        self.processed_words.add(raw_word)

                        #print("found new p-s")

                    elif signature == 's-e':
                        self.stems[new_m1] += 1
                        self.suffixes[new_m2] += 1
                        self.signatures['s-e'].append(hyphen_word)
                        self.processed_words.add(raw_word)

                       # print("found new s-e")

                    # TODO: ???? words: should we add or reprocess????
                    # else:
                    #     self._signatures['?-?'].append(hyphen_word)
                    #     self.processed_words.add(word)


                   # print("final word", hyphen_word, signature)


    def readjust_boundary_one_split(self):
        # TODO:= relax restriction that both morphs be in dictionary
        # after adjusting boundary

        #print('readjusting one split')

        # one split non-numeric morphs only
        p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*/]+)$", re.M)

        # Iterate through one split words and map to signature
        # prefix-stem (p-s)
        # stem-suffix (s-e)

        # for word in self.segments_file_in:
        with open(self.segments_file_in, 'rt') as f:
            for word in f:

                # Already seen word, skip
                if word in self.processed_words:
                    continue

                raw_word = word.lower()

                # Find 1-split words and add morphs to either prefix, suffix, etc.
                match1 = re.search(p1, word)

                if match1:
                    #print("found new one split")
                    m1 = match1.group(1)
                    #print("m1: ", repr(m1))

                    m2 = match1.group(2)
                    #print("m2: ", repr(m2))

                    morphs = [m1, m2]
                    word = ''.join(morphs)
                    i_m2 = len(m1)  # pos of original morph 2 (m2)
                    signature = ''

                    # Try shifting boundary to left
                    #print("shifting boundary left")

                    new_m1 = word[:i_m2 - 1]  # indices of new first morph
                    new_m2 = word[i_m2 - 1:]  # indices of new second morph
                    # stem_index = -1
                    #print("new m1: ", new_m1)
                    #print("new m2: ", new_m2)
                    if new_m1 in self.stems or \
                       new_m2 in self.suffixes:
                        signature = 's-e'
                    elif new_m1 in self.prefixes or \
                         new_m2 in self.stems:
                        signature = 'p-s'

                    # Try shifting boundary to right
                    else:
                        #print("shifting boundary right")

                        new_m1 = word[:i_m2 + 1]  # indices of new first morph
                        new_m2 = word[i_m2 + 1:]  # indices of new second morph
                        #print("new m1: ", new_m1)
                        #print("new m2: ", new_m2)
                        if new_m1 in self.stems or \
                           new_m2 in self.suffixes:
                            signature = 's-e'
                        elif new_m1 in self.prefixes or \
                             new_m2 in self.stems:
                            signature = 'p-s'
                        else:
                            signature = '?-?'  # unknown word
                            new_m1, new_m2 = morphs[0], morphs[1]  # set boundaries back

                    morphs = [new_m1, new_m2]
                    hyphen_word = '-'.join(morphs)

                    # Augment corresponding dictionaries
                    if signature == 'p-s':
                        self.prefixes[new_m1] += 1
                        self.stems[new_m2] += 1
                        self._signatures['p-s'].append(hyphen_word)
                        self.processed_words.add(raw_word)

                        #print("found new p-s")

                    elif signature == 's-e':
                        self.stems[m1] += 1
                        self.suffixes[m2] += 1
                        self.signatures['s-e'].append(hyphen_word)
                        self.processed_words.add(raw_word)

                       # print("found new s-e")

                    # TODO: ???? words: should we add or reprocess????
                    # else:
                    #     self._signatures['?-?'].append(hyphen_word)
                    #     self.processed_words.add(word)


                   # print("final word", hyphen_word, signature)


    @property
    def signatures(self):
        return self._signatures


    @ property
    def word_counts(self):
        return self._word_counts


    def write_dicts(self):
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

        # Write signature (mapping)
        with open('signatures' + dict_file_suffix, 'w') as f_out:
            for signature, words in self.signatures.items():
                f_out.write('\n')
                f_out.write(str(signature) + '(' + str(words) + ')' + '\n')

        # Write lexicon (all words)
        with open('dictionary' + dict_file_suffix, 'w') as f_out:
            for word, freq in self.all_words.items():
                f_out.write(word + '\t' + str(freq) + '\n')


        # Write stats
        with open('stats' + dict_file_suffix, 'w') as f_out:
            for signature, words in self.signatures.items():
                N = len(self.all_words)
                raw_cnt = len(words)
                freq = round(raw_cnt / N, 2)
                #f_out.write('\n')
                f_out.write(str(raw_cnt) + '\t' + str(freq) + '\t' + signature + '\n')
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
    morphs.process_known_one_split()
    #print(morphs.signatures)
    #print(morphs.processed_words)
    #print(morphs.prefixes)
    #print(morphs.stems)
    #print(morphs.suffixes)
    morphs.adjust_boundary_one_split()
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

    morphs.write_dicts()
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


# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
#
# """
# Project: segmentor
# Created on 07.05.17
# @author: Eric Lief
# """
#
#
# import sys
# import os
# import glob
# import regex as re
#
# # no_split_words = set([])
# # prefixes = set([])
# # stems = set([])
# # suffixes = set([])
#
#
# # def process_tokens(segments_file):
# #     all_words = []
# #     all_other_words = []
# #     no_split_words = []
# #     other_one_split_words = []
# #     prefixes = []
# #     stems = []
# #     suffixes = []
# #     for word in segments_file:
# #         morphs = word.lower().rstrip().split()
# #         if len(morphs) == 1:
# #             no_split_words.add(morphs[0])
# #         elif len(morphs) == 2:
# #             m1 = morphs[0]
# #             m2 = morphs[1]
# #             if max(len(m1)/len(m2), len(m2)/len(m1)) >= 2:
# #                 if len(m1) > len(m2):
# #                     stem = m1
# #                     suffix = m2
# #                     stems.add(stem)
# #                     suffixes.add(suffix)
# #
# #                 else:
# #                     prefix = m1
# #                     stem = m2
# #                     prefixes.add(prefix)
# #                     stems.add(stem)
#
# class SubWordUnits:
#     def __init__(self):
#
#
#         self.all_words = []
#         all_other_words = []
#         no_split_words = []
#         other_one_split_words = []
#         prefixes = []
#         stems = []
#         suffixes = []
#
# def process(filename, segments_file_in):
#     # self.all_words = []
#     # all_other_words = []
#     # no_split_words = []
#     # other_one_split_words = []
#     # prefixes = []
#     # stems = []
#     # suffixes = []
#
#     # no split non-numeric morphs only
#     p0 = re.compile("^[^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*]+$", re.M)
#     # one split non-numeric morphs only
#     p1 = re.compile("^([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*]+) ([^0-9_\-@#\$\*<>»¿\s\”\"\'\.%\$#@!\^\*]+)$", re.M)
#
#     for word in segments_file_in:
#         self.all_words.append(word)
#         word = word.lower()
#
#         # Find no-split words and add to dictionary
#         r0 = re.search(p0, word)
#
#         # Find 1-split words and add morphs to either prefix,
#         r1 = re.search(p1, word)
#
#         if r0:
#             m = r0.group(0)
#             print("no split: ", repr(m))
#             no_split_words.append(m)
#             #continue
#             # no_split_words.add(m)
#
#         # suffix, or stem dictionaries,
#         # only if the size of one of the morphs is at least
#         # twice as large as the other
#         elif r1:
#             print("found one split")
#             m1 = r1.group(1)
#             print("m1: ", repr(m1))
#
#             m2 = r1.group(2)
#             print("m2: ", repr(m2))
#
#         # morphs = word.rstrip().split()
#         # if len(morphs) == 1:
#         #     no_split_words.add(morphs[0])
#         # elif len(morphs) == 2:
#         #     m1 = morphs[0]
#         #     m2 = morphs[1]
#             if max(len(m1) / len(m2), len(m2) / len(m1)) >= 2:
#                 if len(m1) > len(m2):
#                     stem = m1
#                     suffix = m2
#                     # stems.add(stem)
#                     # suffixes.add(suffix)
#                     stems.append(stem)
#                     suffixes.append(suffix)
#                 else:
#                     prefix = m1
#                     stem = m2
#                     # prefixes.add(prefix)
#                     # stems.add(stem)
#                     prefixes.append(prefix)
#                     stems.append(stem)
#
#             else:   # affix not long enough
#                 other_one_split_words.append(word)      # add one-split word to process later
#
#         else:
#             all_other_words.append(word)
#         # elif len(morphs) == 1:
#         #     no_split_words.add(word.rstrip().split()[0])
#
#         get_signature(all_words, all_other_words, no_split_words, other_one_split_words,
#                       prefixes, stems,suffixes)
#
#         write_dicts(all_words, all_other_words, no_split_words, other_one_split_words,
#                       prefixes, stems,suffixes)
#
#
# def write_dicts(segments_filename, all_words, all_other_words, no_split_words, other_one_split_words,
#                 prefixes, stems, suffixes):
#
#     # # Get all segments files
#     # filenames = glob.glob('segments-*')
#     # # print(filenames)
#     #
#     # for filename in filenames:
#     #     with open(filename, 'rt') as f_in:
#     #
#     #         # process_tokens(f_in)
#     #         process(f_in)
#
#     dict_file_suffix = segments_filename[8:]
#
#     # Write no split
#     with open('no-split' + dict_file_suffix, 'w') as f_out:
#         for w in no_split_words:
#             f_out.write(str(w) + '\n')
#
#     # Write stems
#     with open('stems' + dict_file_suffix, 'w') as f_out:
#         for w in stems:
#             f_out.write(str(w) + '\n')
#
#     # Write prefixes
#     with open('prefixes' + dict_file_suffix, 'w') as f_out:
#         for w in prefixes:
#             f_out.write(str(w) + '\n')
#
#     # Write suffixes
#     with open('suffixes' + dict_file_suffix, 'w') as f_out:
#         for w in suffixes:
#             f_out.write(str(w) + '\n')
#
#
# def get_signature(all_words, all_other_words, no_split_words, other_one_split_words,
#                   prefixes, stems, suffixes):
#
#     # print('all words')
#     # for word in all_words:
#     #     print(word)
#
#     print('other one split')
#     for word in other_one_split_words:
#
#         print(word)
#         morphs = word.rstrip().split()
#         word = ''.join(morphs)
#         signature = ''
#
#         # Find position (index i) of stem
#         number_of_morphs = len(morphs)
#         stem_index = -1
#         for i in range(number_of_morphs):
#             if morphs[i] in stems:
#                 stem_index = i
#
#
#         pos = 0
#         if stem_index > 0:
#
#             while pos < stem_index:
#                 if morphs[pos] in prefixes:
#                     signature += 'p'
#                     pos += 1
#                     while morphs[pos] in prefixes and os < number_of_morphs - 1:
#                         signature += 'p'
#                         pos += 1
#                     if morphs[pos] in stems:
#                         signature += 's'
#                     else:
#                         print
#
#
#         # for m in morphs:
#         #
#         #     if m in prefixes:
#         #         signature += 'p'
#         #
#         #         while elif m in stems:
#         #         signature += 's'
#         #
#         #     elif m in suffixes:
#         #         signature += 'e'
#         #
#         # if signature == 'p':
#
#         print('all other words')
#         for word in all_other_words:
#             print(word)
#
#
#     # Read segments files, process morphemes and assign to
#     # dictionary, and write to file
#
#
# # Get all segments files
# filenames = glob.glob('segments-*')
# # print(filenames)
#
# for filename in filenames:
#     with open(filename, 'rt') as f_in:
#
#         # process_tokens(f_in)
#         process(filename, f_in)
#
