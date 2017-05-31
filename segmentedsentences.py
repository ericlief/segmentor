#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 30.05.17
@author: Eric Lief
"""

from nltk.tokenize import wordpunct_tokenize


class SegmentedSentences:

    def __init__(self, model, file):
        self.model = model
        self.segmented_sents = self.segment_sentences(file)

    def segment_sentences(self, file):

        with open(file, 'r') as f:
            segmented_sents = []
            for sent in f:
                # words = sent.split()
                sent = sent.lower()
                words = wordpunct_tokenize(sent)
                segmented_sent = SegmentedSent(words, self.model)
                segmented_sents.append(segmented_sent)
                # print(sent)
                # print(segmented_sent.words)
                # print(segmented_sent.segmented_words)
                # print(segmented_sent._segmented_sent_repr)
                # print(segmented_sent._segments_with_space_symbol)
                # print(segmented_sent._segments_no_space_symbol)
            #print(segmented_sents)
            return segmented_sents

    # def segment_sentence(self, words):
    #     return SegmentedSent(words, self.model)

    # @property
    # def _segmented_sents(self):
    #     return self._segmented_sents
    #
    # @_segmented_sents.setter
    # def _segmented_sents(self, sents):
    #     self._segmented_sents = sents

    def words(self):
        results = []
        #print(len(self.segmented_sents))
        for sent in self.segmented_sents:
            results.append(sent.words)
            # print(sent, sent.words)
        return results

    def segmented_words(self):
        results = []
        for sent in self.segmented_sents:
            results.append(sent.segmented_words)
        return results

    def segments_space_symbol(self):
        results = []
        for sent in self.segmented_sents:
            results.append(sent.segments_with_space_symbol)
        return results

    def segments_no_space_symbol(self):
        results = []
        for sent in self.segmented_sents:
            results.append(sent.segments_no_space_symbol)
        return results

    def segmented_sent_repr(self):
        results = []
        for sent in self.segmented_sents:
            results.append(sent.segmented_sent_repr)
        return results


class SegmentedSent:
    def __init__(self, words, model):
        self._words = words
        self.model = model
        self._segmented_words = [" ".join(self.model.segment_word(word)) for word in words]  # ['the', 'boy s', 'chase d', 'the', 'girl s']
        self._segmented_sent_repr = " ◽ ".join(self._segmented_words)                       # 'the  boy s   chase d   the   girl s'
        self._segments_with_space_symbol = self._segmented_sent_repr.split()
        self._segments_no_space_symbol = []
        for word in words:
            segments = self.model.segment_word(word)
            self._segments_no_space_symbol += segments

    @property
    def words(self):
        return self._words

    @property
    def segmented_words(self):
        return self._segmented_words

    @property
    def segmented_sent_repr(self):
        return self._segmented_sent_repr

    @property
    def segments_with_space_symbol(self):
        return self._segments_with_space_symbol

    @property
    def segments_no_space_symbol(self):
        return self._segments_no_space_symbol

