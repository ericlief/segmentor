#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: MT
Created on 17.03.17
@author: Eric Lief
"""

import io
import sys
# import numpy as np
from collections import Counter, defaultdict
# from alignedsentence import *


class IBMModel1():
    """
    Source: EN
    Target : CZ
    """

    def __init__(self, aligned_sents, iters, thresh):
        self.src_vocab = set()
        self.target_vocab = set()

        # Init vocabularies
        for aligned_sent in aligned_sents:
            self.src_vocab.update(aligned_sent.mots)
            self.target_vocab.update(aligned_sent.words)

        # Seed with uniform distribution
        n = len(self.target_vocab)
        init_prob = 1 / n
        self.trans_table = defaultdict(lambda: defaultdict(lambda: init_prob))

        for f in self.src_vocab:
            for e in self.target_vocab:
                self.trans_table[e][f]

        # Train using EM algorithm
        self.train(aligned_sents, iters)

        # print(self.trans_table)

        # Get best alignements (max of all)
        # sent_align = self.get_alignments(aligned_sents)
        # for align in sent_align:
        #     print(align)

        # Get all alignments above threshold
        # print("all alignments above threshold = ", thresh)
        sent_align = self.get_alignments_threshold(aligned_sents, thresh)
        for align in sent_align:
            res = ''
            for j, i in align:
                res += str(j) + '-' + str(i) + ' '
            print(res)
        self._sent_align = sent_align


    def train(self, aligned_sents, iters):

        i = 0
        while i < iters:

            # Initialize
            count_e_f = defaultdict(lambda: defaultdict(lambda: 0.0))
            total_f = defaultdict(lambda: 0.0)

            for sent in aligned_sents:
                total_count = defaultdict(lambda: 0.0)

                # Normalize (E-step)
                for e in sent.words:  # not sure if to add the null
                    if total_count[e] == 0.0:   # only count one unique word per sentence
                        for f in sent.mots:
                            total_count[e] += self.trans_table[e][f]

                # Normalize (E-step)
                # for e in sent.words:  # not sure if to add the null
                #     for f in sent.mots:
                #         total_count[e] += self.trans_table[e][f]

                # Collect counts (E-step)
                for e in sent.words:
                    for f in sent.mots:
                        count = self.trans_table[e][f]
                        normal_count = count / total_count[e]
                        count_e_f[e][f] += normal_count
                        total_f[f] += normal_count

            # Get probabilities (M-step)
            for f in self.src_vocab:
                for e in self.target_vocab:
                    self.trans_table[e][f] = count_e_f[e][f] / total_f[f]

                    # print('iter  ', i+1)
                    # print(e,f,self.trans_table[e][f])

            i += 1

    def get_alignments(self, aligned_sents):
        all_sent_alignments = []
        for sent in aligned_sents:
            sent_alignments = []
            for j, e in enumerate(sent.words):
                max_p = 0.0
                best_align_pos = None
                for i, f in enumerate(sent.mots):
                    prob = self.trans_table[e][f]
                    if prob >= max_p:
                        max_p = prob
                        best_align_pos = i
                sent_alignments.append((j, best_align_pos))
            all_sent_alignments.append(sent_alignments)
        return all_sent_alignments

    def get_alignments_threshold(self, aligned_sents, thresh):
        all_sent_alignments = []
        for sent in aligned_sents:
            sent_alignments = []
            for j, e in enumerate(sent.words):
                # max_p = 0.0
                # best_align_pos = None
                for i, f in enumerate(sent.mots):
                    prob = self.trans_table[e][f]
                    if prob > thresh:
                        # max_p = prob
                        # best_align_pos = i
                        # print(j,i,prob)
                # if best_align_pos:
                        sent_alignments.append((j, i))
            all_sent_alignments.append(sent_alignments)
        return all_sent_alignments

    def get_alignments_threshold2(self, aligned_sents, thresh):
        all_sent_alignments = []
        for sent in aligned_sents:
            sent_alignments = []
            for j, e in enumerate(sent.words):
                max_p = 0.0
                best_align_pos = None
                for i, f in enumerate(sent.mots):
                    prob = self.trans_table[e][f]
                    if prob >= max_p and prob > thresh:
                        max_p = prob
                        best_align_pos = i
                        # print(j,i,prob)
                if best_align_pos:
                    sent_alignments.append((j, best_align_pos))
            all_sent_alignments.append(sent_alignments)
        return all_sent_alignments

    def write_alignments(self, file):
        # Get best alignements (max of all)
        # sent_align = self.get_alignments(aligned_sents)
        # for align in sent_align:
        #     print(align)

        # Get all alignments above threshold
        # print("all alignments above threshold = ", thresh)
        # sent_align = self.get_alignments_threshold(aligned_sents, thresh)

        with open(file, 'w') as f:

            for align in self._sent_align:
                res = ''
                for j, i in align:
                    res += str(j) + '-' + str(i) + ' '
                    # print(res)
                    f.write(res + '\n')

class AlignedSentence:
    """
    A simple AlignedSentence object which encapsulates
    two sentences and the alginment between them
    """

    def __init__(self, words, mots, alignment=None):
        self._words = words                 # source language words
        self._mots = mots                   # target language words
        self._alignment = alignment          # list of tuples of tar to src mapping [(0,1), (1,1), ...]

    @property
    def words(self):
        return self._words

    @property
    def mots(self):
        return self._mots


    @property
    def alignment(self):
        return self._alignment

    @alignment.setter
    def aligment(self, alignment):
        self._alignment = alignment

if __name__ == "__main__":
    stream = io.TextIOWrapper(sys.stdin.buffer)
    aligned_sents = []
    iters = 0
    thresh = 0
    # # EN = set()     # English words
    # # CZ = set()     # Czech words
    # all_words = Counter()       # English words (e)
    # all_mots = Counter()        # Foreign words (f)
    # total_words = defaultdict(int)
    # total_mots = defaultdict(int)
    # probs = {}

    # Process input
    try:
        line = stream.readline()
        iters, thresh = line.split()
        iters = int(iters.split(":")[1])
        thresh = float(thresh.split(":")[1])

        # Process each sentence pair
        for line in stream:
            pair = line.split("#")
            pair[0] = pair[0].strip()
            pair[1] = pair[1].strip()
            words = pair[0].split()
            mots = pair[1].split()
            aligned_sent = AlignedSentence(words, mots)
            # for w in words:
            #     all_words[w] += 1
            # for w in mots:
            #     all_mots[w] += 1
            aligned_sents.append(aligned_sent)


    except IOError:
        sys.stderr.write('Problem with input format.')

    model = IBMModel1(aligned_sents, iters, thresh)

    # for alignment in model.get_alignments()
    #


    #for pair in pairs:

    # Initialize t(e|f) uniformly
    # totalAlignments = len(en)**len(cz)      # (l_f + 1)^l_e,  add 1?




    # #for pair in pairs:
    # # totalAlignments = len(en)**len(cz)      # (l_f + 1)^l_e,  add 1?
    #
    # n = len(EN)   # size of source corpus
    # for e in CZ:  # not sure if to add the null
    #     for f in EN:
    #         probs[(e, f)] = 1 / n

   #  print(probs)
   # # print(iters, thresh)
   #  #EM(S)
   #  print("EN: ", EN)
   #  print("CZ: ", CZ)

