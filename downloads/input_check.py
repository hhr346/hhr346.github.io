'''
This program aims to check if the data in input.json file is valid.
'''
import glob
import json
import datetime
import os
import h5py
import calendar
import numpy as np

def GF5_trans_GF5B_old(input_file):
    
    output_file =os.path.splitext(input_file)[0]+'_converted.h5'
    error_info='Convert GF5 spectrum sucessfully!'
    try:
        with h5py.File(input_file,'r') as fin:
            with h5py.File(output_file,'w') as fout:
                speccoeff = []
                rad = []
                radcoeff = []
                def copy_group_or_dataset(name, obj):
                    if isinstance(obj, h5py.Dataset):
                        if name == 'Channel_Attributes/DataField/SpecCaliCoeff':
                            speccoeff = np.array(obj[()])
                        elif name == 'Channel_Attributes/DataField/Radiance':
                            rad = np.array(obj[()])
                        elif name == 'Channel_Attributes/DataField/RadCaliCoeff':
                            radcoeff = np.array(obj[()])
                            fout.create_dataset('RadCaliCoeff/RadCaliCoeff', data=obj[()], dtype=obj.dtype,
                                                compression=obj.compression if 'compression' in obj.attrs else None,
                                                chunks=obj.chunks)

                        elif name == 'Channel_Attributes/GeolocationField/PixelQualityFlag':
                            fout.create_dataset('DataField/PixelQualityFlag', data=obj[()], dtype=obj.dtype,
                                                compression=obj.compression if 'compression' in obj.attrs else None,
                                                chunks=obj.chunks)
                        else:
                            desired_string = "/".join(name.split('/')[1:])
                            fout.create_dataset(desired_string, data=obj[()], dtype=obj.dtype,
                                              compression=obj.compression if 'compression' in obj.attrs else None,
                                              chunks=obj.chunks)        
                out = fin.visititems(copy_group_or_dataset)
                speccoeff = fin['Channel_Attributes/DataField/SpecCaliCoeff']
                rad = fin['Channel_Attributes/DataField/Radiance']
                radcoeff = fin['Channel_Attributes/DataField/RadCaliCoeff']

                nxtrack = np.shape(speccoeff)[0]
                nwavel = np.shape(rad)[2]
                wavel = np.zeros((nxtrack,nwavel))

                for i in range(0,nxtrack):
                    for j in range(0,nwavel):
                        wavel[i,j] = speccoeff[i,0] + speccoeff[i,1] * (j+1) + speccoeff[i,2] * (j+1) * (j+1)
                coeff = radcoeff * wavel
                dn = rad / coeff
                dn = np.nan_to_num(dn, nan=0.0, posinf=0.0, neginf=0.0)
                fout.create_dataset('DataField/DN',data=dn,dtype='float32',compression='gzip')
                fout.create_dataset('SpecCaliCoeff/Wavelength',data=wavel,dtype='float32',compression='gzip')
    except Exception as e:
        error_info='Convert GF5 spectrum error!'
    return error_info

def GF5_trans_GF5B(input_file):
    output_file = os.path.splitext(input_file)[0] + '_converted.h5'
    error_info = 'Convert GF5 spectrum successfully!'
    
    try:
        with h5py.File(input_file, 'r') as fin:
            with h5py.File(output_file, 'w') as fout:
                # 读取校准系数和辐射数据集的尺寸
                speccoeff = fin['Channel_Attributes/DataField/SpecCaliCoeff']
                rad = fin['Channel_Attributes/DataField/Radiance']
                radcoeff = fin['Channel_Attributes/DataField/RadCaliCoeff']
                
                nxtrack = speccoeff.shape[0]
                nwavel = rad.shape[2]  # 假设 Radiance 数据是三维的：行 x 列 x 波段

                # 创建用于存储结果的空数据集（启用分块存储）
                dn_shape = rad.shape
                dn = fout.create_dataset('DataField/DN', shape=dn_shape, dtype='float32', compression='gzip', chunks=True, maxshape=(None, None, rad.shape[2]))
                wavel = fout.create_dataset('SpecCaliCoeff/Wavelength', shape=(nxtrack, nwavel), dtype='float32', compression='gzip', chunks=True)

                # 计算波长
                print('Calculating wavelength...')
                wavel_data = np.zeros((nxtrack, nwavel), dtype=np.float32)
                for i in range(nxtrack):
                    for j in range(nwavel):
                        wavel_data[i, j] = speccoeff[i, 0] + speccoeff[i, 1] * (j + 1) + speccoeff[i, 2] * (j + 1) ** 2

                # 将计算得到的波长保存到文件
                wavel[:] = wavel_data  # 使用切片将数据写入文件

                print('Calculating DN...')
                # 按分块方式计算 DN（数字数值）
                chunk_size = 100  # 可根据内存调整块大小
                for i in range(0, dn_shape[0], chunk_size):  # 按行处理
                    for j in range(0, dn_shape[1], chunk_size):  # 按列处理
                        # 读取当前块的 rad 和 radcoeff 数据
                        rad_chunk = rad[i:i+chunk_size, j:j+chunk_size, :]
                        radcoeff_chunk = radcoeff[i:i+chunk_size]
                        wavel_chunk = wavel_data[i:i+chunk_size]

                        # 计算当前块的 DN
                        coeff_chunk = radcoeff_chunk * wavel_chunk
                        dn_chunk = np.nan_to_num(rad_chunk / coeff_chunk, nan=0.0, posinf=0.0, neginf=0.0)

                        # 将当前块结果写入文件
                        dn[i:i+chunk_size, j:j+chunk_size, :] = dn_chunk

    except Exception as e:
        error_info = f'Convert GF5 spectrum error! {str(e)}'
    
    return error_info



