#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 17:17:43 2021

@author: Bhupendra Raut
"""

from netCDF4 import Dataset  
import numpy as np

nblock=14
ofile = './data/new.nc'

def creatNetCDF(fname, x_loc, y_loc, ):
    """ Create nc4 file for writing CMV data.

    Parameters
    ----------
    fname : String
        File name.
    x_loc : Numpy array
        X-cordinate of the mid points of the blocks where CMVs are computed.
    y_loc : Numpy array
        Y-cordinate of the mid points of the blocks where CMVs are computed.

    Returns
    -------
    None.

    """
    ncfile = Dataset(fname, mode='w',format='NETCDF4_CLASSIC') 
    nblock_x = x_loc.size
    nblock_y = y_loc.size
    
    x_dim = ncfile.createDimension('x', nblock_x)     
    y_dim = ncfile.createDimension('y', nblock_y)
    t_dim = ncfile.createDimension('time', None) # unlimited time axis 
    ncfile.title='CMV data'
    ncfile.subtitle="CMVs computed using phase correlation method in hemispheric camera images."
    
    x = ncfile.createVariable('x', np.int32, ('x',))
    x.units = 'pixels'
    x.long_name = 'x'
    
    y = ncfile.createVariable('y', np.int32, ('y',))
    y.units = 'pixels'
    y.long_name = 'y'
    
    time = ncfile.createVariable('time', np.int32, ('time',))
    time.units = 'frame2 number'
    time.long_name = 'time steps'
    
    u = ncfile.createVariable('u', np.float32, ('time','x','y'), zlib=True, complevel=9)
    u.units = 'pixels'
    u.long_name = 'u component'
    
    v = ncfile.createVariable('v', np.float32, ('time','x','y'), zlib=True, complevel=9)
    v.units = 'pixels'
    v.long_name = 'v component'
    
    x[:] = x_loc
    y[:] = y_loc
    
    ncfile.close()
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
        Time index for writing in the netCDF file.

    Returns
    -------
    None.

    """
    ncfile = Dataset(nc_name, mode="a")
    ncfile['time'][tcount] = frame2_num
    ncfile['u'][tcount, :, :] = u
    ncfile['v'][tcount, :, :] = v
    ncfile.close()
    return 



