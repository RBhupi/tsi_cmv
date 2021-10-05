#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 4 10:03:50 2021

@author: Bhupendra Raut
"""

import argparse
import cv2 as cv
#from matplotlib import pyplot as plt
from phase_correlation import fft_flowvectors
from sys import exit
from time import sleep

parser = argparse.ArgumentParser(description='''This program uses phase correlation method from the TINT module
                                              to compute the cloud motion vectors in the hemispheric camera video''')
parser.add_argument('--input', type=str, help='Path to an input video or images.', default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
parser.add_argument('--fskip', type=str, help='Background subtraction method (KNN, MOG2).', default=30)

args = parser.parse_args()



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

while video_cap.isOpened():
    ret, frame = video_cap.read()
    fcount +=1 
    
    if not ret:
        video_cap.release()
        print("End of video reached!")
        break
    
    if fcount==1 or fcount % args.fskip == 0:
        print('Current Frame:', fcount)
        sky = frame[101:549, 16:464, :]
        
        #Store the sky data for first the frame as .
        if first_frame:
            sky_curr = sky
            first_frame = False
            continue

        #move one frame forward
        sky_prev = sky_curr
        sky_curr = sky
        
        
        mean_motion = fft_flowvectors(sky_prev[:, :, 2], sky_curr[:, :, 2], global_shift=True)
        print(mean_motion)
        
        cv.imshow("Original", frame)
        cv.waitKey(1000)
        

    
   
            
exit()
    
