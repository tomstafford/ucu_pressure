#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 17:49:28 2019

Munge some data, make some graphs from 

"Pressure Vessels: The epidemic of poor mental health among higher education staff" By Liz Morrish
https://www.hepi.ac.uk/wp-content/uploads/2019/05/HEPI-Pressure-Vessels-Occasional-Paper-20.pdf

Assumes conda environment saved in munge.yml
Assumes pdf of report downloaded as vessels.pdf and these lines run at the command line

pdftk vessels.pdf cat 55-57 output appendixA.pdf
pdftk vessels.pdf cat 59-61 output appendixB.pdf


"""

#--------------------------------------------------------------->>>> ESTABLISH THAT PROCESSING ENVIRONMENT!

import matplotlib.pyplot as plt #plotting
import socket #to get host machine identity
import os # for joining paths and filenames sensibly
import pandas as pd #dataframes
import numpy as np #number functions
import tabula #importing tables from pdfs. 98% works, 98% of the time

#test which machine we are on and set working directory
if 'tom' in socket.gethostname():
    os.chdir('/home/tom/t.stafford@sheffield.ac.uk/A_UNIVERSITY/toys/ucu_pressure')
else:
    print("I don't know where I am! ")
    print("Maybe the script will run anyway...")



#------------------------------------------------------------------------------------->>>> GET THAT DATA!
    

colnames=['Institution','2009','2010','2011','2012','2013','2014','2015','2016','2016Finished']

print("importing appendix A")

#import option #1
dfA = tabula.read_pdf("appendixA.pdf",multiple_tables=False,pages="1-3",lattice=True,pandas_options={'names': colnames})
#unique to option 1 corrections
dfA.loc[67,'2014']=np.NaN;dfA.loc[67,'2015']=np.NaN;
dfA.loc[69,'2014']=np.NaN;dfA.loc[69,'2015']=np.NaN;
dfA.loc[74,'2013']=15;dfA.loc[74,'2014']=24;dfA.loc[74,'2015']=25;
dfA.drop(75,inplace=True) #drop totals row
'''
#import option #2
dfA = tabula.read_pdf("appendixA.pdf",multiple_tables=False,pages="1-3") #98% of importing done in one line
#option 2 corrections
dfA.columns=['Institution','2009','2010','2011','2012','2013','2014','2015','2016','2016Finished'] #titles for columns
dfA.drop(0,inplace=True) #drop spare row
dfA.drop(82,inplace=True) #drop totals row
dfA['2016Finished']=dfA['2016Finished'].astype(str).apply(lambda x: x.translate({ord(ch): None for ch in ' 0123456789'})) #remove some funny extra numbers in the final column
dfA.loc[24,'Institution']='Royal Holloway';dfA.loc[24,'2016']=30;dfA.drop(23,inplace=True)
dfA.loc[28,'Institution']='Manchester Metropolitan University';dfA.loc[28,'2016']=145;dfA.drop(27,inplace=True)
dfA.loc[33,'Institution']='The Queen’s University of Belfast';dfA.loc[33,'2016']=94;dfA.drop(32,inplace=True)
dfA.loc[74,'2014']=np.NaN;dfA.loc[74,'2015']=np.NaN;
dfA.loc[76,'2014']=np.NaN;dfA.loc[76,'2015']=np.NaN;
dfA.loc[81,'2014']=24;dfA.loc[81,'2015']=25;
'''
#common corrections
dfA['2014']=pd.to_numeric(dfA['2014'],errors='ignore')
dfA['2015']=pd.to_numeric(dfA['2015'],errors='ignore')
dfA['Institution']=dfA['Institution'].apply(lambda x:str(x).replace('†',''))
dfA['Institution']=dfA['Institution'].apply(lambda x:str(x).replace('\r',' '))

#save to csv
dfA.to_csv('A_Counselling.csv')

dfA.sum(axis=0) #there may be labelling errors buy my total equals those reported, so all numbers are probably in the right place

print("importing appendix B")
dfB = tabula.read_pdf("appendixB.pdf",multiple_tables=False,pages="1-3",lattice=True,pandas_options={'names': colnames})
# more handcoded error correction
for col in ['2013','2014','2015','2016']:
    dfB[col]=pd.to_numeric(dfB[col].astype('str').apply(lambda x:x.replace(',','')),errors='coerce')
dfB['Institution']=dfB['Institution'].apply(lambda x:str(x).replace('†',''))
dfB['Institution']=dfB['Institution'].apply(lambda x:str(x).replace('\r',' '))
dfB['Institution']=dfB['Institution'].apply(lambda x: x.translate({ord(ch): None for ch in '0123456789'}))
dfB['Institution']=dfB['Institution'].apply(lambda x:str(x).replace(',',''))

#save to csv
dfB.to_csv('B_OccupationalHealth.csv')

dfB.sum(axis=0) #there may be labelling errors buy my total equals those reported, so all numbers are probably in the right place

#------------------------------------------------------------------------------------->>>> MAKE SOME GRAPHS!

C=dfA.sum(axis=0).drop(['Institution'])
O=dfB.sum(axis=0).drop(['Institution'])

#C=dfA.mean(axis=0)
#O=dfB.mean(axis=0)



lwparam=3
mark='o'
marksize=8
annofont=8
annocolor='gray'
annopos=(0.15,0.70)

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Year')
ax1.set_ylabel('Total recorded counselling Referrals', color=color)
ax1.plot(C[:-1], color=color,lw=lwparam)
ax1.plot(C[:-1], color=color,marker=mark,ms=marksize)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Total recorded occupational Health Referrals', color=color)  # we already handled the x-label with ax1
ax2.plot(O[:-1], color=color,lw=lwparam)
ax2.plot(O[:-1], color=color,marker=mark,ms=marksize)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped


#ax1.annotate('Data: "Pressure Vessels: The epidemic of \npoor mental health among higher education staff"\n - Liz Morrish/HEPI',xycoords='figure fraction',xy=(0.2,0.8),fontsize=7) 

plt.title('Data from "Pressure Vessels: The epidemic of \npoor mental health among higher education staff"\n - Liz Morrish/HEPI')
plt.savefig('figs/totals.png',bbox_inches='tight')


x=[year for year in range(2009,2017)]


for institution in dfA['Institution'].values:
    
    C=dfA[dfA['Institution']==institution].transpose().drop(['Institution','2016Finished'])
    
    O=dfB[dfB['Institution']==institution].transpose().drop(['Institution','2016Finished'])
    
    
    if (dfA[dfA['Institution']==institution]['2016Finished'].values[0]=='Yes'):
        finishedA=True
    else:
        finishedA=False
    
    try:
        if (dfB[dfB['Institution']==institution]['2016Finished'].values[0]=='Yes'):
            finishedB=True
        else:
            finishedB=False
    except:
        finishedB=True
    
    
    fig, ax1 = plt.subplots()
    
    
    color = 'tab:red'
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Counselling Referrals', color=color)
  
    ax1.plot(x,C, color=color,lw=lwparam)
    ax1.plot(x,C, color=color,marker=mark,ms=marksize)
    if (not finishedA) and (not finishedB):
       ax1.annotate('2016 counts incomplete\nfinal figure likely higher',xycoords='figure fraction',xy=annopos,fontsize=annofont,color=annocolor) 
    elif (not finishedA):
       ax1.annotate('2016 Counselling count\nincomplete final \nfigure likely higher',xycoords='figure fraction',xy=annopos,fontsize=annofont,color=annocolor)
    elif (not finishedB):
       ax1.annotate('2016 Occupational Health \ncount incomplete final \nfigure likely higher',xycoords='figure fraction',xy=annopos,fontsize=annofont,color=annocolor)
    
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xlim([2008.5,2016.5])
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    
    color = 'tab:blue'
    ax2.set_ylabel('Occupational Health Referrals', color=color)  # we already handled the x-label with ax1
    if O.empty is False:
        ax2.plot(x,O, color=color,lw=lwparam)
        ax2.plot(x,O, color=color,marker=mark,ms=marksize)
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    
    plt.title(institution+'\nData from "Pressure Vessels: The epidemic of \npoor mental health among higher education staff"\n - Liz Morrish/HEPI')
    plt.savefig('figs/'+institution +'.png',bbox_inches='tight')
    plt.close()