def input_check(json_file,logfile):
    json_file = open(json_file, 'r')
    input_file = json.load(json_file)
    # log_file.write('The parameters are as followed\n')
    # log_file.write(str(input_file))
    # log_file.write('\n')

    class request_data():
        def __init__(self) -> None:
            # Initialize the input data
            self.satellite = None
            self.gas = None
            self.start = None
            self.end = None
            self.lat_s = None
            self.lat_e = None
            self.lon_s = None
            self.lon_e = None
            self.outpath = None
    input_data = request_data()
    # Read the satellite and gas
    input_data.satellite = input_file['satellite'] 
    input_data.gas = input_file['gas']

    # Read the time period
    input_data.start = input_file['period']['start']
    input_data.end = input_file['period']['end']
    date_today = datetime.date.today()
    date_today = int(date_today.strftime("%Y%m"))

    # Read the area location
    input_data.lat_s = input_file['area']['lat_s']
    input_data.lat_e = input_file['area']['lat_e']
    input_data.lon_s = input_file['area']['lon_s']
    input_data.lon_e = input_file['area']['lon_e']

    # Read the outpath

    # Error check for the exceptions
    error_status = 1        # Only set to be zero when everything is ok
    if input_data.satellite not in ['GF5', 'DQ1', 'GF5B']:
        error_info = 'Error in the satellite selection! Only in [GF5, DQ1, GF5B]'
    elif input_data.gas not in ['HCHO', 'NO2', 'O3']:
        error_info = 'Error in the gas selection! Only in [HCHO, NO2, O3]'
    elif (input_data.lat_s > input_data.lat_e) or (input_data.lat_s < -15) or (input_data.lat_e > 30):
        error_info = 'Error in the latitude selection! Only in the range of [-15, 30]'
    elif (input_data.lon_s > input_data.lon_e) or (input_data.lon_s < 90) or (input_data.lon_e > 150):
        error_info = 'Error in the longitude selection! Only in the range of [90, 150]'
    else:
        # Check the time range
        # The initial time

        if ((input_data.gas=='HCHO') | (input_data.gas=='O3')):

           LV1_root = '../EMHCHO/out/'
           L1_header = input_data.satellite+'_EMI_' 
           file_s = sorted(glob.glob(LV1_root + L1_header+ str(input_data.start) + '*_UV2.h5'))
           file_e = sorted(glob.glob(LV1_root + L1_header+ str(input_data.end) + '*_UV2.h5'))

           if len(file_s)==0 or len(file_e)==0:
               if input_data.satellite == 'GF5':
                   # error_info = 'Error in the time range of GF5! Only in 2020.01-2020.12'
                   error_info = 'Error in the time range of GF5, Missing spectrum!'
               elif input_data.satellite == 'GF5B':
                   # error_info = 'Error in the time range of GF5B! Only in 2021.12-' + endtime
                   error_info = 'Error in the time range of GF5B, Missing spectrum!'
               elif input_data.satellite == 'DQ1':
                   # error_info = 'Error in the time range of DQ1! Only in 2022.06-' + endtime
                   error_info = 'Error in the time range of DQ1, Missing spectrum!'
           else:

               if input_data.satellite == 'GF5':
                  begin = datetime.date(int(str(input_data.start)[0:4]),int(str(input_data.start)[4:6]), 1)
                  endday=calendar.monthrange(int(str(input_data.end)[0:4]), int(str(input_data.end)[4:6]))[1]
                  end = datetime.date(int(str(input_data.end)[0:4]), int(str(input_data.end)[4:6]),endday )
               
                  nf_conv=0
                  d=begin
                  delta = datetime.timedelta(days=1)
                  while d<=end:
                     date_str = d.strftime("%Y%m%d")
                     d += delta
                     file_s = sorted(glob.glob(LV1_root + L1_header+ date_str + '*_UV2.h5'))
                     if len(file_s) > 0:
                        for L1_file in file_s:
                            conv_info=GF5_trans_GF5B(L1_file)
                            if conv_info=='Convert GF5 spectrum sucessfully!':
                               nf_conv=nf_conv+1
                  if nf_conv>0:
                      error_info = 'All parameters are valid'
                  else:
                      error_info = 'Error open in the spectrum of GF5!'
               else:
                  error_info = 'All parameters are valid'
        else:

           LV1_root = '../EMNO2/out/'
           L1_header = input_data.satellite+'_EMI_' 
           file_s = sorted(glob.glob(LV1_root + L1_header+ str(input_data.start) + '*_VI1.h5'))
           file_e = sorted(glob.glob(LV1_root + L1_header+ str(input_data.end) + '*_VI1.h5'))

           if len(file_s)==0 or len(file_e)==0:
               if input_data.satellite == 'GF5':
                   # error_info = 'Error in the time range of GF5! Only in 2020.01-2020.12'
                   error_info = 'Error in the time range of GF5, Missing spectrum!'
               elif input_data.satellite == 'GF5B':
                   # error_info = 'Error in the time range of GF5B! Only in 2021.12-' + endtime
                   error_info = 'Error in the time range of GF5B, Missing spectrum!'
               elif input_data.satellite == 'DQ1':
                   # error_info = 'Error in the time range of DQ1! Only in 2022.06-' + endtime
                   error_info = 'Error in the time range of DQ1, Missing spectrum!'
           else:
               error_info = 'All parameters are valid'
     
    if error_info == 'All parameters are valid':
        error_status = 0


    with open(logfile,'w') as log_file:
        log_file.write(error_info)
        log_file.write('\n')
    return input_file, error_info, error_status
   

