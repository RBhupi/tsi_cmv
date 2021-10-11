#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 17:12:16 2021

@author: Bhupendra Raut
"""

import argparse
import sys
from matplotlib import pyplot as plt
from netCDF4 import Dataset
from videoRead import openVideoFile, readVideoFrame, videoCropInfo
import numpy as np


parser = argparse.ArgumentParser(description='''This program cloud motion vectors and cloud images 
                                 from the hemispheric camera video''')
#parser.add_argument('--video', type=str, help='Path to an input video or images.', 
#                    default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
parser.add_argument('--cmv', type=str, help='CMV data file.', 
                    default="./data/CMV_sgptsimovieS01.a1.20160726.000000.nc")

args = parser.parse_args()



ncfile = Dataset(args.cmv, mode="r")
index = ncfile['index'][:]
x = ncfile['x'][:]
y = ncfile['y'][:]

video_file = ncfile.getncattr('input_video')
nblock = ncfile.getncattr('nblock')
block_len = ncfile.getncattr('block_len')
fleap = ncfile.getncattr('fleap')

nframes_video = fleap*index.size

video_cap = openVideoFile(video_file)

#get video frame and cropping info in a dictinary
inf = videoCropInfo(video_cap, nblock, block_len)

fcount = 0
tcount = 0
plt.ion()
flow_plot= plt.figure()
for i in range(0, nframes_video-1):
    fcount, frame = readVideoFrame(fcount, video_cap)
    
    # We skip [fleap-1] numeber of frames to plot the flow
    if fcount==1 or fcount % fleap == 0:
        sys.stdout.write('Current Frame:' + str(fcount)+ '\r')
        sys.stdout.flush()
        sky = frame[inf['x1']:inf['x2'], inf['y1']:inf['y2'], :]
    else:
        continue
    

    
    u = ncfile['u'][tcount, :, :]
    v = ncfile['v'][tcount, :, :]
    tcount+=1
    
    u_mean = u[(np.abs(u)>0) | (np.abs(v)>0)].mean()
    v_mean = v[(np.abs(u)>0) | (np.abs(v)>0)].mean()
    
    plt.imshow(sky)
    plt.quiver(224, 224, u_mean, v_mean, scale=5, color="b")
    
    plt.pause(0.3)
    plt.close()


plt.show()
plt.ioff()


    


ncfile.close()



#plt.quiver(x, y, u, v, scale=35)