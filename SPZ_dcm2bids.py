#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Filename: SPZ_dcm2bids.py
# Author: Chang Wenshuo
# Date: 6/5/2025
#
# This script is used to convert the dicom files to BIDS format using dcm2bids

import os
from os.path import join as opj
from glob import glob as gg

RootPath = '/home/wenshuo/DATA/Experiments/SPZ'
RawPath = opj(RootPath, 'dicomdir_for_dcm2bids')
SubjFiles = gg(opj(RawPath, 'SPZ*'))
SubjFiles.sort()
BidsPath = opj(RootPath, 'mri_bids')
OutPath = opj(BidsPath, 'sourcedata')
config_file = opj(BidsPath, 'code', 'dcm2bids_config.json')
os.system('dcm2bids -v') # check if dcm2bids is installed
for subj in SubjFiles:
    # get the subject number
    SubNum = subj.split('/')[-1].split('_')[0]
    # check if the subject has been converted
    if not os.path.exists(opj(OutPath, 'sub-%s'%SubNum)):
        print('Running dcm2bids for %s'%SubNum)
        # run dcm2bids
        os.system('dcm2bids -d %s -p %s -c %s -o %s --auto_extract_entities --force_dcm2bids'%
                  (subj, SubNum, config_file, OutPath))
    else:
        print('Already converted %s'%SubNum)
