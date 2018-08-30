#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: MT
Created on 17.03.17
Mofified on 30.08.18
@author: Eric Lief
"""

import io
import sys
from collections import Counter, defaultdict
from alignedsentence import *


class IBM1:
    """
    Source: EN
    Target : CZ
    """

    def __init__(self, aligned_sents, iters, thresh=None, output='output_alignments.txt'):
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

        # Get best alignements (max of all)
        self.get_alignments(aligned_sents)
        for a_sent in aligned_sents:
            res = ''
            for j, i in a_sent.alignment:
                res += str(j) + '-' + str(i) + ' '
            print(res)

        # Save alignments, write
        self.aligned_sents = aligned_sents
        self.write_alignments(output, aligned_sents)


    def train(self, aligned_sents, iters):
        """Train with EM algorithm"""
        
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

                # Normalize/collect counts (E-step)
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
 
            i += 1


    def get_alignments(self, aligned_sents):
        """Add tar-src alignments to list"""
        
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
            sent.alignment = sent_alignments

    def get_alignments_threshold(self, aligned_sents, thresh):
        """Do same but only for alignments above a given threshold"""
        
        all_sent_alignments = []
        for sent in aligned_sents:
            sent_alignments = []
            for j, e in enumerate(sent.words):
                for i, f in enumerate(sent.mots):
                    prob = self.trans_table[e][f]
                    if prob > thresh:
                        sent_alignments.append((j, i))
            all_sent_alignments.append(sent_alignments)
        return all_sent_alignments

    def get_alignments_threshold2(self, aligned_sents, thresh):
        """Alternate version of the above"""
        
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
                         
                if best_align_pos:
                    sent_alignments.append((j, best_align_pos))
            all_sent_alignments.append(sent_alignments)
        return all_sent_alignments

    def write_alignments(self, file, aligned_sents):
        # Get best alignements (max of all)
        
        # Get all alignments above threshold
 
        with open(file, 'w') as f:
            for a_sent in aligned_sents:
                res = ''
                for j, i in a_sent.alignment:
                    res += str(j) + '-' + str(i) + ' '
                f.write('\t'.join(a_sent.words) + '\n')
                f.write('\t'.join(a_sent.mots) + '\n')
                f.write(res + '\n')

       
if __name__ == "__main__":
    stream = io.TextIOWrapper(sys.stdin.buffer)
    aligned_sents = []
    iters = 10
    thresh = 0
    
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
            aligned_sent = AlignedSentence(mots, words)
            aligned_sents.append(aligned_sent)


    except IOError:
        sys.stderr.write('Problem with input format.')

    model = IBM1(aligned_sents, iters, thresh)

    