#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 17:12:16 2021

@author: Bhupendra Raut
"""

import argparse
import sys

import numpy as np
from matplotlib import pyplot as plt
from netCDF4 import Dataset

from videoRead import openVideoFile, readVideoFrame, videoCropInfo
import cv2 as cv


parser = argparse.ArgumentParser(description='''This program cloud motion vectors and cloud images 
                                 from the hemispheric camera video''')
#parser.add_argument('--video', type=str, help='Path to an input video or images.', 
#                    default="./data/sgptsimovieS01.a1.20160726.000000.mpg")
parser.add_argument('--cmv', type=str, help='CMV data file.', 
                    default="/Users/bhupendra/projects/cloud_motion/Python/CMV/data/sensitivity_test-V3/CMVsgptsimovieS01.a1.20160726.000000_i1f-l20p-bgr8-vmax07p-d1p-thrs2.nc")

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

for i in range(0, nframes_video-1):
    fcount, frame = readVideoFrame(fcount, video_cap)
    
    # We skip [fleap-1] numeber of frames to plot the flow
    if fcount==1 or fcount % fleap == 0:
        sys.stdout.write('Current Frame:' + str(fcount)+ '\r')
        sys.stdout.flush()
        sky = frame[inf['y1']:inf['y2'], inf['x1']:inf['x2'], :]
        sky = cv.cvtColor(sky, cv.COLOR_BGR2RGB)
    else:
        continue
    

    
    #u = ncfile['u'][tcount, :, :]
    #v = ncfile['v'][tcount, :, :]
    
    u_mean = ncfile['u_mean'][tcount]
    v_mean = ncfile['v_mean'][tcount]
    
    u_global = ncfile['u_global'][tcount]
    v_global = ncfile['v_global'][tcount]
    
    u = ncfile['u'][tcount]
    v = ncfile['v'][tcount]
    
    tcount+=1
    
    #u_mean = u[(np.abs(u)>0) | (np.abs(v)>0)].mean()
    #v_mean = v[(np.abs(u)>0) | (np.abs(v)>0)].mean()
    
    
    plt.imshow(sky, origin="lower")
    plt.quiver(185, 185, u_mean, v_mean, scale=10, color="b")
    plt.quiver(x, y, u, v, scale=25, color='dimgrey', width=0.005)
    #fig_path = "./plots/image"+f'{tcount:05d}'+".jpg"
    #plt.savefig(fig_path)
    plt.pause(0.5)
    plt.close()
    

plt.show()
plt.ioff()


    


ncfile.close()



#plt.quiver(x, y, u, v, scale=35)