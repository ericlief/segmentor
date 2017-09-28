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
from collections import defaultdict
import codecs

def grow_diag_final_and(srclen, trglen, e2f, f2e):
    """
    This module symmetrisatizes the source-to-target and target-to-source
    word alignment output and produces, aka. GDFA algorithm (Koehn, 2005).

    Step 1: Find the intersection of the bidirectional alignment.

    Step 2: Search for additional neighbor alignment points to be added, given
            these criteria: (i) neighbor alignments points are not in the
            intersection and (ii) neighbor alignments are in the union.

    Step 3: Add all other alignment points thats not in the intersection, not in
            the neighboring alignments that met the criteria but in the original
            foward/backward alignment outputs.

        >>> forw = ('0-0 2-1 9-2 21-3 10-4 7-5 11-6 9-7 12-8 1-9 3-10 '
        ...         '4-11 17-12 17-13 25-14 13-15 24-16 11-17 28-18')
        >>> back = ('0-0 1-9 2-9 3-10 4-11 5-12 6-6 7-5 8-6 9-7 10-4 '
        ...         '11-6 12-8 13-12 15-12 17-13 18-13 19-12 20-13 '
        ...         '21-3 22-12 23-14 24-17 25-15 26-17 27-18 28-18')
        >>> srctext = ("この よう な ハロー 白色 わい 星 の Ｌ 関数 "
        ...            "は Ｌ と 共 に 不連続 に 増加 する こと が "
        ...            "期待 さ れる こと を 示し た 。")
        >>> trgtext = ("Therefore , we expect that the luminosity function "
        ...            "of such halo white dwarfs increases discontinuously "
        ...            "with the luminosity .")
        >>> srclen = len(srctext.split())
        >>> trglen = len(trgtext.split())
        >>>
        >>> gdfa = grow_diag_final_and(srclen, trglen, forw, back)
        >>> gdfa == set([(28, 18), (6, 6), (24, 17), (2, 1), (15, 12), (13, 12),
        ...         (2, 9), (3, 10), (26, 17), (25, 15), (8, 6), (9, 7), (20,
        ...         13), (18, 13), (0, 0), (10, 4), (13, 15), (23, 14), (7, 5),
        ...         (25, 14), (1, 9), (17, 13), (4, 11), (11, 17), (9, 2), (22,
        ...         12), (27, 18), (24, 16), (21, 3), (19, 12), (17, 12), (5,
        ...         12), (11, 6), (12, 8)])
        True

    References:
    Koehn, P., A. Axelrod, A. Birch, C. Callison, M. Osborne, and D. Talbot.
    2005. Edinburgh System Description for the 2005 IWSLT Speech
    Translation Evaluation. In MT Eval Workshop.

    :type srclen: int
    :param srclen: the number of tokens in the source language
    :type trglen: int
    :param trglen: the number of tokens in the target language
    :type e2f: str
    :param e2f: the forward word alignment outputs from source-to-target
                language (in pharaoh output format)
    :type f2e: str
    :param f2e: the backward word alignment outputs from target-to-source
                language (in pharaoh output format)
    :rtype: set(tuple(int))
    :return: the symmetrized alignment points from the GDFA algorithm
    """

    # Converts pharaoh text format into list of tuples.
    # e2f = [tuple(map(int, a.split('-'))) for a in e2f.split()]
    # f2e = [tuple(map(int, a.split('-'))) for a in f2e.split()]

    neighbors = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    alignment = set(e2f).intersection(set(f2e))  # Find the intersection.
    union = set(e2f).union(set(f2e))

    # *aligned* is used to check if neighbors are aligned in grow_diag()
    aligned = defaultdict(set)
    for i, j in alignment:
        aligned['e'].add(i)
        aligned['f'].add(j)

    def grow_diag():
        """
        Search for the neighbor points and them to the intersected alignment
        points if criteria are met.
        """
        prev_len = len(alignment) - 1
        # iterate until no new points added
        while prev_len < len(alignment):
            # for english word e = 0 ... en
            for e in range(srclen):
            # for e in range(trglen):

                # for foreign word f = 0 ... fn
                # for f in range(srclen):
                for f in range(trglen):

                    # if ( e aligned with f)
                    if (e, f) in alignment:
                        # for each neighboring point (e-new, f-new)
                        for neighbor in neighbors:
                            neighbor = tuple(i + j for i, j in zip((e, f), neighbor))
                            e_new, f_new = neighbor
                            # if ( ( e-new not aligned and f-new not aligned)
                            # and (e-new, f-new in union(e2f, f2e) )
                            if (e_new not in aligned and f_new not in aligned) \
                                    and neighbor in union:
                                alignment.add(neighbor)
                                aligned['e'].add(e_new)
                                aligned['f'].add(f_new)
                                prev_len += 1

    def final_and(a):
        """
        Adds remaining points that are not in the intersection, not in the
        neighboring alignments but in the original *e2f* and *f2e* alignments
        """
        # for english word e = 0 ... en
        # for e_new in range(trglen):
        for e_new in range(srclen):

            # for foreign word f = 0 ... fn
            # for f_new in range(srclen):
            for f_new in range(trglen):

                # if ( ( e-new not aligned and f-new not aligned)
                # and (e-new, f-new in union(e2f, f2e) )
                if (e_new not in aligned
                    and f_new not in aligned
                    and (e_new, f_new) in a):
                    alignment.add((e_new, f_new))
                    aligned['e'].add(e_new)
                    aligned['f'].add(f_new)

    grow_diag()
    final_and(e2f)
    final_and(f2e)

    return alignment

