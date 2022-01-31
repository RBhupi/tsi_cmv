#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 4 10:03:50 2021

@author: Bhupendra Raut
"""

import argparse
import sys
from os.path import basename, dirname, join, exists
import glob
from itertools import compress

from videoRead import openVideoFile, videoCropInfo, readVideoFrame
from cmvUtils import flowVectorSplit, meanCMV
from outNC import creatNetCDF, writeCMVtoNC, writeMeanCMVtoNC, writeNMFtoNC

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


import cv2 as cv


def getMatchingFileNames(args):
    files_mpg = glob.glob(args.indir+"/sgpt*C1*20170102*.mpg")
    files_dt = []
    file_exists = []
    
    for fname in files_mpg:         
        fname_dt = "dt_"+basename(fname).replace(".mpg", ".csv")
        dirname_dt = dirname(fname)
        dirname_dt=dirname_dt.replace("waggle-scott-tsi", "dt_waggle-scott-tsi")
        path_dt = join(dirname_dt, fname_dt)
        file_exists.append(exists(path_dt))
        if exists(path_dt):
            files_dt.append(path_dt)
        
    files_mpg = list(compress(files_mpg, file_exists))
    
    return files_mpg, files_dt
    

def computFileCMV(inf, video_cap):
    """ Compute CMV for whole video and save in a netCDF file.
    """
    ofile_name=creatNetCDF(inf)
    
    dt = pd.read_csv(inf['dt_file'], parse_dates=[0],
                     infer_datetime_format=True, sep=',',header=None)
    
    dt_int = dt.values.astype(np.int64)/10**9
    
    fcount = 0
    first_frame = True
    tcount = 0
    
    while video_cap.isOpened():
        fcount, frame = readVideoFrame(fcount, video_cap)
        if fcount<0:
            return
    
        # We leap forward given number of frames to compute the flow
        if fcount == 1 or fcount % inf['fleap'] == 0:
            sys.stdout.write('Current Frame:' + str(fcount)+ '\r')
            sys.stdout.flush()
            
            if np.any(inf["channel"] == np.array([0, 1, 2])):
                sky_new = frame[inf['y1']:inf['y2'], inf['x1']:inf['x2'], inf['channel']]
            elif inf["channel"] == 8:
                sky_new = frame[inf['y1']:inf['y2'], inf['x1']:inf['x2'], :]
                sky_new = (sky_new[:, :, 2]+0.5)/(sky_new[:, :, 0]+0.5)
            elif inf["channel"] == 9:
                sky_new = frame[inf['y1']:inf['y2'], inf['x1']:inf['x2'], :]
                sky_new = cv.cvtColor(sky_new, cv.COLOR_BGR2GRAY)
          
            #Store the sky data for first the frame as .
            if first_frame:
                sky_curr = sky_new
                first_frame = False
                continue
    
            #move one frame forward
            sky_prev = sky_curr
            sky_curr = sky_new
    
            cmv_x, cmv_y, nmf_x, nmf_y = flowVectorSplit(sky_prev, sky_curr, inf)
            u_mean,  v_mean = meanCMV(cmv_x, cmv_y)
            
            #if(tcount==1213):
            #    print("stope here")
            
            writeCMVtoNC(ofile_name, cmv_x, cmv_y, dt_int[fcount-1], tcount)
            #writeNMFtoNC(ofile_name, nmf_x, nmf_y, dt_int[fcount], tcount)
            writeMeanCMVtoNC(ofile_name, u_mean, v_mean, dt_int[fcount-1], tcount)
            #writeGlobalCMVtoNC(ofile_name, gcmv_x, gcmv_y, fcount, tcount)
            
            #increment the tcount after writing is done.
            tcount += 1



def main():    
    parser = argparse.ArgumentParser(description='''
                                     This program uses phase correlation method 
                                     from the TINT module to compute the cloud 
                                     motion vectors in the hemispheric camera''')
    parser.add_argument('--indir', type=str, 
                        help='Path to an input directory', 
                        default="/Users/bhupendra/projects/cloud_motion/data/waggle-scott-tsi")
    
    parser.add_argument('--fleap', type=str, 
                        help='Skip frames for better motion detection.', default=1)
    
    args = parser.parse_args()
    
    files_mpg, files_dt = getMatchingFileNames(args)
    
    
    #====== General settings for the CMV computation and quality control. ======# 
    
    #The sky view will be divided into the square blocks of block size, say 32x32 pixels
    nblock = 10
    block_len = 40
    
    for file_num in range(len(files_mpg)):
        
        mpg_file = files_mpg[file_num]
        dt_file = files_dt[file_num]
        print('Opening:', mpg_file)
        video_cap = openVideoFile(mpg_file)
    
        #get video frame and cropping info in a dictionary
        inf = videoCropInfo(video_cap, nblock, block_len)
        
        # showing video properties
        print("Original Frame width '{}'".format(inf['frame_width']))
        print("Original Frame Height : '{}'".format(inf['frame_height']))
        print("Using cropped region: ", inf['x1'],":", inf['x2'], ",", 
          inf['y1'], ":", inf['y2'])
    
        # Can not use all the RGB channels, so select one
        inf['channel'] = 2  #0,1,2 BGR in OpenCV
        inf['v_max'] = int(np.ceil(block_len/3))
    
        inf['fleap'] = 1
        inf['input'] = mpg_file
        inf["dt_file"] = dt_file
        
        inf['WS05-neighborhood_dist'] = 1
        inf['WS05-eps'] = 0.2
        inf['WS05-error_thres'] = 6
        
    
    #------------------------------------------------------------------------------
    
        computFileCMV(inf, video_cap)


if __name__ == "__main__":
    main()
