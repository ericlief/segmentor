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


if __name__ == "__main__":

    # Get all segments files
    #filenames = glob.glob('segments*')

    #test = ['segments-test.txt'] 'segments-ep.cs-en.en.txt',
    filenames = ['segments-ep.cs-en.cs.txt']
    # dict_file_suffix = self.segments_file_in[8:]
    # abbrev_fn = self.segments_file_in[9:-3]

    for filename in filenames:

        # Train model
        model = MorphModel(filename)
        model.process()
        model.reprocess()
        model.shift_boundary()
        model.write()

        # Process text for translation
        segmented_sents = SegmentedSentences(model, 'cs-en.txt/Europarl' + filename[-13:-4])
        #segmented_sents = SegmentedSentences(model, 'test.txt')
        #f = 'Europarl.cs-en.en'

        # Write to disk
        with open('cs-en.txt/segmented-sents' + filename[-12:], 'w') as f_out:
        #with open('test-segmented-sents.txt', 'w') as f_out:
                # words = segmented_sents.words()
                # segmented_words = segmented_sents.segmented_words()
                segs_spaces = segmented_sents.segments_space_symbol()
                # segs_no_space = segmented_sents.segments_no_space_symbol()

                for sent in segs_spaces:

                    f_out.write(str(sent) + '\n')

        # Write to disk
        with open('cs-en.txt/sent-repr' + filename[-12:], 'w') as f_out:
        #with open('test-sent-repr.txt', 'w') as f_out:

            # words = segmented_sents.words()
            # segmented_words = segmented_sents.segmented_words()
            repr = segmented_sents.segmented_sent_repr()
            # segs_no_space = segmented_sents.segments_no_space_symbol()

            for sent in repr:
                f_out.write(str(sent) + '\n')


        # print(segmented_sents.words())
        # print(segmented_sents.segmented_words())
        # print(segmented_sents.segments_space_symbol())
        # print(segmented_sents.segments_no_space_symbol())



