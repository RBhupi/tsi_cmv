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
from outNC import creatNetCDF, writeCMVtoNC, writeMeanCMVtoNC


parser = argparse.ArgumentParser(description='''This program uses phase correlation method from the TINT module
                                              to compute the cloud motion vectors in the hemispheric camera video''')
parser.add_argument('--input', type=str, help='Path to an input video or images.', default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
parser.add_argument('--fleap', type=str, help='Skip frames for better motion detection.', default=2)

args = parser.parse_args()

# Can not use all the RGB channels, so select one
chan = 2 #0,1,2 BGR in OpenCV
#The sky view will be divided into the square blocks of block size, say 32x32 pixels
nblock = 14
block_len = 32


print('Opening:', args.input)
video_cap = openVideoFile(args.input)

#get video frame and cropping info in a dictionary
inf = videoCropInfo(video_cap, nblock, block_len)
inf['fleap']=args.fleap
inf['input']=args.input
inf['channel']=chan

# showing video properties
print("Original Frame width '{}'".format(inf['frame_width']))
print("Original Frame Height : '{}'".format(inf['frame_height']))
print("Using cropped region: ", inf['x1'],":", inf['x2'], ",", inf['y1'], ":", inf['y2'])


ofile_name=creatNetCDF(inf)


fcount = 0
first_frame = True
tcount = 0


while video_cap.isOpened():
    fcount, frame = readVideoFrame(fcount, video_cap)
    

    # We leap forward given number of frames to compute the flow
    if fcount==1 or fcount % args.fleap == 0:
        sys.stdout.write('Current Frame:' + str(fcount)+ '\r')
        sys.stdout.flush()
        
        sky_new = frame[inf['y1']:inf['y2'], inf['x1']:inf['x2'], chan]
      
        #Store the sky data for first the frame as .
        if first_frame:
            sky_curr = sky_new
            first_frame = False
            continue

        #move one frame forward
        sky_prev = sky_curr
        sky_curr = sky_new

        cmv_x, cmv_y = flowVectorSplit(sky_prev, sky_curr, nblock)
        u_mean,  v_mean = meanCMV(cmv_x, cmv_y)

        
        writeCMVtoNC(ofile_name, cmv_x, cmv_y, fcount, tcount)
        writeMeanCMVtoNC(ofile_name, u_mean, v_mean, fcount, tcount)
        #increment the tcount after writing is done.
        tcount +=1



        
        
        
        
        
        

        

    
   
            

    
