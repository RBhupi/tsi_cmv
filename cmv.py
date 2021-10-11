#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 4 10:03:50 2021

@author: Bhupendra Raut
"""

import argparse
import cv2 as cv

#from matplotlib import pyplot as plt
import sys


from videoRead import openVideoFile, videoCropInfo, readVideoFrame
from cmvUtils import flowVectorSplit
from outNC import creatNetCDF, writeCMVtoNC


parser = argparse.ArgumentParser(description='''This program uses phase correlation method from the TINT module
                                              to compute the cloud motion vectors in the hemispheric camera video''')
parser.add_argument('--input', type=str, help='Path to an input video or images.', default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
parser.add_argument('--fskip', type=str, help='Skip frames for better motion detection.', default=2)

args = parser.parse_args()

# Can not use all the RGB channels, so select one
chan = 2 #0-2
#The sky view will be divided into the square blocks of block size, say 32x32 pixels
nblock = 14
block_len = 32




print('Opening:', args.input)
video_cap = openVideoFile(args.input)

#get video frame and cropping info in a dictinary
inf = videoCropInfo(video_cap, nblock, block_len)
inf['fskip']=args.fskip
inf['input']=args.input

# showing video properties
print("Original Frame width '{}'".format(inf['frame_width']))
print("Original Frame Height : '{}'".format(inf['frame_height']))
print("Using cropped region: ", inf['x1'],":", inf['x2'], ",", inf['y1'], ":", inf['y2'])


ofile_name=creatNetCDF(inf)


fcount = 0
first_frame = True
tcount = 0

#plt.ion()
#flow_plot= plt.figure()

while video_cap.isOpened():
    fcount, frame = readVideoFrame(fcount, video_cap)
    

    # We skip given number of frames to compute the flow
    if fcount==1 or fcount % args.fskip == 0:
        sys.stdout.write('Current Frame:' + str(fcount)+ '\r')
        sys.stdout.flush()
        
        sky_new = frame[inf['x1']:inf['x2'], inf['y1']:inf['y2'], chan]
      
        #Store the sky data for first the frame as .
        if first_frame:
            sky_curr = sky_new
            sky_for_plot1 = frame[inf['x1']:inf['x2'], inf['y1']:inf['y2'], :]
            first_frame = False
            continue

        #move one frame forward
        sky_prev = sky_curr
        sky_curr = sky_new
        
        #I want to plot the frame1 with the arrow showing motion to next frame.
        sky_for_plot = sky_for_plot1
        sky_for_plot = cv.cvtColor(sky_for_plot, cv.COLOR_BGR2RGB)
        sky_for_plot1 = frame[inf['x1']:inf['x2'], inf['y1']:inf['y2'], :]
    

        cmv_x, cmv_y = flowVectorSplit(sky_prev, sky_curr, nblock)
        
        writeCMVtoNC(ofile_name, cmv_x, cmv_y, fcount, tcount)
        #increment the tcount after writing is done.
        tcount +=1
        exit()


        
        #plt.imshow(sky_for_plot)
        #plt.quiver(arrow_loc, arrow_loc, cmv_y, -cmv_x, scale=30)
        
        #fig_path = "./plots/image"+f'{fcount:05d}'+".png"
        #plt.savefig(fig_path)
        #plt.pause(0.3)
        #plt.close()


#plt.show()
#plt.ioff()

        
        
        
        
        
        

        

    
   
            

    
