#(C) Copyright Thousand Smiles Foundation 2023
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

#TSD.py
#Loads Thousand Smiles Data into Pandas Data Frames and
#consolidates several files for easier access
#DataFrames begin with prefix "df_" and can be found easily with Auto Complete
#FileLocations bigeing with prefix "file_loc_"

import pandas as pd

from os import listdir
from os.path import isfile, join

#centralized location for file paths

file_prefix = '../data/'

file_loc_clinic = file_prefix+'clinic_clinic-final.txt'
file_loc_register = file_prefix+'register_register-final.txt'
file_loc_patient = file_prefix+'patient_massaged.txt'
file_loc_images = file_prefix+'image_image-final.txt'
file_loc_history = file_prefix+'medicalhistory_medicalhistory-final.txt'
file_loc_routing = file_prefix+'routingslip_routingslip-final.txt'

#list of clinics
clinic_cols = ['id','location','start','end']
df_clinic = pd.read_csv(file_loc_clinic, encoding="latin-1", sep="__", engine ='python',names=clinic_cols).query('id != "id" and location != "location"')
N = 11 
# drop the first 11 rows, these were earlier clinics with restarts and
# not worth displaying
df_clinic = df_clinic.iloc[N: , :]
df_clinic['id'] = df_clinic['id'].astype(int)

#convert dates to datetime
date_cols = ['start','end']
df_clinic[date_cols] = df_clinic[date_cols].apply(pd.to_datetime)

#registration data
register_cols = ['id','timein','timeout','state','clinic_id','patient_id']
df_register = pd.read_csv(file_loc_register, header=None, names=register_cols, encoding="latin-1", sep="__", engine ='python').query('id != "id" and timein != "Sex"')
df_register['clinic_id'] = df_register['clinic_id'].astype(int)


#convert dates to datetime
date_cols = ['timein','timeout']
df_register[date_cols] = df_register[date_cols].apply(pd.to_datetime)

#add clinic data to df_register
df_merged = pd.merge(df_register.drop(['id','state'], axis=1), df_clinic, left_on="clinic_id", right_on="id")
df_merged['patient_id'] = df_merged['patient_id'].astype(int)
df_merged.drop('id',axis=1, inplace=True)


#patient data
patient_cols = ["id","dob","gender","city","colonia","state"]
df_patient = pd.read_csv(file_loc_patient, header=None, names=patient_cols, encoding="utf-8", sep="__", engine="python").query('id != "id" and dob != "dob"')
df_patient['id'] = df_patient['id'].astype(int)
df_patient.set_index('id',inplace=True)


#convert dates to datetime
date_cols = ['dob']
df_patient[date_cols] = df_patient[date_cols].apply(pd.to_datetime)

#create merged set
df_merged = pd.merge(df_patient, df_merged, left_on="id", right_on="patient_id")


#Colonia not named
df_merged.fillna({"colonia":"unlisted"},inplace=True)
                

#clinic dataframes
df_images = pd.read_csv(file_loc_images, encoding="latin-1", sep="__", engine="python")
df_headshot = df_images.copy(deep=True)
df_headshot = df_headshot[df_headshot['imagetype'] == 'h']
df_headshot.set_index('id',inplace=True)
df_headshot['clinic_id'] = df_headshot['clinic_id'].map(df_clinic['start'])
#Headshot from first 11 clinics will be removed
df_headshot.dropna(subset=['clinic_id'],inplace=True)
df_headshot

df_xray = df_images.copy(deep=True)
df_xray = df_xray[df_xray['imagetype'] == 'x']
df_xray['clinic_id'] = df_xray['clinic_id'].map(df_clinic.set_index('id')['start'])

df_routing = pd.read_csv(file_loc_routing, encoding="latin-1", sep="__", engine="python")
di = {'d': "Dental", 'r': "Returning Cleft", 'n': "New Cleft", 'o': "Ortho", 't': "Other", 'u': "Unknown", 'h': "Hearing Aids", 'e': "Ears"}
df_routing = df_routing.replace({"category": di})
df_routing['clinic_id'] = df_routing['clinic_id'].map(df_clinic['start'])

#medical history
df_medical = pd.read_csv(file_loc_history, encoding="latin-1", sep="__", engine="python")


