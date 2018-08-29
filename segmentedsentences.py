#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor
Created on 30.05.17
@author: Eric Lief
"""

from nltk.tokenize import wordpunct_tokenize
from morphmodel import *

class SegmentedSentences:
    """
    A SegmentedSentences object which encapsulates
    several different internal (segmental) representation of all sentences
    of a sentence tokenized text, which can be used in
    MT.
    """
    def __init__(self, morph_model, file):
        self.model = morph_model                                      # MorphModel
        # self.segmented_sents = self.segment_sentences(file)     # list(SegmentedSentences)

        # Tokenize text and then segment sentences, using
        # trained MorphModel
        with open(file, 'r') as f:

            segmented_sents = []
            for sent in f:
                # words = sent.split()
                sent = sent.lower()
                words = wordpunct_tokenize(sent)
                segmented_sent = SegmentedSent(words, self.model)
                segmented_sents.append(segmented_sent)
            self._segmented_sents = segmented_sents

    # def segment_sentences(self, file):
    #
    #     with open(file, 'r') as f:
    #         segmented_sents = []
    #         for sent in f:
    #             # words = sent.split()
    #             sent = sent.lower()
    #             words = wordpunct_tokenize(sent)
    #             segmented_sent = SegmentedSent(words, self.model)
    #             segmented_sents.append(segmented_sent)
    #             # print(sent)
    #             # print(segmented_sent.words)
    #             # print(segmented_sent.segmented_words)
    #             # print(segmented_sent._segmented_sent_repr)
    #             # print(segmented_sent._segments_with_space_symbol)
    #             # print(segmented_sent._segments_no_space_symbol)
    #         #print(segmented_sents)
    #         return segmented_sents

    # def segment_sentence(self, words):
    #     return SegmentedSent(words, self.model)

    @property
    def segmented_sents(self):
        return self._segmented_sents

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
    """
    A SegmentedSentence object which encapsulates
    several different internal representation of splits (segments)
    of a given sentence
    """

    def __init__(self, words, model):
        self._words = words     # return words
        self.model = model      # MorphModel

        # print(self.model.__class__.__name__)
        
        self._segmented_words = [" ".join(self.model.segment_word(word)) for word in words]  # ['the', 'boy s', 'chase d', 'the', 'girl s']
        self._segmented_sent_repr = " ◽ ".join(self._segmented_words)                        # 'the ◽ boy s ◽ chase d ◽ the ◽ girl s'
        self._segments_with_space_symbol = self._segmented_sent_repr.split()                 # ['the', '◽', 'boy', 's' '◽'...]
        self._segments_no_space_symbol = []                                                  # ['the', 'boy', 's'...]
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

    
    
    
    
    
if __name__ == "__main__":
    import sys
    import pickle

    # Unit tests
 
    #if len(sys.argv) == 3:
        #filename_src = sys.argv[1]
        #filename_targ = sys.argv[2]
        #print('processing ', filename_src, filename_targ)
        
        #with open('model-' + filename_src[0:-3] + '.bin', 'rb'):      
            #model_src = pickle.load
            
        #with open('model-' + filename_targ[0:-3] + '.bin', 'rb'):     
            #model_targ = pickle.load            
            
    #else:
        #sys.exit
      
    #filenames = ['segments-ep.cs-en.cs.txt']
    filenames = ['segments-ep.cs-sk.sk.txt'] 
    #filenames = ['segments-ep.cs-sk.cs.txt', 'segments-dgt.cs-sk.cs.txt', 'segments-os.cs-sk.cs.txt',
    #             'segments-ep.cs-sk.sk.txt', 'segments-dgt.cs-sk.sk.txt', 'segments-os.cs-sk.sk.txt']

    for f_idx, filename in enumerate(filenames):

        # Train source MorphModel
        print('Building model for: ', filename)
        model = MorphModel(filename)
        model.process()
        model.reprocess()
        model.shift_boundary()
        model.write()
        
        with open('model'+filename[8:-3]+'bin', 'wb') as f:
            pickle.dump(model, f)
            
 
        with open('model'+filename[8:-3]+'bin', 'rb') as f:
            m = pickle.load(f)
            print('UNKNOWN words for ', filename)
            print(m.unknown)
            print(m.segment_word('pochopit'))
            print(m.segment_word('ženy'))    
            
            file = filename[9:-4] + '.sm'       
            segmented_sents = SegmentedSentences(m, file)
            for seg_sent in segmented_sents.segmented_sents:
                print(seg_sent.segmented_words)
