#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Class: MorphModel
Created on 07.05.17
Mofified on 30.08.18
@author: Eric Lief
"""

import re
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
        First step:
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
                
                # Now do a preliminary annotation (signature) of segments according to their relative
                # position wrt the stem (e.g. prefix before, suffix after)
                signature = ''
                if is_stem_2X:
                    max_i = morphs.index(max_len_morph)
                    for i, m in enumerate(morphs):
                        if i < max_i:
                            self.prefixes[m] += 1
                            signature += '-p' if signature else 'p'
                        elif i > max_i:
                            self.suffixes[m] += 1
                            signature += '-e' if signature else 'e'
                        else:
                            self.stems[m] += 1
                            signature += '-s' if signature else 's'

                    # Add word to lists of processed words
                    self.signatures[signature].append(split_word)
                    self.processed_words.add(split_word)
                    self.words_to_segments[orig_word] = morphs

    def reprocess(self):
        """
        This second post-processing step tries 
        to identify the segments skipped in the first step, i.e.
        those with a stem not meeting the minimum size requirements.
        """
        
        # Alphabetic/non-numeric morphs only
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
                    continue
                
                # Get the signature of the morphs
                morphs = split_word.split('-')

                # Reprocess morphs not seen yet
                signature = self.add_signature(morphs)

                # Update data structs/Add word to list of processed words
                self.signatures[signature].append(split_word)
                self.processed_words.add(split_word)
                #w = Word(orig_word, morphs, signature)
                self.words_to_segments[orig_word] = morphs

    def add_signature(self, morphs):
        """
        Get signature (morpheme labels) of
        a sequence of morphemes and then
        add the segments to their respective
        dictionaries (as previous method does).
        
        Words with no apparent stem are also repaired 
        if possible.
        
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
        # If so, check if any morphs may also be stems by checking
        # if they are in the stem dictionary (added in the first pass from 
        # words with large enough stems.
        # Then reconstruct signature with the alternate
        # stem label(s) if the word would be wellformed, updating the dictionaries.
        if 's' not in signature:
    
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
                if not has_stem and m in self.stems and not prefix_to_right:

                    # Change label to stem if no prefix_to_right
                    # since we do not permit ..s-p..

                    new_sig += '-s' if new_sig else 's'
                    self.stems[m] += 1  # add to stems dict
                    has_stem = True

                    # Update dictionaries
                    dict_ref = MorphModel.__getattribute__(self, label)
                    cur_morf_cnt = dict_ref[m]

                    if cur_morf_cnt > 1:    # update dict for old label
                        dict_ref[m] -= 1
                    else:
                        del dict_ref[m]

                else:           # reuse label, update
                    new_sig += '-' + labels[i] if i > 0 else labels[i]
  
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
        Determine signature (morpheme labels) of
        a sequence of morphemes without
        adding the segments to their respective
        dictionaries (as previous method does)
        :param morphs:
        :return: signature
        """

        signature = ''
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

        return signature

    def shift_boundary(self):
        """
        Shift/adjust boundary and try to
        force segmentation of previously undefined/
        unknown sequences, i.e. words containing one or more unknowns ('?').

        All dictionaries are later updated.
        """
 

        ambig = list(self.ambig_words.keys())
        for word in ambig:
            old_morphs = word.split('-')
            n = len(old_morphs)
            new_morphs = [old_morphs[0]]
            has_shift = False
            for i in range(0, n - 1):
 
                is_valid = False
                # Original morphs
                m1 = new_morphs.pop()
                m2 = old_morphs[i + 1]
   
                # Do not alter if the signature if the current
                # candidate morphs are valid
                # if m1 not in self.unknown and m2 not in self.unknown:
                candidates = self.get_candidates(m1, m2, new_morphs)
                if self.valid_shift(candidates[:-1]):
                    new_morphs = list(candidates)
                    is_valid = True
                    continue

                # Otherwise, shift morpheme boundary left
                has_shift = True
                new_m1 = m1 + m2[0]
                new_m2 = m2[1:]
   
                # Get candidates
                candidates =self.get_candidates(new_m1, new_m2, new_morphs)
                
                # Is this a valid shift (are both morphs now known)?
                # If so, do shift and add both morphs to the stack
                if self.valid_shift(candidates[:-1]):
                    is_valid = True
                    new_morphs = list(candidates)
                    continue

                # Otherwise, try shifting right
                new_m1 = m1[:-1]
                new_m2 = m1[-1] + m2
 
                # Get candidates
                candidates =self.get_candidates(new_m1, new_m2, new_morphs)
 
                # Is this a valid shift (are both morphs now known)?
                # If so, do shift and add both morphs to the stack (new segmented word)

                new_morphs = list(candidates)
                if self.valid_shift(candidates[:-1]):
                    is_valid = True
                    continue

                # Otherwise, keep old morphs and abort for this word
                else:
                    break


            if has_shift and is_valid and self.valid_shift(new_morphs):

                # Add new signature, update dicts
                new_signature = self.get_signature(new_morphs)
                adj_word = '-'.join(new_morphs)
                orig_word = ''.join(new_morphs)
                word_count = self.alphabetic_words[word]
 
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
                n = len(old_labels)  # number of labels/length of signature
                for i in range(n):
                    m = old_morphs[i]  # current morph
                    label = self.LABELS[old_labels[i]]  # expand label name
                    dict_ref = MorphModel.__getattribute__(self, label)
                    cur_morf_cnt = dict_ref[m]

                    if cur_morf_cnt > 1:  # update dict for old label
                        dict_ref[m] -= word_count
                    else:
                        del dict_ref[m]

    def valid_shift(self, candidates):
        """
        Validate the potential shift. A split is invalid
        if it contains any unknowns ('?')
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
        Helper method for shifting boundaries, which
        concatenates morphs to the running new the potential shift.
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
                f_out.write(str(freq) + '\t' + signature + '\n')


        with open('stats-token' + dict_file_suffix, 'w') as f_out:
            N = sum(self.alphabetic_words.values())     # text size/number of tokens
            f_out.write('1' + '\t' + abbrev_fn + '\n')
            for signature, words in self.signatures.items():
                counts = 0
                for word in words:
                    if word in self.shifted_words:
                        word = self.shifted_words[word]    # lookup original word before adjustment
                    counts += self.alphabetic_words[word]
              
                freq = round(counts / N, 3)
                f_out.write(str(freq) + '\t' + signature + '\n')
