'''
/*******************************************************************
 * Project Name: Contour Plotting for Temperature, Salinity, etc 
 * File Name: lib_contour.py
 * Description: Open source library for contour plots of environmental data
 * Author: Umi-Reco 
 * License: MIT (see LICENSE file for details)
 ******************************************************************/
''' 

import os
import pandas as pd
import numpy as np
from   scipy.interpolate import griddata
from   scipy import signal

def make_contour_filepaths(dict_config):
    dir_base = dict_config['dir_base']
    dict_config['dir_contour']   = os.path.join(dir_base,dir_base + 'CTD_CONTOUR')
    os.makedirs(dict_config['dir_contour'],exist_ok=True)
    return dict_config


def make_contour_table(dict_config):

    font_size       = 18
    font_size_large = 32

    import matplotlib.pyplot as plt

    dep_levels = 4200.0
    lat_levels = 2000.0

    dep_max = dict_config['filters']['depth_max']
    dep_min = dict_config['filters']['depth_min']

    l_envdata   = dict_config['filters']['env_data']
    l_envdata_n = dict_config['filters']['env_data_names']
    data_bins   = np.arange(dep_min,dep_max,(dep_max-dep_min)/dep_levels)        
    lat_bins   = []

    l_columns   = ['lat','lon','dep']
    for c_envdata in l_envdata:
        l_columns.append('data.' + c_envdata)
    df_out      = pd.DataFrame(columns=l_columns)
    
    c_findex = 0

    for c_dive_id in dict_config['dive_id']:
        dir_base = dict_config['dir_base']
        dir_dive = os.path.join(dir_base,c_dive_id)
        dir_db   = os.path.join(dir_dive,c_dive_id + '_DB')
        path_gbb = os.path.join(dir_db,c_dive_id   + '.gbb.csv')
        path_out = os.path.join(dict_config['dir_contour'],'contour.csv')

        print('Processing > ' + str(path_gbb))

        df = pd.read_csv(path_gbb)
        df['dt_utc']   = pd.to_datetime(df['datetime'],format='mixed')   
        df['dt_local'] = pd.to_datetime(df['datetime_local'],format='mixed')  

        for c_envdata in l_envdata:
            df['data.' + c_envdata] = df[c_envdata].rolling(window=50).median()

        for c_data_bin in data_bins:
            j = np.argmin(np.abs(df['dep'] - c_data_bin))

            df_out.at[c_findex,'lat'] = df['lat'].iloc[10]
            df_out.at[c_findex,'lon'] = df['lon'].iloc[10]
            df_out.at[c_findex,'dep'] = df['dep'].iloc[j]

            if(np.abs((c_data_bin - df['dep'].iloc[j]) > 2.0)):
                print('Cannot match > ' + str(c_data_bin) + ' - ' + str(df['dep'].iloc[j]))
            #    df_out.at[c_findex,'salinity'] = df['salinity'].iloc[j]
                #else:

            for c_envdata in l_envdata:
                df_out.at[c_findex,'data.' + c_envdata] = df[c_envdata].iloc[j]

            #if c_data_bin == 10.0:
            #    lat_bins.append(df['lat'].iloc[j])

            c_findex = c_findex + 1

        lat_bins.append(df['lat'].iloc[10])

    df_out = df_out.sort_values('lat')

    df_out.to_csv(path_out,index=False)

    l_points = []
    for index,row in df_out.iterrows():
        l_points.append([row['lat'],row['dep']])
    x = lat_bins
    y = data_bins

    x1 = (np.arange(min(x),max(x),(max(x)-min(x))/lat_levels))
    y1 = y

    pts = np.array(l_points)

    for c_envdata,c_envdata_n in zip(l_envdata,l_envdata_n):
        l_values = df_out['data.' + c_envdata].to_list()

        val   = np.array(l_values)
        xr,yr = np.meshgrid(x1,y1)
        zr    = griddata(points=pts, values=val, xi=(xr, yr), method='cubic')

        num_levels = 750  # Adjust as needed for desired smoothness
        clr_levels = np.linspace(val.min(), val.max(), num_levels)
        
        f          = plt.figure(figsize=(35,9))
        p          = plt.contourf(xr,yr,zr, levels=clr_levels, cmap='jet')
        
        f.suptitle(c_envdata_n, fontsize=font_size_large)
        plt.xlabel("Station",fontsize=font_size)
        plt.ylabel("Depth (m)",fontsize=font_size)
        plt.ylim(dep_min, dep_max)

        plt.gca().invert_yaxis()
        plt.gca().invert_xaxis()

        plt.xticks(rotation=60)
        plt.xticks(lat_bins,['SC1', 'SC2', 'SC3','SR1'])
        plt.xticks(fontsize=font_size)
        plt.yticks(fontsize=font_size)

        cbar = f.colorbar(p)
        cbar.ax.tick_params(labelsize=font_size) 
        cbar.set_label(c_envdata_n, size=font_size,labelpad=font_size_large) # Change '15' to your desired font size


        path_fig = os.path.join(dict_config['dir_contour'],'contour_' + str(dep_min) + '-' + str(dep_max) + '_' + c_envdata + '.png')
        print('Saving > ' + path_fig)
        plt.savefig(path_fig)


    return dict_config