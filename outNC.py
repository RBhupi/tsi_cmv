#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 17:17:43 2021

@author: Bhupendra Raut
"""

from netCDF4 import Dataset  
import numpy as np
from datetime import datetime
from os.path import basename, dirname, join
nblock=14
ofile = './data/new.nc'

def creatNetCDF(info):
    """ Create nc4 file for writing CMV data.

    Parameters
    ----------
    fname : String
        File name.
    info : python dictinary
        Information of the blocks and video where CMVs are computed.

    Returns
    -------
    None.

    """
    #make output netCDF file
    ofile = join(dirname(info['input']),"CMV_"+basename(info['input']).replace(".mpg", ".nc"))
    ncfile = Dataset(ofile, mode='w',format='NETCDF4_CLASSIC') 
    
    x_dim = ncfile.createDimension('x', info['nblock'])     
    y_dim = ncfile.createDimension('y', info['nblock'])
    t_dim = ncfile.createDimension('index', None) # unlimited time axis 
    
    #Create variables
    x = ncfile.createVariable('x', np.int32, ('x',))
    x.units = 'pixels'
    x.long_name = 'x'
    
    y = ncfile.createVariable('y', np.int32, ('y',))
    y.units = 'pixels'
    y.long_name = 'y'
    
    index = ncfile.createVariable('index', np.int32, ('index',))
    index.units = 'number'
    index.long_name = 'frame2 index as time steps'
    
    u = ncfile.createVariable('u', np.float32, ('index','x','y'), zlib=True, complevel=9)
    u.units = 'pixels'
    u.long_name = 'u component'
    
    v = ncfile.createVariable('v', np.float32, ('index','x','y'), zlib=True, complevel=9)
    v.units = 'pixels'
    v.long_name = 'v component'
    
    x[:] = info['block_mid']
    y[:] = info['block_mid']
    

    global_attributes(ncfile, info)
    
    ncfile.close()
    
    return ofile



def global_attributes(ncfile, info):
    creation_time=datetime.now()
    dt_string = creation_time.strftime("%b %d, %Y %H:%M:%S")
    ncfile.description = "CMVs computed for the hemispheric camera images"
    ncfile.created = dt_string
    ncfile.input_video=info['input']
    ncfile.BGR_chan=info['channel']
    ncfile.original_width = info['frame_width']
    ncfile.original_height = info['frame_height']
    ncfile.crop_x1 = info['x1']
    ncfile.crop_x2 = info['x2']
    ncfile.crop_y1 = info['y1']
    ncfile.crop_y2 = info['y2']
    ncfile.nblock = info['nblock']
    ncfile.block_len = info['block_len']
    ncfile.fleap = info['fleap']
    return


def writeCMVtoNC(nc_name, u, v, frame2_num, tcount):
    """
    

    Parameters
    ----------
    nc_name : String
        NetCDF file to append the data.
    u : Numpy array
        u component of CMV.
    v : Numpy array
        u component of CMV.
    frame2_num : Integer
        Frame number of the second frame used in computing CMV.
    tcount : Integer
        Frame index to be written in the netCDF file.

    Returns
    -------
    None.

    """
    ncfile = Dataset(nc_name, mode="a")
    ncfile['index'][tcount] = frame2_num-1
    ncfile['u'][tcount, :, :] = u
    ncfile['v'][tcount, :, :] = v
    ncfile.close()
    return 



