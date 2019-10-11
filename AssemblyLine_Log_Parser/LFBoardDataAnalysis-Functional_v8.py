import sys
import os
from lxml import etree
import glob
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import gc
from collections import Counter
from collections import defaultdict
import SpoolingDataHandler.Pickuprate as Pr
import SpoolingDataHandler.Analysis_RootInsert as Ar
#import All_Method as AM
#from Pickuprate.py import Pickup
from pathlib import Path

boardname=[]
componentcount=[]
componentcountperarea=[]
starttime=[]
completiontime=[]
processtime=[]
pt_pa_1=[]
pt_pa_2=[]
processtimeperarea=[]
pickup_retry_count=[]
max_retry_count=[]
Machine_type=[]
Machine_id=[]
BoardID=[]
Component_Count_per_hour_PA=[]
Component_Count_per_hour_Global=[]
cc_pa_1=[]
cc_pa_2=[]
pa_cc_dict={}
GantryID=[]
Gantry1pickupefficiency=[]
Gantry2pickupefficiency=[]
Gantry3pickupefficiency=[]
Gantry4pickupefficiency=[]
all_dataframes_dict={}
Spooling_dict={}
Retry_per_gantry={},
pickuprate_pergantry={}
#Gantry=[]
Retry_Gantry={}
x=[]
placeheadidglobal=[]
pickupefficiencypergantry=[]


# In[77]:

filename = glob.glob('Board*.xml')
print(filename)

def dataset_componentcount(root):
    stm=0
    datetimeformat='%Y-%m-%d %H:%M:%S.%f'
    posh=root.find("BoardHistory/PositionHistory")
    
    #component count for the processing position
    childm=root.find("BoardHistory/ProcessingHistory")
    
    #checking empty nodes
    if (len(childm))==0:
        print('No processinghistory in file ')
        #componentcount.append('None')
       # globcount.append(1)    
    else:
        cc=[]
        pt=[]
        pa=[]
        for i in childm.getiterator(tag='ProcessingPosition'):
            childn=i.find("ComponentCount")
            pachild=i.find("ProcessingArea")
            print(childn.text)
            cc.append(int(childn.text))#component count for the processing position
            pt.append(Processtime(i))
            pa.append(pachild.text)
           
        # print(pa)
        # print(pt)
        # print(cc)
            
        for i,v in enumerate(pt):
            if v==0:
                pt[i]=1
                print('changed pt\n')
        
        #CCPH per area
        compcount_per_pa=[i/j for i,j in zip(cc,pt)]#comp count per sec per pa
        Component_Count_per_hour_PA.append(round(sum(compcount_per_pa)*3600))
        
        
        #Comp count global
        componentcount.append(sum(cc))
        componentcountperarea.append(cc)
        processtime.append(sum(pt))
        processtimeperarea.append(pt)
        
        #CCPH global
        globalccps=sum(cc)/sum(pt)
        #print('globalccps',globalccps)
        globalccph=globalccps*3600
        
        #print('globalccph:\n', globalccph)
        Component_Count_per_hour_Global.append(round(globalccph))
        print('Component_Count_per_hour_Global:\n',Component_Count_per_hour_Global)
        
        cc_pt=zip(cc,pt)
        pa_cc_dict=dict(zip(pa,cc_pt))
        #print(pa_cc_dict)
        
        #print(list(pa_cc_dict.keys()))
        if list(pa_cc_dict.keys()) == ['0','1'] or list(pa_cc_dict.keys()) == ['1','0'] or list(pa_cc_dict.keys()) == ['1']:
            #print(list(pa_cc_dict.keys()))
            for i,v in pa_cc_dict.items():
                if i=='1':
                    cc_pa_1.append(v[0])
                    pt_pa_1.append(v[1])
                    cc_pa_2.append(None)
                    pt_pa_2.append(None)
        elif list(pa_cc_dict.keys()) == ['0','2'] or list(pa_cc_dict.keys()) == ['2','0'] or list(pa_cc_dict.keys()) == ['2']:
            #print(list(pa_cc_dict.keys()))
            for i,v in pa_cc_dict.items():
                if i == '2':
                    cc_pa_1.append(None)
                    pt_pa_1.append(None)
                    cc_pa_2.append(v[0])
                    pt_pa_2.append(v[1])
        elif list(pa_cc_dict.keys()) == ['1','2']:
            #print(list(pa_cc_dict.keys()))
            for i,v in pa_cc_dict.items():
                 if i=='1':
                    cc_pa_1.append(v[0])
                    pt_pa_1.append(v[1])
                 elif i=='2':
                    cc_pa_2.append(v[0])
                    pt_pa_2.append(v[1])


                    
   
        # print(cc_pa_1)
        # print(pt_pa_1)
        # print(cc_pa_2)
        # print(pt_pa_2)
        #return globcount
        
        
        
               
        
