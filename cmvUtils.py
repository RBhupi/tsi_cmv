#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 14:48:13 2021

@author: Bhupendra Raut
Parts of this module are adopted from TINT module phase_correlation.py
"""

import numpy as np
from scipy import ndimage
import cv2 as cv

def openVideoFile(fname):
    video_cap = cv.VideoCapture(fname)
    if not video_cap.isOpened():
        print('Unable to open: ', fname)
        exit(0)
        
    return video_cap



def readVideoFrame(fcount, capture):
        ret, frame = capture.read()
        fcount +=1 
    
        if not ret:
            capture.release()
            print("End of video reached!")
            exit()
        return fcount, frame


def flowVectorSplit(array1, array2, nblock):
    array1_split = split2DArray(array1, nblock)
    array2_split = split2DArray(array2, nblock)
    
    cmv_x = np.zeros(nblock*nblock)
    cmv_y = np.zeros(nblock*nblock)
    for i in range(nblock*nblock):
        cmv_x[i], cmv_y[i] = fftFlowVector(array1_split[i], array2_split[i])
    
    cmv_x, cmv_y = rmLargeValues(cmv_x, cmv_y)
    
    cmv_x = cmv_x.reshape([nblock, nblock])
    cmv_y = cmv_y.reshape([nblock, nblock])
    return cmv_x, cmv_y

def rmLargeValues(cmv_x, cmv_y, std_fact=1):
    
    vmag, vdir = vectorMagnitudeDirection(cmv_x, cmv_y)
    vmag_std = vmag[vmag>0].std()
    
    for i in range(0, cmv_x.size):
            if vmag[i]> vmag_std*std_fact:
                cmv_x[i]=0
                cmv_y[i]=0
    
    return cmv_x, cmv_y


def vectorMagnitudeDirection(cmv_x, cmv_y, std_fact=1):
    vec_mag = np.sqrt(cmv_x*cmv_x + cmv_y*cmv_y)
    
    #confirm this statement, we are not using this at this time
    #vec_dir = (270-np.rad2deg(np.arctan2(cmv_x,cmv_y)))%360 
    return vec_mag, np.NAN #vec_dir


def fftFlowVector(im1, im2, global_shift=True):
    """ Estimates flow vectors in two images using cross covariance. """
    if not global_shift and (np.max(im1) == 0 or np.max(im2) == 0):
        return None

    crosscov = fftCrossCov(im1, im2)
    sigma = (1/8) * min(crosscov.shape)
    cov_smooth = ndimage.filters.gaussian_filter(crosscov, sigma)
    dims = np.array(im1.shape)

    pshift = np.argwhere(cov_smooth == np.max(cov_smooth))[0]
    
    rs = np.ceil(dims[0]/2).astype('int')
    cs = np.ceil(dims[1]/2).astype('int')

    # Calculate shift relative to center - see fft_shift.
    pshift = pshift - (dims - [rs, cs])
    return pshift

def fftCrossCov(im1, im2):
    """ Computes cross correlation matrix using FFT method. """
    fft1_conj = np.conj(np.fft.fft2(im1))
    fft2 = np.fft.fft2(im2)
    normalize = abs(fft2*fft1_conj)
    normalize[normalize == 0] = 1  # prevent divide by zero error
    cross_power_spectrum = (fft2*fft1_conj)/normalize
    crosscov = np.fft.ifft2(cross_power_spectrum)
    crosscov = np.real(crosscov)
    return motionVector(crosscov)

def motionVector(fft_mat):
    """ Rearranges the cross correlation matrix so that 'zero' frequency or DC
    component is in the middle of the matrix. Taken from stackoverflow Que.
    30630632. """
    if type(fft_mat) is np.ndarray:
        rs = np.ceil(fft_mat.shape[0]/2).astype('int')
        cs = np.ceil(fft_mat.shape[1]/2).astype('int')
        quad1 = fft_mat[:rs, :cs]
        quad2 = fft_mat[:rs, cs:]
        quad3 = fft_mat[rs:, cs:]
        quad4 = fft_mat[rs:, :cs]
        centered_t = np.concatenate((quad4, quad1), axis=0)
        centered_b = np.concatenate((quad3, quad2), axis=0)
        centered = np.concatenate((centered_b, centered_t), axis=1)
        # Thus centered is formed by shifting the entries of fft_mat
        # up/left by [rs, cs] indices, or equivalently down/right by
        # (fft_mat.shape - [rs, cs]) indices, with edges wrapping. 
        return centered
    else:
        print('input to motionVector() should be a matrix')
        return


#Splits sky into given number of blocks. Not tested for uneven shapes 
#or nonfitting arrays
def split2DArray(arr2d, nblock):
    split_0 = np.array_split(arr2d, nblock, axis=0)
    split_arr=[]
    for arr in split_0:
        split_01 = np.array_split(arr, nblock, axis=1)
        split_arr += split_01
    
    return split_arr


