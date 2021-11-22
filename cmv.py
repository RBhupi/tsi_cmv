#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 4 10:03:50 2021

@author: Bhupendra Raut
"""

import argparse
import sys

from videoRead import openVideoFile, videoCropInfo, readVideoFrame
from cmvUtils import flowVectorSplit, meanCMV
from outNC import creatNetCDF, writeCMVtoNC, writeMeanCMVtoNC, writeNMFtoNC

import numpy as np
import matplotlib.pyplot as plt

import cv2 as cv


def computFileCMV(inf, video_cap):
    """ Compute CMV for whole video and save in a netCDF file.
    """
    ofile_name=creatNetCDF(inf)
    
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
    
            
            writeCMVtoNC(ofile_name, cmv_x, cmv_y, fcount, tcount)
            writeNMFtoNC(ofile_name, nmf_x, nmf_y, fcount, tcount)
            writeMeanCMVtoNC(ofile_name, u_mean, v_mean, fcount, tcount)
            #writeGlobalCMVtoNC(ofile_name, gcmv_x, gcmv_y, fcount, tcount)
            
            #increment the tcount after writing is done.
            tcount += 1



def main():    
    parser = argparse.ArgumentParser(description='''
                                     This program uses phase correlation method 
                                     from the TINT module to compute the cloud 
                                     motion vectors in the hemispheric camera''')
    parser.add_argument('--input', type=str, 
                        help='Path to an input video or images.', 
                        default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
    
    parser.add_argument('--fleap', type=str, 
                        help='Skip frames for better motion detection.', default=1)
    
    args = parser.parse_args()
    
    #====== General settings for the CMV computation and quality control. ======# 
    
    #The sky view will be divided into the square blocks of block size, say 32x32 pixels
    nblock = 20
    block_len = 20
    
    print('Opening:', args.input)
    video_cap = openVideoFile(args.input)
    
    #get video frame and cropping info in a dictionary
    inf = videoCropInfo(video_cap, nblock, block_len)
    video_cap.release()
    
    # showing video properties
    print("Original Frame width '{}'".format(inf['frame_width']))
    print("Original Frame Height : '{}'".format(inf['frame_height']))
    print("Using cropped region: ", inf['x1'],":", inf['x2'], ",", 
          inf['y1'], ":", inf['y2'])
    
    
    run_num = 1
    for i in [1, 2]:
        for d in [1, 2]:
            for er in [2]:#[2, 5, 8]:
                for ch in [8, 9, 0, 1, 2]:
                    video_cap = openVideoFile(args.input)
                    print(run_num)         
                    run_num +=1
                    
                    # Can not use all the RGB channels, so select one
                    inf['channel'] = ch  #0,1,2 BGR in OpenCV
                    inf['v_max'] = int(np.ceil(block_len/3))
                    
                    inf['fleap'] = i
                    inf['input'] = args.input
                    
                    inf['WS05-neighborhood_dist'] = d
                    inf['WS05-eps'] = 0.2
                    inf['WS05-error_thres'] = er
    
    #------------------------------------------------------------------------------
    
                    computFileCMV(inf, video_cap)


if __name__ == "__main__":
    main()