def Processtime(root):

    datetimeformat='%Y-%m-%d %H:%M:%S.%f'
    starttime=root.find('Approaching')
    compt=root.find('Completed')
    if (starttime.text)!=None and (compt.text)!=None:
        start=datetime.strptime(str(starttime.text),datetimeformat)
        comp=datetime.strptime(str(compt.text),datetimeformat)
        diff=comp-start
        ptime=diff.total_seconds()
        return int(ptime)
    else:
        return 0


# In[26]:


def Board_ID(root):
    print('in board id')
    childm=root.find("Id")
    #Retry_per_gantry,pickuprate_pergantry,global_pickuprate=Spooling(root,childm.text)
    Spooling_dict['Pickup']=[]
    #print(Spooling(root,childm.text))
    Spooling_dict['Pickup'].append(Spooling(root,childm.text))
    #Spooling_dict_for_df=Spooling(root,childm.text)
    #print(Spooling_dict)
    BoardID.append(childm.text)

    
def Spooling(root,Id):
    Spooling_dict['ID']=Id
    Spooling_dict['LineBoardId']=(root.find('LineBoardId')).text#'a74ff8e8-ad30-48a4-bf80-4935aac5144c'
    Spooling_dict['Recipe']=(root.find('Recipe')).text#TB228G\FP-T = 320 x 210'
    if not os.path.exists('SpoolingData\OutputLogfile.xml'):
        Ar.root_insertion()
    #f=sp_datafiles[0]
    f='SpoolingData\OutputLogfile.xml'#Spooling data file has fixed name
    #print(Pr.Pickup(f,(root.find('LineBoardId')).text,(root.find('Recipe')).text,Id))
    return Pr.Pickup(f,(root.find('LineBoardId')).text,(root.find('Recipe')).text,Id)


def MachineType_ID(root):
    childm=root.find('MachineType')
    #mt=childm.text
    childn=root.find('MachineId')
    #mi=childn.text
    #print(childn[2])
    if childm!=None:
        #for i in range(len(globcount)):
        Machine_type.append(childm.text)
    else:
        Machine_type.append('None')
    if childn!=None:
        #for i in range(len(globcount)):
        Machine_id.append(childn.text)
    else:
        Machine_id.append('None')
    Machine_Id,Machine_Name=zip(*(x.split('-') for x in Machine_id))
    #print(Machine_Name)


#BoardID.append(childm[0].text)
def Repicks(root):
    retrycount=[]
    placeheadidlist=[]#list of placehead with positive retry count

    childm=root.find("PlacePositions")
    if (len(childm))==0:
       # print('Data unavailable in file ',filename)
        retrycount.append(0)
    else:
        for PlacePosition in childm.getiterator(tag='PlacePosition'):#iterating through all tags=PlacePosition
            placeheadid=PlacePosition.find('PlaceHeadId')
            placeheadid=placeheadid.text                  #PlaceheadId info
            placeheadidglobal.append(placeheadid)     #List of all used PlaceheadId
            childn=PlacePosition.find('Component')
            #childn=PlacePosition.findall
            if childn==None:
                #print('Data unavailable in file ',filename)
                retrycount.append(np.nan)
            else:
                childp=PlacePosition.find('Component/RetryCount')
                retrycount.append(int(childp.text))
                if int(childp.text)>0:#if placeheadid has positive retry count it is added to list
                    placeheadidlist.append(placeheadid)

