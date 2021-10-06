#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 4 10:03:50 2021

@author: Bhupendra Raut
"""

import argparse
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from sys import exit

from cmvUtils import openVideoFile, readVideoFrame, flowVectorSplit

parser = argparse.ArgumentParser(description='''This program uses phase correlation method from the TINT module
                                              to compute the cloud motion vectors in the hemispheric camera video''')
parser.add_argument('--input', type=str, help='Path to an input video or images.', default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
parser.add_argument('--fskip', type=str, help='Background subtraction method (KNN, MOG2).', default=2)

args = parser.parse_args()

chan = 2 # The program does not use all the RGB channels
nblock = 14

print('Opening:', args.input)

video_cap = openVideoFile(args.input)

# showing video properties
print("Original Frame width '{}'".format(video_cap.get(cv.CAP_PROP_FRAME_WIDTH)))
print("Original Frame Height : '{}'".format(video_cap.get(cv.CAP_PROP_FRAME_HEIGHT)))




fcount = 0
first_frame = True
plt.ion()
flow_plot= plt.figure()

while video_cap.isOpened():
    fcount, frame = readVideoFrame(fcount, video_cap)
    

    # We skip given number of frames to compute the flow
    if fcount==1 or fcount % args.fskip == 0:
        print('Current Frame:', fcount)
        sky = frame[101:549, 16:464, chan] #too specific
      
        #Store the sky data for first the frame as .
        if first_frame:
            sky_curr = sky
            sky_for_plot1 = frame[101:549, 16:464, :]
            first_frame = False
            continue

        #move one frame forward
        sky_prev = sky_curr
        sky_curr = sky
        
        sky_for_plot = sky_for_plot1
        sky_for_plot = cv.cvtColor(sky_for_plot, cv.COLOR_BGR2RGB)
        sky_for_plot1 = frame[101:549, 16:464, :]
    
        
        cmv_x, cmv_y = flowVectorSplit(sky_prev, sky_curr, nblock)
        #exit()

        #compute central points for plotting the arrows
        arrow_loc = np.arange(15, 448, 32)
        
        plt.imshow(sky_for_plot)
        plt.quiver(arrow_loc, arrow_loc, cmv_y, -cmv_x, scale=30)
        
        fig_path = "./plots/image"+f'{fcount:05d}'+".png"
        plt.savefig(fig_path)
        plt.pause(0.3)
        plt.close()


plt.show()
plt.ioff()

        
        
        
        
        
        

        

    
   
            
exit()
    
