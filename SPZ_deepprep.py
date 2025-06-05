#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This script is used to run DeepPrep for preprocessing MRI data

import os
from os.path import join as opj
from os.path import exists as ope
from glob import glob as gg

RootPath = '/home/wenshuo/DATA/Experiments/SPZ/mri_bids'
InPath = opj(RootPath, 'sourcedata')
OutPath = opj(RootPath, 'derivatives', 'deepprep')
fslicense_file = '/home/wenshuo/Toolboxes/license.txt'
# how many dummy scans?
dummy = 10 # s
TR = 2 # s
bold_skip_frame = int(dummy/TR)
# all subjects in sourcedata
SubjFiles = gg(opj(InPath, 'sub-*'))
SubjFiles.sort()

#### delete dummmy scans ####
def get_bold_info(subj):
    ''' get the BOLD file dir and the number of frames '''
    SubNum = subj.split('sub-')[1]
    bold_file = opj(subj, 'func', 'sub-%s_task-rest_bold.nii.gz'%SubNum)
    from subprocess import getstatusoutput as sg
    out = sg('fslinfo %s | grep dim4'%bold_file)
    dim4_frames = out[1].split('\n')[0].split('\t\t')[1]
    print('%s bold file has %s frames'%(SubNum, dim4_frames))
    return bold_file, dim4_frames

def delete_dummy_scans(bold_file, bold_skip_frame):
  ''' delete dummy scans '''
  print("Deleting %s dummy scans from %s"%(str(bold_skip_frame), bold_file))
  bold_noskip = bold_file.replace('.nii.gz', '_noskip.nii.gz')
  os.system('mv %s %s'%(bold_file, bold_noskip))
  os.system('fslroi %s %s %i -1'%(bold_noskip, bold_file, bold_skip_frame))

# delete dummy scans for each subject
for subj in SubjFiles:
    bold_file, dim4_frames = get_bold_info(subj)
    if int(dim4_frames) == 300:
       delete_dummy_scans(bold_file, bold_skip_frame)
    else:
        print('%s bold file has %s frames, no need to delete dummy scans'%(subj.split('sub-')[1], dim4_frames))

# check if the deepprep ouput exists, if not, include it in the command
subj_list = [subj.split('/')[-1].split('-')[-1] for subj in SubjFiles if not ope(opj(OutPath, 'QC', subj.split('/')[-1]))]
subj_list.sort()
subj_list_str = str(subj_list).strip('[]').replace(',', '').replace('\'', '')
# who to include
print(subj_list_str)

'''
DeepPrep Command
  1. 必要参数
    - <bids_dir> 输入数据集的本地目录，必须为BIDS格式。
    - <output_dir> DeepPrep 的输出结果目录，详情可参阅。
    - <fs_license_file> 有效的 FreeSurfer 许可证的目录。
    - deepprep:25.1.0 Docker 的 DeepPrep 镜像版本，可以通过 deepprep:<version>指定版本。
    - participant 分析水平。
    - --bold_task_type 指定需要处理的BOLD任务类型 （例： rest, motor)。
  2. 可选参数
    - --participant_label可以指定具体受试者数据，例：  'sub-001 sub-002'.否则会默认处理 <bids_dir> 所有受试者。
    - --subjects_dir Recon 文件的输入目录。
    - --skip_bids_validation 可以跳过输入数据集的 BIDS 格式验证。
    - --anat_only 仅处理结构数据。
    - --bold_only 仅处理功能数据，其中 Recon 需要被提供。
    - --bold_sdc 进行磁场校正（susceptibility distortion correction），默认为 True。
    - --bold_confounds 生成关于BOLD 的 confounds ，例如头动信息等，默认为 True。
    - --bold_surface_spaces 指定表面模板空间，例： 'fsnative fsaverage fsaverage[3-6]'，默认为 'fsaverage6'. 
        (注：空间名称必须使用单引号引起来)
    - --bold_volume_space 指定TemplateFlow中可用的体积空间，默认值为MNI152NLin6Asym。
    - --bold_volume_res 指定TemplateFlow中相应模板空间的空间分辨率，默认为02。
    - --device 指定设备。默认为auto，自动选择 GPU 设备；0指定第一个 GPU 设备；cpu仅指 CPU。
    - --cpus 指的是最大 CPU 使用率，应该大于 0 的整数值。
    - --memory 指可使用的最大内存资源，应为大于 0 的整数值。
    - --ignore_error 忽略处理过程中发生的错误。
    - --resume 允许 DeepPrep 从最后一个断点处启动。
    - --bold_skip_frame 指定需要跳过的帧数，默认为 0
'''
# write the command to run DeepPrep
deepprep_cmd = "docker run \
                -v %s:/input \
                -v %s:/output \
                -v %s:/fs_license.txt \
                deepprep:25.1.0 \
                /input \
                /output \
                participant \
                --participant_label '%s' \
                --bold_task_type rest \
                --skip_bids_validation \
                --bold_sdc True \
                --bold_confounds True \
                --fs_license_file /fs_license.txt \
                --device cpu \
                --cpu 5" % (InPath, OutPath, fslicense_file, subj_list_str)
# run DeepPrep
print(deepprep_cmd)
os.system(deepprep_cmd)