#Retry attempt per gantry
    Retry_Gantry=CountGantryperPlacePosition(placeheadidlist,root)

    #Placeheads per gantry
    Placeheadpergantry=CountGantryperPlacePosition(placeheadidglobal,root)
    
    #Gantry used for the board
    GantryID.append(Placeheadpergantry.keys())
    
    #Calculate efficiency per gantry           
    pickupefficiencypergantry.append(pickupefficiency_per_gantry(Placeheadpergantry,Retry_Gantry))
    #print('pickupefficiencypergantry:', pickupefficiencypergantry)
    
    #for display in dataframe
    s=[]
    for i in list(Retry_Gantry.items()):
            s.append(str(i[0])+':'+str(i[1]))
    x.append(s)

    # print('retrygantrydict list ',x)
    # print('Maximum retries: ',max(retrycount))
    # print('Total retry:',sum(retrycount))
    #for i in range(len(globcount)):
    max_retry_count.append(max(retrycount))
    pickup_retry_count.append(sum(retrycount))

def pickupefficiency_per_gantry(Placeheadpergantry,Retry_Gantry):
    pickup=Counter(Placeheadpergantry)
    retry=Counter(Retry_Gantry)
    sumofpickupandretry=dict(pickup+retry)
    pickupefficiency={}
    for i,v in Placeheadpergantry.items():
        pickupefficiency[i]=round(((v/sumofpickupandretry[i])*100),3)
    #print(pickupefficiency)
    addtolist(pickupefficiency)
    pickupefficiency=list(map(list,pickupefficiency.items()))
    #print(pickupefficiency)
    return(pickupefficiency)


# In[295]:


def addtolist(pickupefficiencypergantry):
    for i,v in pickupefficiencypergantry.items():
        if i=='1':
            print(v)
            Gantry1pickupefficiency.append(v)
        elif i=='2':
            print(v)
            Gantry2pickupefficiency.append(v)
        elif i=='3':
            print(v)
            Gantry3pickupefficiency.append(v)
        elif i=='4':
            print(v)
            Gantry4pickupefficiency.append(v)


# In[296]:


def CountGantryperPlacePosition(countlist,root):
    gantry_dict={}
    countlistunique=list(set(countlist))
    placeheads=root.find('PlaceHeads')
    for i in countlistunique:
        c=countlist.count(str(i))
        for p in placeheads.getiterator(tag='PlaceHead'):
            j=p.attrib.values()
            if j[0]==i:
                g=p.find('GantryId')
                g=g.text
                if g not in gantry_dict:
                    gantry_dict[g]=c
                
    print('Gantrydict:' , gantry_dict)
    return gantry_dict

def Retry_TrackEmpty_Correlation(filename,root):
    _ID_Retry_TrackEmpty={}
    _ID_Retry_TrackEmpty['File']=[]
    _ID_Retry_TrackEmpty['Id']=[]
    _ID_Retry_TrackEmpty['RetryCount']=[]
    _ID_Retry_TrackEmpty['TrackEmpty']=[]

    child=root.find('PlacePositions')
    if (len(child))==0:
       #print('Data unavailable in file ',filename)
        retrycount.append(0)
    else:
        for PlacePosition in child.getiterator(tag='PlacePosition'):
            id=PlacePosition.attrib.values()
            childn=PlacePosition.find('Component')
            #childn=PlacePosition.findall
            if childn==None:
                #print('Data unavailable in file ',filename)
                #retrycount.append(np.nan)
                for i in _ID_Retry_TrackEmpty.keys():
                    _ID_Retry_TrackEmpty[i].append(None) 
            else:
                childp=PlacePosition.find('Component/RetryCount')
                #retrycount.append(int(childp.tefxt))
                child_trackempty=PlacePosition.find('Component/TrackEmpty')
                #TrackEmpty.append(child_trackempty.text)

            
            if int(childp.text)!=0 or child_trackempty.text!='eUnspecified':
                _ID_Retry_TrackEmpty['RetryCount'].append(childp.text)
                _ID_Retry_TrackEmpty['TrackEmpty'].append(child_trackempty.text)
                _ID_Retry_TrackEmpty['File'].append(filename)
                _ID_Retry_TrackEmpty['Id'].append(id)
    TrackEmpty_Retry_df=pd.DataFrame.from_dict(_ID_Retry_TrackEmpty,orient='index').T
    all_dataframes_dict[filename]=TrackEmpty_Retry_df
    all_TrackEmpty_Retry_df=pd.concat(all_dataframes_dict.values())
    all_TrackEmpty_Retry_df.to_html('All_TrackEmpty_Retry_df.html')
    #TrackEmpty_Retry_df.to_html('TrackEmpty_Retry_df.html')
    #print(TrackEmpty_Retry_df)
    #return TrackEmpty_Retry_df

