#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 29.05.17
@author: Eric Lief
"""


class AlignedSentence:
    """
    A simple AlignedSentence object which encapsulates
    two sentences and the alginment between them
    """

    def __init__(self, words, mots, alignment=None):
        self._words = words                 # source language words
        self._mots = mots                   # target language words
        self.alignment = alignment          # list of tuples of tar to src mapping [(0,1), (1,1), ...]

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
