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

from cmvUtils import flowVectorSplit, fftFlowVector

parser = argparse.ArgumentParser(description='''This program uses phase correlation method from the TINT module
                                              to compute the cloud motion vectors in the hemispheric camera video''')
parser.add_argument('--input', type=str, help='Path to an input video or images.', default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
parser.add_argument('--fskip', type=str, help='Background subtraction method (KNN, MOG2).', default=2)

args = parser.parse_args()

chan = 2 # The program does not use all the RGB channels
nblock = 7

print('Opening:', args.input)

video_cap = cv.VideoCapture(args.input)

if not video_cap.isOpened():
    print('Unable to open: ', args.input)
    exit(0)
    
# showing video properties
print("Original Frame width '{}'".format(video_cap.get(cv.CAP_PROP_FRAME_WIDTH)))
print("Original Frame Height : '{}'".format(video_cap.get(cv.CAP_PROP_FRAME_HEIGHT)))




fcount = 0
first_frame = True
plt.ion()
flow_plot= plt.figure()
while video_cap.isOpened():
    ret, frame = video_cap.read()
    fcount +=1 
    
    if not ret:
        video_cap.release()
        print("End of video reached!")
        break
    
    if fcount==1 or fcount % args.fskip == 0:
        print('Current Frame:', fcount)
        sky = frame[101:549, 16:464, chan] #too specific
        
        #Store the sky data for first the frame as .
        if first_frame:
            sky_curr = sky
            first_frame = False
            continue

        #move one frame forward
        sky_prev = sky_curr
        sky_curr = sky
        
        
        
        mean_motion = fftFlowVector(sky_prev, sky_curr, global_shift=True)
        print(mean_motion)
        
        cmv_x, cmv_y = flowVectorSplit(sky_prev, sky_curr, nblock)
        

        #comput centra point for plotting arrows
        arrow_loc = np.arange(31, 448, 64)
        
        plt.imshow(sky_prev)
        plt.quiver(arrow_loc, arrow_loc, cmv_y, -cmv_x)
        plt.pause(0.3)
        plt.close()


plt.show()
plt.ioff()

        
        
        
        #cv.imshow("Original", frame)
        #cv.waitKey(1000)
        #exit()
        
        
        
        
        

        

    
   
            
exit()
    
