#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 17:17:43 2021

@author: Bhupendra Raut
"""



from datetime import datetime
from os.path import basename, dirname, join

import numpy as np
from netCDF4 import Dataset


nblock = 14
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
    
    @toDo Total number of frames in the video are not reading correctly by 
    the openCV capture (shows 20), possibly compression chunk size equals 20. 
    Hence, I can not estimate values of the index dimention, which is now 
    written at every step in one of the data writting fucntions. 
    This can be later moved to the file creation function.
    """
    #make output netCDF file
    dir_name = dirname(info['input'])
    
    run_id = ('_i'+str(info['fleap'])+"f-l"+str(info['block_len'])
    +'p-bgr'+str(info['channel'])+'-vmax'+str(info['v_max']).zfill(2)+'p-d'
    +str(info['WS05-neighborhood_dist'])+'p-thrs'
    +str(info['WS05-error_thres']))
    
    ofile_name ="CMV" + basename(info['input']).replace(".mpg", run_id+".nc")
    ofile = join(dir_name, "CMV_SGP-C01_V2", ofile_name)
    ncfile = Dataset(ofile, mode='w',format='NETCDF4_CLASSIC') 
    
    x_dim = ncfile.createDimension('x', info['nblock'])     
    y_dim = ncfile.createDimension('y', info['nblock'])
    t_dim = ncfile.createDimension('time', None)
    
    #Create variables
    x = ncfile.createVariable('x', np.int32, ('x',))
    x.units = 'pixels'
    x.long_name = 'block-center along x-axis'
    
    y = ncfile.createVariable('y', np.int32, ('y',))
    y.units = 'pixels'
    y.long_name = 'block-center along y-axis'
    
    time = ncfile.createVariable('time', np.int32, ('time',))
    time.units = 'seconds since 1970-01-01 00:00:00 +00:00:00'
    time.long_name = 'frame2 time'
    
    u = ncfile.createVariable('u', np.float32, ('time','y','x'), 
                              zlib=True, complevel=9)
    u.units = 'pixel/time-steps'
    u.long_name = 'u component'
    
    #u_nmf = ncfile.createVariable('u_nmf', np.float32, ('time','x','y'), 
      #                        zlib=True, complevel=9)
    #u_nmf.units = ''
    #u_nmf.long_name = 'Normalized median fluctuation of u component'
    
    #v_nmf = ncfile.createVariable('v_nmf', np.float32, ('time','x','y'), 
     #                         zlib=True, complevel=9)
    #v_nmf.units = ''
    #v_nmf.long_name = 'Normalized median fluctuation of v component'
    
    v = ncfile.createVariable('v', np.float32, ('time','y','x'), 
                              zlib=True, complevel=9)
    v.units = 'pixel/time-steps'
    v.long_name = 'v component'
    
    u_global = ncfile.createVariable('u_global', np.float32, ('time'), 
                              zlib=True, complevel=9)
    u_global.units = 'pixel/time-steps'
    u_global.long_name = 'u component of global CMV'
    
    v_global = ncfile.createVariable('v_global', np.float32, ('time'), 
                              zlib=True, complevel=9)
    v_global.units = 'pixel/time-steps'
    v_global.long_name = 'v component of global CMV'
    
    
    u_mean = ncfile.createVariable('u_mean', np.float32, ('time'), 
                                   zlib=True, complevel=9)
    u_mean.units = 'pixel/time-steps'
    u_mean.long_name = 'mean u over the domain'
    
    v_mean = ncfile.createVariable('v_mean', np.float32, ('time'), 
                                   zlib=True, complevel=9)
    v_mean.units = 'pixel/time-steps'
    v_mean.long_name = 'mean v over the domain'
    
    x[:] = info['block_mid']
    y[:] = info['block_mid']
    

    writeGlobalAttributes(ncfile, info)
    
    ncfile.close()
    
    return ofile



def writeGlobalAttributes(ncfile, info):
    creation_time=datetime.now()
    dt_string = creation_time.strftime("%b %d, %Y %H:%M:%S")
    ncfile.description = "CMVs computed over a suqare grid in the hemispheric camera images"
    ncfile.created = dt_string
    ncfile.input_video=info['input']
    ncfile.channel = info['channel']
    ncfile.channel_description = "0=Blue, 1=Green, 2=Red, 8=Red/Blue, 9=Gray"
    ncfile.original_width = info['frame_width']
    ncfile.original_height = info['frame_height']
    ncfile.center_x = info['cent_x']
    ncfile.center_y = info['cent_y']
    ncfile.crop_x1 = info['x1']
    ncfile.crop_x2 = info['x2']
    ncfile.crop_y1 = info['y1']
    ncfile.crop_y2 = info['y2']
    ncfile.nblock = info['nblock']
    ncfile.block_len = info['block_len']
    ncfile.fleap = info['fleap']
    ncfile.v_max = info['v_max']
    ncfile.WS05_dist = info['WS05-neighborhood_dist']
    ncfile.WS05_eps = info['WS05-eps']
    ncfile.WS05_thres = info['WS05-error_thres']
    return


def writeCMVtoNC(nc_name, u, v, ftime, tcount):
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
        Frame time to be written in the netCDF file.

    Returns
    -------
    None.

    """
    ncfile = Dataset(nc_name, mode="a")
    #One of the writing functions must have following statement, 
    ncfile['time'][tcount] = ftime
    ncfile['u'][tcount, :, :] = u
    ncfile['v'][tcount, :, :] = v
    ncfile.close()
    return 



def writeNMFtoNC(nc_name, u_nmf, v_nmf, frame2_num, tcount):
    ncfile = Dataset(nc_name, mode="a")
    #One of the writing functions must have following statement, 
    #ncfile['time'][tcount] = frame2_num-1
    ncfile['u_nmf'][tcount, :, :] = u_nmf
    ncfile['v_nmf'][tcount, :, :] = v_nmf
    ncfile.close()
    return 



def writeGlobalCMVtoNC(nc_name, ug, vg, frame2_num, tcount):
    """
    
    Parameters
    ----------
    nc_name : String
        NetCDF file to append the data.
    u_mean : Numpy array

    v_mean : Numpy array

    frame2_num : Integer
        Frame number of the second frame used in computing CMV.
    tcount : Integer
        Frame time to be written in the netCDF file.

    Returns
    -------
    None.

    """
    ncfile = Dataset(nc_name, mode="a")
    
    #One of the writing functions must have following statement, 
    #ncfile['time'][tcount] = frame2_num-1
    
    ncfile['u_global'][tcount] = ug
    ncfile['v_global'][tcount] = vg
    ncfile.close()
    return 



def writeMeanCMVtoNC(nc_name, u_mean, v_mean, frame2_num, tcount):
    """
    
    Parameters
    ----------
    nc_name : String
        NetCDF file to append the data.
    u_mean : Numpy array

    v_mean : Numpy array

    frame2_num : Integer
        Frame number of the second frame used in computing CMV.
    tcount : Integer
        Frame time to be written in the netCDF file.

    Returns
    -------
    None.

    """
    ncfile = Dataset(nc_name, mode="a")
    
    #One of the writing functions must have following statement, 
    #ncfile['time'][tcount] = frame2_num-1
    
    ncfile['u_mean'][tcount] = u_mean
    ncfile['v_mean'][tcount] = v_mean
    ncfile.close()
    return 




