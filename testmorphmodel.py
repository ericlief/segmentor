#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor

Main method for testing the MorphModel class.
The training files can be batch processed
by their Morfessor 'segments-' prefixed filenames.

Created on 30.05.17
@author: Eric Lief
"""

from glob import glob
from morphmodel import *
from segmentedsentences import *
from alignedsentence import *
from ibm1 import *

if __name__ == "__main__":

    # Get all segments files
    #filenames = glob.glob('segments*')

    #test = ['segments-test.txt'] 'segments-ep.cs-en.en.txt',
    filenames_cs = ['segments-ep.cs-en.cs.txt']
    filenames_en = ['segments-ep.cs-en.en.txt']

    # dict_file_suffix = self.segments_file_in[8:]
    # abbrev_fn = self.segments_file_in[9:-3]

    for filename_cs in filenames_cs:

        # Train model
        model = MorphModel(filename_cs)
        model.process()
        model.reprocess()
        model.shift_boundary()
        model.write()

        # Process text for translation
        # segmented_sents = SegmentedSentences(model, 'cs-en.txt/Europarl' + filename[-13:-4])
        #segmented_sents = SegmentedSentences(model, 'test.txt')
        # segmented_sents_cs = SegmentedSentences(model, '/media/liefe/data/corp/EP/Europarl' + filename_cs[-13:-4])
        segmented_sents_cs = SegmentedSentences(model, 'Europarl' + filename_cs[-13:-4])

    for filename_en in filenames_en:
        # Train model
        model = MorphModel(filename_en)
        model.process()
        model.reprocess()
        model.shift_boundary()
        model.write()

        # Process text for translation
        # segmented_sents = SegmentedSentences(model, 'cs-en.txt/Europarl' + filename[-13:-4])
        # segmented_sents = SegmentedSentences(model, 'test.txt')
        # segmented_sents_en = SegmentedSentences(model, '/media/liefe/data/corp/EP/Europarl' + filename_en[-13:-4])
        segmented_sents_en = SegmentedSentences(model, 'Europarl' + filename_en[-13:-4])

        #f = 'Europarl.cs-en.en'

        # Write to disk segments with space symbol
        # with open('aligned sents' + filename_cs[-15:-7], 'w') as f_out:
        #with open('test-segmented-sents.txt', 'w') as f_out:
                # words = segmented_sents.words()
                # segmented_words = segmented_sents.segmented_words()
        segs_spaces_cs = segmented_sents_cs.segments_space_symbol()
        segs_spaces_en = segmented_sents_en.segments_space_symbol()
        # segs_no_space = segmented_sents.segments_no_space_symbol()

        aligned_sentences = []
        for sent_e, sent_f in zip(segmented_sents_en, segmented_sents_cs):
            aligned_sent = AlignedSentence(sent_e, sent_f)
            aligned_sentences.append(aligned_sent)

        iters = 10
        thres = .30
        file = 'aligned_sents' + filename_cs[-15:-7]
        model = IBMModel1(aligned_sentences, iters, thresh)
        model.write_alignments(file)

        # for sent in segs_spaces_cs:
        #
        #             f_out.write(str(sent) + '\n')
        #

        # # Write to disk
        # with open('sent-repr' + filename[-13:], 'w') as f_out:
        # #with open('test-sent-repr.txt', 'w') as f_out:
        #
        #     # words = segmented_sents.words()
        #     # segmented_words = segmented_sents.segmented_words()
        #     repr = segmented_sents.segmented_sent_repr()
        #     # segs_no_space = segmented_sents.segments_no_space_symbol()
        #
        #     for sent in repr:
        #         f_out.write(str(sent) + '\n')


        # print(segmented_sents.words())
        # print(segmented_sents.segmented_words())
        # print(segmented_sents.segments_space_symbol())
        # print(segmented_sents.segments_no_space_symbol())




