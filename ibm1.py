#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: MT
Created on 17.03.17
@author: Eric Lief
"""

import io
import sys
import numpy as np
from collections import Counter, defaultdict
from alignedsentence import *

# def EM(S):
#     pass

"""
Source: EN
Target : CZ
"""


class IBMModel1():

    def __init__(self, aligned_sents, iters):
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

        print(self.trans_table)

        sent_align = self.get_alignments(aligned_sents)
        for align in sent_align:
            print(align)

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
                    if total_count[e] == 0.0:
                        for f in sent.mots:
                            total_count[e] += self.trans_table[e][f]

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

                    print('iter  ', i+1)
                    print(e,f,self.trans_table[e][f])

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
                    if self.trans_table[e][f] > max_p:
                        max_p = prob
                        best_align_pos = i
                sent_alignments.append((j, best_align_pos))
            all_sent_alignments.append(sent_alignments)
        return all_sent_alignments

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

    model = IBMModel1(aligned_sents, iters)




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

