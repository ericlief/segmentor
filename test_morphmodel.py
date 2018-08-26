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
from segmentedsentences import *
import pickle

if __name__ == "__main__":


    filenames = ['segments-ep.cs-en.cs.txt', 'segments-dgt.cs-en.cs.txt', 'segments-os.cs-en.cs.txt',
                 'segments-ep.cs-en.en.txt', 'segments-dgt.cs-en.en.txt', 'segments-os.cs-en.en.txt']


    for f_idx, filename in enumerate(filenames):

        # Train source MorphModel
        print('Building model for: ', filename)
        model = MorphModel(filename)
        model.process()
        model.reprocess()
        model.shift_boundary()
        model.write()
        
        with open('model'+filename[8], 'w') as f:
            pickle.dump(model, f)
            
 