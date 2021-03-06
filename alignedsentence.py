#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 29.05.17
Mofified on 30.08.18
@author: Eric Lief
"""

from segmentedsentences import *

class AlignedSentence:
    """
    An AlignedSentence object which encapsulates
    two sentences and the alignment between them. In addition
    providing useful tools to compare alignments and calculate
    statistics.
    """

    def __init__(self, words, mots, alignment=None):
        self._words = words                 # tar language words
        self._mots = mots                   # src language words
        self.alignment = alignment          # list of tuples of tar to src mapping [(0,1), (1,1), ...]

    @classmethod
    def from_segmented_sent_to_words(cls, segmented_sent_tar, segmented_sent_src):
        """Returns a word representation of an aligned sentence"""
        words = segmented_sent_tar.segmented_words                 # source language words
        mots = segmented_sent_src.segmented_words                  # target language words
   
        return cls(words, mots)

    @classmethod
    def from_segmented_sent_to_segments_with_space_symbol(cls, segmented_sent_tar, segmented_sent_src):
        words = segmented_sent_tar.segments_with_space_symbol  # source language words
        mots = segmented_sent_src.segments_with_space_symbol   # target language words
  
        return cls(words, mots)

    @classmethod
    def from_segmented_sent_to_segments_no_space_symbol(cls, segmented_sent_tar, segmented_sent_src):
        words = segmented_sent_tar.segments_no_space_symbol  # source language words
        mots = segmented_sent_src.segments_no_space_symbol   # target language words
        
        return cls(words, mots)

    def inverse_alignment(self):
        """
        Utility method for alignment symmetrization.
        :return: inverse alignemnt
        """
        if self.alignment:
            return [(f, e) for (e, f) in self.alignment]

    @property
    def words(self):
        return self._words

    @property
    def mots(self):
        return self._mots


