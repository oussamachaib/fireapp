# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 15:43:59 2021

@author: chaibou001
"""

from pylab import*
from matplotlib import*
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from matplotlib.pyplot import*

clean_columns=[
'N Test Enac',
'Code CA Manufacturer Plant',
'Production order (PO)',
'Drum',
'Cable',
'Diameter',
'Number of cables',
'Laboratory',
'Compound',
'Open or Closed Doors Humidity content',
'Humidity',
'Temperature',
'Safety Margin',
'Test date',
'Euroclasse',
'FS',
'THR1200s',
'HRRmax',
'Time',
'FIGRA',
'Euroclass',
'TSP1200s',
'Peak SPR',
'Smoke',
'Flaming inf 10s',
'Flaming sup 10s',
'Droplets']


################## Scripts in Pandas #####################

# Reading initial Excel table
def read_table_dirty(path):
    print('Reading file...')
    tic=time.time()
    # read excel sheet, skips first 7 lines
    df = pd.read_excel(path,0,skiprows=6)
    # clean columns
    df.columns=clean_columns
    elapsed= time.time()-tic
    print(f'- Successful. Time elapsed: {elapsed:2.3} seconds\n')
    return(df)

# Reading clean Excel table
def read_table(path):
    print('Reading file...')
    tic=time.time()
    # read excel sheet
    df = pd.read_excel(path,0)
    elapsed= time.time()-tic
    print(f'- Successful. Time elapsed: {elapsed:2.3} seconds\n')
    return(df)

def clean_table(df,path,save_file):
    print('Cleaning file...')
    tic=time.time()
    # create a new dataframe clean of lines with no cable name or humidity
    # deletes: (1) repeated lines due to merging (2) lines with no useful data (3) last empty block of lines
    df_clean=df.loc[(pd.isnull(df['Cable'])==False) & (pd.isnull(df['Humidity'])==False)  & (pd.isnull(df['Temperature'])==False) ]

    df_clean=df_clean[df_clean['Temperature']!='--']
    df_clean=df_clean[df_clean['Temperature']!='??']
    df_clean=df_clean[df_clean['Temperature']!='NC']   

    df_clean=df_clean[df_clean['Humidity']!='--']
    df_clean=df_clean[df_clean['Humidity']!='??']
    df_clean=df_clean[df_clean['Humidity']!='NC']
    
    df_clean=df_clean[df_clean['FS']!='-']
    df_clean=df_clean[df_clean['FS']!='--']
    df_clean=df_clean[df_clean['FS']!='??']
    df_clean=df_clean[df_clean['THR1200s']!='-']    
    df_clean=df_clean[df_clean['THR1200s']!='--']
    df_clean=df_clean[df_clean['THR1200s']!='??']

    df_clean=df_clean[df_clean['FIGRA']!='-']
    df_clean=df_clean[df_clean['FIGRA']!='--']
    df_clean=df_clean[df_clean['FIGRA']!='??']
    df_clean=df_clean[df_clean['FS']!='-']    
    df_clean=df_clean[df_clean['HRRmax']!='--']
    df_clean=df_clean[df_clean['HRRmax']!='??']
    
    # remove spaces (x here is a column, we can add index=1 if we want to navigate through rows)    
    df_clean['Cable']=df_clean['Cable'].str.strip().str.upper().str.replace(',','.').str.replace(' AS ',' (AS) ').str.replace('1000V','1KV').str.replace('1000 V','1KV')
    df_clean['Compound']=df_clean['Compound'].str.replace(' ','').str.replace('(','').str.replace(')','').str.replace(',','.').str.upper()
    
    # create excel writer
    writer = pd.ExcelWriter(path+'/'+save_file+'.xlsx')
    # write dataframe to excel sheet named save_file
    df_clean.to_excel(writer,index=False)
    # save the excel file
    writer.save()
    elapsed= time.time()-tic
    print(f'- Successful. Time elapsed: {elapsed:2.3} seconds\n')    
    print('Saved successfully to Excel sheet: '+save_file+'.xlsx')
    return 0

def statistics(df):
    print('[*] Statistics\n')
 
    site_distribution=df['Laboratory'].value_counts()
    cable_distribution=df['Cable'].value_counts()
    cmp_distribution=df['Compound'].value_counts()
    a=len(df)
    b=site_distribution
    c=cable_distribution[0:20]#.to_string()
    d=cmp_distribution[0:20]#.to_string()
    print('Fire test count:',a)
    print('\n\n')
    print('Site distribution:\n') 
    print(b) # Insert Pie chart here for data vizualization: will do it later
    print('\n\n')
    print('Cable distribution:\n')
    print(c)
    print('\n\n')
    print('Compound distribution:\n')
    print(d)
    print('\n\n')
    return a,b,c,d

def search(df,site,cable,compound):
    # another way to do it: look at the name of variables and try to play on their formatting
    a={site: 'Laboratory', cable: 'Cable', compound: 'Compound'}
    df_target=df
    for j,k in enumerate([site, cable, compound]):
        if(k!=''):
            df_target=df_target[df_target[a[k]]==k]
    return(df_target)

def plot_data(df,site,cable,compound,y,x,l):
    a={site: 'Laboratory', cable: 'Cable', compound: 'Compound'}
    df_target=df
    # Filter based on site + cable + compound
    for j,k in enumerate([site, cable, compound]):
        if(k!=''):
            df_target=df_target[df_target[a[k]]==k]
    # Filter based on x,y,l
    if(y=='HRRpeak'):
        y='HRRmax'
    y_axis=df_target[y]
    x_axis=df_target[x]
    if l!='nolegend':
        l_arr=df_target[l]
    else:
        l_arr=0
    return x_axis, y_axis, l_arr
