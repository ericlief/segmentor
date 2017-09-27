#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 29.05.17
@author: Eric Lief
"""

from segmentedsentences import *

class AlignedSentence:
    """
    A simple AlignedSentence object which encapsulates
    two sentences and the alginment between them
    """

    def __init__(self, words, mots, alignment=None):
        self._words = words                 # tar language words
        self._mots = mots                   # src language words
        self._alignment = alignment         # list of tuples of tar to src mapping [(0,1), (1,1), ...]

    @classmethod
    def from_segmented_sent_to_words(cls, segmented_sent_tar, segmented_sent_src):
        words = segmented_sent_tar.segmented_words                 # source language words
        mots = segmented_sent_src.segmented_words                  # target language words
        # self._alignment = alignment          # list of tuples of tar to src mapping [(0,1), (1,1), ...]
        # aligned_sent = AlignedSentence(sent_e, sent_f)
        # aligned_sentences.append(aligned_sent)
        return cls(words, mots)

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