if __name__=='__main__':
    
    for f in filename:
        globcount=[]
        try:
            #fileload(f)
            boardname.append(f)
            doc=etree.parse(f)
            docn=doc.getroot()
            dataset_componentcount(docn)
            print(globcount)
            Board_ID(docn)
            MachineType_ID(docn)
            Repicks(docn)
            Retry_TrackEmpty_Correlation(f,docn)
            #Gantry_id(docn)
            #Processtime(doc)
        except Exception as e:
            print(e)
            print('Error in line {}'.format(sys.exc_info()[-1].tb_lineno))
            

    #Dataframe creation
    testar=[BoardID,boardname,cc_pa_1,cc_pa_2,componentcount,Component_Count_per_hour_PA,Machine_id,Machine_type,
            pt_pa_1,pt_pa_2,processtime,pickup_retry_count]
            #,max_retry_count,x,GantryID,Gantry1pickupefficiency,Gantry2pickupefficiency,Gantry3pickupefficiency,Gantry4pickupefficiency]
    header=['BoardID','Board_Name','Comp_pa_1','Comp_pa_2','Comp_Count_Global','Component_Count_per_hour_PA','Machine_ID','Machine_Type',
            'ProcTime_pa_1','ProcTime_pa_2','Process_Time','Component_Pickup_Retry_Count']
            #,'Maximum_Retry_Attempt','Retry attempt per Gantry','Gantry','Gantry1PickupSucc','Gantry2PickupSucc','Gantry3PickupSucc','Gantry4PickupSucc']
    #testar=[BoardID,boardname,cc_pa_1,cc_pa_2,componentcount,Component_Count_per_hour_PA,Machine_id,Machine_type,pt_pa_1,pt_pa_2,processtime,pickup_retry_count,max_retry_count,x,GantryID,Retry_per_gantry,pickuprate_pergantry,global_pickuprate]
    #header=['BoardID','Board_Name','Comp_pa_1','Comp_pa_2','Comp_Count_Global','Component_Count_per_hour_PA','Machine_ID','Machine_Type','ProcTime_pa_1','ProcTime_pa_2','Process_Time','Component_Pickup_Retry_Count','Maximum_Retry_Attempt','Retry attempt per Gantry','Gantry','Retry per Gantry(new)','Pickup Efficience per Gantry','Global Pickup Rate']

    tcdf=(pd.DataFrame(testar)).T
    tcdf.columns=header
    tcdf = tcdf.replace('None', np.nan, regex=True)

    Pickup_Retry_df=pd.DataFrame.from_dict(Spooling_dict['Pickup'])
    #print(Pickup_Retry_df)

    tcdf=pd.concat([tcdf,Pickup_Retry_df],axis=1)
    #Pickup efficiency
    #p=(tcdf['Comp_Count_Global'].div(tcdf['Comp_Count_Global']+tcdf['Component_Pickup_Retry_Count'],axis=0))*100
    #tcdf['Pickup_Success']=round(p,2)
    
    #os.chdir("..")

    if not os.path.exists('Analysis results'):
        os.makedirs('Analysis results')
    #Excel generation

    filepath='Analysis results\Boardhistorydataset.xls'
    tcdf.to_excel(filepath,index=False)
    #tcdf_html=tcdf.drop(['Gantry'], axis=1)
    tcdf.to_html('Analysis results\BoardHistoryTest.html')

