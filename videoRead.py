#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 13:06:48 2021

@author: Bhupendra Raut
"""

from sys import exit

import numpy as np
import cv2 as cv

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
    
    crop_info = cropMarginInfo(frame_height, frame_width, nblock, block_len)
    return crop_info





def videoCropInfoWaggle(camera, nblock, block_len):
    frame = camera.snapshot()
    frame_height = frame.data.shape[0]
    frame_width = frame.data.shape[1]
    
    crop_info = cropMarginInfo(frame_height, frame_width, nblock, block_len)
    return crop_info
    




def cropMarginInfo(frame_height, frame_width, nblock, block_len):
    crop_len = block_len * nblock
    if(crop_len >= min([frame_height, frame_width])):
        exit("Error: The original frame size is smaller than \
             the provided crop-dimensions.")
    cent_x = int(frame_width/2)
    cent_y = int(frame_height/2)
    
    #crop a square region of interest to accomodate 
    y1 = int(cent_y - crop_len/2)
    y2 = int(cent_y + crop_len/2)
    x1 = int(cent_x - crop_len/2)
    x2 = int(cent_x + crop_len/2)
    
    #compute approximate central points of each block
    mid_loc = np.arange((block_len/2) - 1, nblock * block_len, block_len)
    mid_loc= mid_loc.astype('int32')
    return dict(frame_width=frame_width, frame_height=frame_height, 
                x1=x1, x2=x2, y1=y1, y2=y2, cent_x=cent_x, cent_y=cent_y, 
                block_mid=mid_loc, nblock=nblock, block_len=block_len)





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
    fcount += 1 

    if not ret:
        capture.release()
        print("End of video reached!")
        return -1, frame
    return fcount, frame