if __name__ == "__main__":

    # Get all segments files
    #filenames = glob.glob('segments*')

    #test = ['segments-test.txt'] 'segments-ep.cs-en.en.txt',
    filenames_cs = ['corp/DGT/cs-en.txt/DGT.cs-en.en', 'segments-ep.cs-en.cs.txt']
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
        # segmented_sents_cs = SegmentedSentences(model, 'Europarl' + filename_cs[-13:-4])
        segmented_sents_cs = SegmentedSentences(model, 'small_cz')
        # segmented_sents_cs = SegmentedSentences(model, 'large_cz')

        # segmented_sents_cs = SegmentedSentences(model, 'test_cz')
        print(segmented_sents_cs)

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
        # segmented_sents_en = SegmentedSentences(model, 'Europarl' + filename_en[-13:-4])
        segmented_sents_en = SegmentedSentences(model, 'small_en')
        # segmented_sents_en = SegmentedSentences(model, 'large_en')
        # segmented_sents_en = SegmentedSentences(model, 'test_en')

        #f = 'Europarl.cs-en.en'

        # Write to disk segments with space symbol
        # with open('aligned sents' + filename_cs[-15:-7], 'w') as f_out:
        #with open('test-segmented-sents.txt', 'w') as f_out:
                # words = segmented_sents.words()
                # segmented_words = segmented_sents.segmented_words()
        # segs_spaces_cs = segmented_sents_cs.segments_space_symbol()
        # segs_spaces_en = segmented_sents_en.segments_space_symbol()
        # segs_no_space = segmented_sents.segments_no_space_symbol()

        aligned_sentences_e2f = []
        aligned_sentences_f2e = []

        for sent_tar, sent_src in zip(segmented_sents_en.segmented_sents, segmented_sents_cs.segmented_sents):
            # aligned_sent = AlignedSentence(sent_e, sent_f)
            # aligned_sent = AlignedSentence.from_segmented_sent_to_words(sent_tar, sent_src)
            aligned_sent = AlignedSentence.from_segmented_sent_to_segments_with_space_symbol(sent_tar, sent_src)
            aligned_sentences_e2f.append(aligned_sent)
            # aligned_sent = AlignedSentence.from_segmented_sent_to_words(sent_src, sent_tar)
            aligned_sent = AlignedSentence.from_segmented_sent_to_segments_with_space_symbol(sent_src, sent_tar)
            aligned_sentences_f2e.append(aligned_sent)

        # Train both forward and backward models
        iters = 20
        thresh = .30
        file = 'aligned_sents-' + filename_cs[-15:-7] + '.txt'
        model_e2f = IBM1(aligned_sentences_e2f, iters, thresh, output='output_alignments_small_e2f.txt')
        model_f2e = IBM1(aligned_sentences_f2e, iters, thresh, output='output_alignments_small_f2e.txt')


        # e2f_alignments = [sent.alignment for sent in e2f_sents]
        # f2e_alignments = [sent.inverse_alignment() for sent in f2e_sents]
        # alignments = [set(e2f).intersection(set(f2e)) for (e2f, f2e) in zip(e2f_alignments, f2e_alignments)]


        with open(file, 'w') as f:

            # Symmetricize alignements by taking intersection

            e2f_sents = model_e2f.aligned_sents
            f2e_sents = model_f2e.aligned_sents
            for k, e_sent in enumerate(e2f_sents):
            # for k, e_sent in enumerate(f2e_sents):

                # Convert alignements to string representation
                e2f_str = ''
                e2f = e_sent.alignment
                # e2f = e_sent.inverse_alignment() # inverse?

                for j, i in e2f:
                    e2f_str += str(j) + '-' + str(i) + ' '

                f2e_str = ''
                f_sent = f2e_sents[k]
                # f_sent = e2f_sents[k]

                f2e = f_sent.inverse_alignment()
                # f2e = f_sent.alignment
                for j, i in f2e:
                    f2e_str += str(j) + '-' + str(i) + ' '

                # Get intersection, convert to string
                int_str = ''
                intersection = set(e2f).intersection(set(f2e))
                # intersection = set(f2e).intersection(set(e2f))

                for j, i in intersection:
                    int_str += str(j) + '-' + str(i) + ' '

                # # Symmetrization of bidirectional alignment (Cohn)
                # srclen = len(e_sent.mots)       # len of src sentence (f)
                # trglen = len(e_sent.words)      # len of tar sentence (e)
                # # trglen = len(e_sent.mots)  # len of src sentence (f)
                # # srclen = len(e_sent.words)  # len of tar sentence (e)
                #
                # sym_align = grow_diag_final_and(srclen, trglen, e2f, f2e)
                # # sym_align = grow_diag_final_and(srclen, trglen, f2e, e2f)
                # sym_str = ''
                # for j, i in sym_align:
                #     sym_str += str(j) + '-' + str(i) + ' '

                # Write
                f.write('\t'.join(e_sent.words) + '\n')
                f.write('\t'.join(e_sent.mots) + '\n')
                f.write(e2f_str + '\n')
                f.write(f2e_str + '\n')
                f.write('intersection\n')
                f.write(int_str + '\n')
                # f.write('symmetrization\n')
                # f.write(sym_str + '\n')


                    # model.write_alignments(file)

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

        # print(segmented_sents.segments_space_symbol())



