'''
/*******************************************************************
 * Project Name: Contour Plotting for Temperature, Salinity, etc 
 * File Name: contour_main.py
 * Description: Open source main program for executing the contour library
 * Author: Umi-Reco 
 * License: MIT (see LICENSE file for details)
 ******************************************************************/
''' 

from lib_contour import *


dict_config = {
    'dive_id':['Folder1','Folder2','Folder3','Folder4'],
    'dir_base':'/BaseFolderFullPath',
    'filters':{
        'depth_min':0,
        'depth_max':50,
        'env_data':['salinity','temperature_degC','conductivity_ms_cm','density_SigmaT','chl_flu_ppb','oxygen_gng_mg_l','turbidity_ftu'],
        'env_data_names':['Salinity','Temperature(C)','Conductivity(ms/cm)','SigmaT','Chlorophyll(ppb)','Oxygen(mg/l)','Turbidity(FTU)']
    }
}

dict_config = make_contour_filepaths(dict_config)

make_contour_table(dict_config)