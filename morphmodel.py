#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Class: MorphModel
Created on 07.05.17
@author: Eric Lief
"""

import regex as re
from collections import defaultdict

class MorphModel:
    """
    Class to process Morfessor segmented output and classify each
    segment as either a prefix, stem, surffix, or ? (unknown)

    In order to optimize the mapping of segments to each category,
    an algorithm has been implemnted which corrects the often incorrect
    Morfessor splits by shifting the boundary (leftward or rightward one
    segment) if an already occurring stem can be matched. For instance, if
    the output is 'un believa ble' and the suffix 'able' has already been
    seen, then the shift correction will be 'un belieb able'
    """

    def __init__(self, segments_file_in):

        self.segments_file_in = segments_file_in        # morfessor output file
        self.alphabetic_words = defaultdict(int)        # all seen words {word: count}
        self.prefixes = defaultdict(int)                # prefix dictionary {segment: count}
        self.stems = defaultdict(int)                   # stem dictionary {segment: count}
        self.suffixes = defaultdict(int)                # suffix dictionary {segment: count}
        self.unknown = defaultdict(int)                 # unknown (?) dictionary {segment: count}
        self.ambig_words = {}                           # dict of words with 1+ unknown segments
        self._signatures = defaultdict(list)            # the label of a word {signature: [words]}
        self.processed_words = set([])                  # set of all processed words
        self.shifted_words = {}                         # words shifted {orig_word: shifted_word}
        self.LABELS = {'p': 'prefixes', 's': 'stems', 'e': 'suffixes', '?': 'unknown'}
        self.changed_signature = {}                     # dict of words whose signature changed
        self.words_to_segments = {}                     # mapping of words to their splits

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

        Dictionaries are updated.
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

    def shift_boundary(self):
        """
        Shift/adjust boundary and try to
        force segmentation of previously undefined/
        unkown sequences, containing one or more ?s.

        All dictionaries are later updated.
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
                self.shifted_words[adj_word] = word
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
        if '?' not in cand_sig:
            return True

        return False

    def get_candidates(self, m1, m2, new_morphs):
        """
        Validate the potential shift.
        :param m1:
        :param m2:
        :param new_morphs:
        :return: boolean
        """

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


    @property
    def signatures(self):
        return self._signatures

    def segment_word(self, word):
        if word in self.words_to_segments:
            segments = self.words_to_segments[word]
            #print(segments)
        else:
            segments = [word]
        return segments

    def write(self):

        dict_file_suffix = self.segments_file_in[8:]
        abbrev_fn = self.segments_file_in[9:-3]

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
            for adj, orig in self.shifted_words.items():
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
                    if word in self.shifted_words:
                        word = self.shifted_words[word]    # lookup original word before adjustment
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


