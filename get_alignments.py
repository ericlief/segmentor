#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project: segmentor

These helper functions write the alignments (fwd and bwd) to file
in the preferred representation format.
The intersection of fwd and bwd alignments are also computed,
and the frequency of the tar-src morheme/segment signature (type)
is also updated and written to file.

Created on 30.05.17
Modified on 30.08.18
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

def identify_morph(morph, morph_model):
    """
    Rudimentary (rough) way of identifying what type of morph a segment is for a
    given language, by checking the dictionaries in the MorphModel
    :param morph:
    :param morph_model:
    :return:
    """
    if morph in morph_model.stems:
        return 's'
    if morph in morph_model.prefixes:
        return 'p'
    if morph in morph_model.suffixes:
        return 'e'
    return '<UNK>'

if __name__ == "__main__":
    import sys
    import pickle
    
 
    if len(sys.argv) == 3:
        filename_src = sys.argv[1]
        filename_targ = sys.argv[2]
        print('processing ', filename_src, filename_targ)
        
        with open('model-' + filename_src[0:-3] + '.bin', 'rb') as f:      
            model_src = pickle.load(f)
            print('loaded model src', model_src.__class__.__name__)
            
        with open('model-' + filename_targ[0:-3] + '.bin', 'rb') as f:     
            model_targ = pickle.load(f)
            print('loaded model targ', model_targ.__class__.__name__) 
            
    else:
        sys.exit("Usage python get_alignments.py [src_file] [tar_file]")
        
    segmented_sents_src = SegmentedSentences(model_src, filename_src)
    segmented_sents_targ = SegmentedSentences(model_targ, filename_targ)
     
    
    # Get alignments 
    aligned_sentences_e2f = []
    aligned_sentences_f2e = []
    for sent_targ, sent_src in zip(segmented_sents_targ.segmented_sents, segmented_sents_src.segmented_sents):

        # Get fwd alignments in the form of an AlignedSentence object
        # We must choose appropriate representation (1-4)
        # aligned_sent = AlignedSentence(sent_targ, sent_src)
        # aligned_sent = AlignedSentence.from_segmented_sent_to_words(sent_targ, sent_src)
        # aligned_sent = AlignedSentence.from_segmented_sent_to_segments_with_space_symbol(sent_targ, sent_src)
        aligned_sent = AlignedSentence.from_segmented_sent_to_segments_no_space_symbol(sent_targ, sent_src)
        
        # Add to list of aligned fwd sentences
        aligned_sentences_e2f.append(aligned_sent)

        # Get bwd alignments in the form of an AlignedSentence object
        # We must choose appropriate representation (1-4)
        # aligned_sent = AlignedSentence.from_segmented_sent_to_words(sent_src, sent_trg)
        # aligned_sent = AlignedSentence.from_segmented_sent_to_segments_with_space_symbol(sent_src, sent_targ)
        aligned_sent = AlignedSentence.from_segmented_sent_to_segments_no_space_symbol(sent_src, sent_targ)
        
        # Add to list of aligned bwd sentences
        aligned_sentences_f2e.append(aligned_sent)

    # Train both forward and backward models, get alignments
    iters = 20
    thresh = .30
    file = 'alignments_no_space_' + filename_src  # change  name accordingly 

    # Forward (English) model with alignments
    model_e2f = IBM1(aligned_sentences_e2f, iters, thresh, output='fwd_no_space_' + file)

    # Backward (Foreign) model with alignments
    model_f2e = IBM1(aligned_sentences_f2e, iters, thresh, output='back_no_space_' + file)

    # A little test 
    # e2f_alignments = [sent.alignment for sent in e2f_sents]
    # f2e_alignments = [sent.inverse_alignment() for sent in f2e_sents]
    # alignments = [set(e2f).intersection(set(f2e)) for (e2f, f2e) in zip(e2f_alignments, f2e_alignments)]

    with open(file, 'w') as f:
        print('saving ', file)
        signatures = defaultdict(int)   # for calculating stats

        # Symmetrize alignements by taking intersection
        e2f_sents = model_e2f.aligned_sents     # forward sentences
        f2e_sents = model_f2e.aligned_sents     # backward sentences

        # Iterate through forward and backward pairs, write alignments
        # and get intersection (symmetrize)
        for k, forward_sent in enumerate(e2f_sents):
 
            # Convert alignments to string representation
            e2f_str = ''
            e2f = forward_sent.alignment            # forward alignment
 
            for j, i in e2f:
                e2f_str += str(j) + '-' + str(i) + ' '

            f2e_str = ''
            f_sent = f2e_sents[k]               # corresponding backward sentence
 
            f2e = f_sent.inverse_alignment()    # backward alignment
             for j, i in f2e:
                f2e_str += str(j) + '-' + str(i) + ' '

            # Get intersection, convert to string
            int_str = ''
            intersection = set(e2f).intersection(set(f2e))
 
            for j, i in intersection:
                int_str += str(j) + '-' + str(i) + ' '

            # Symmetrization of bidirectional alignment (Koehn)
            # Uncomment to use the GDFA algorithm
            # I could not get it to work properly with segments_no_space_symbol
            
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

            words = forward_sent.words      # target sentence
            mots = forward_sent.mots        # source sentence

            # Write results, final stats appear as a dictionary with frequency at end of file
            f.write('\t'.join(words) + '\n')
            f.write('\t'.join(mots) + '\n')
            f.write(e2f_str + '\n')
            f.write(f2e_str + '\n')
            f.write('intersection\n')
            f.write(int_str + '\n')

            # Calculate alignment stats for intersection (symmetrized) alignments
            # signatures = defaultdict(int)
            for j, i in intersection:
                word = words[j]     # target segment
                mot = mots[i]       # source segment
                sig = identify_morph(word, model_targ) + '-' + identify_morph(mot, model_src)      # e.g. 'j-i' -> 's-e'
                signatures[sig] += 1


            f.write('stats\n')
            f.write(str(signatures) + '\n')
            
            # Uncomment if using the GDFA algorithm
            # f.write('symmetrization\n')
            # f.write(sym_str + '\n')

  
