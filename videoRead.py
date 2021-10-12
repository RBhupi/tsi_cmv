#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 13:06:48 2021

@author: Bhupendra Raut
"""


import numpy as np
from scipy import ndimage
import cv2 as cv
from sys import exit

def openVideoFile(fname):
    """
    Opens video file using openCV VideoCapture.
    
    Exits when file is not availbale. 

    Parameters
    ----------
    fname : input file 

    Returns captured object
    -------
    video_cap : openCV VideoCapture object

    """
    video_cap = cv.VideoCapture(fname)
    if not video_cap.isOpened():
        print('Unable to open: ', fname)
        exit(0)
        
    return video_cap



def videoCropInfo(video_cap, nblock, block_len):
    frame_width = video_cap.get(cv.CAP_PROP_FRAME_WIDTH)
    frame_height = video_cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    
    crop_len = block_len*nblock
    if(crop_len >= min([frame_height, frame_width])):
        exit("Error: The original frame size is smaller than \
             the provided crop-dimensions.")
    
    #crop a square region of interest to accomodate 
    y1 = int((frame_height/2)-(nblock/2*block_len))
    y2 = int((frame_height/2)+(nblock/2*block_len))
    x1 = int((frame_width/2)-(nblock/2*block_len))
    x2 = int((frame_width/2)+(nblock/2*block_len))
    
    #compute approximate central points of each block
    mid_loc = np.arange((block_len/2)-1, nblock*block_len, block_len)
    return dict(frame_width=frame_width, frame_height=frame_height, 
                x1=x1, x2=x2, y1=y1, y2=y2, block_mid=mid_loc, nblock=nblock,
                block_len=block_len)



def readVideoFrame(fcount, capture):
    """
    Exits when file ends.
    
    Parameters
    ----------
    fcount : frame read till now
    capture : openCV VideoCapture object

    Returns
    -------
    fcount : frame count increamented by 1
    frame : video frame 

    """
    ret, frame = capture.read()
    fcount +=1 

    if not ret:
        capture.release()
        print("End of video reached!")
        exit()
    return fcount, frame