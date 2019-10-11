import xml.etree.ElementTree as ET
from collections import defaultdict
from statistics import mean
import sys
import numpy as np

gantry_per_componentloc=[]
Spooling_dict={}

def Pickup(f,LineBoardId,Recipe,Id):
    parser = ET.XMLParser(encoding="utf-8")
    context=ET.parse(f,parser=parser)
    pickup={'count_picks':[],'Components_Consumed':[],'ComponentsPlaced':[]}
    doc=context.getroot()
    try:
        for i in doc.iterfind('SiplaceMessage/ProductionEnded/ProductionResults/ProductionResult'):
            #count=count+1
            IGUID=i.find('PCB').attrib['IndividualGUID']
            Recipe=i.find('PCB').attrib['RecipeName']#i.find('ProductionResults/ProductionResult/PCB/RecipeName')
            InvID=i.find('PCB').attrib['IndividualID']#i.find('ProductionResults/ProductionResult/PCB/IndividualID')
            if IGUID==LineBoardId and Recipe==Recipe and InvID==Id:  #from boardhistory file
                component_locations=i.find('ConsumptionData/ComponentLocations')
                for j in component_locations.getiterator(tag='ComponentLocation'):
                    gantry_per_componentloc.append(j.find('FeederLocation').attrib['Location'])#list of all gantrys used for this board
                    pickup['count_picks'].append(j.find('ComponentConsumption').attrib['CountPicks'])
                    pickup['Components_Consumed'].append(j.find('ComponentConsumption').attrib['ComponentsConsumed'])
                    pickup['ComponentsPlaced'].append(j.find('ComponentConsumption').attrib['ComponentsPlaced'])
        var=[list(map(int,i)) for i in pickup.values()]
        pickup_rate=[round(((x/y)*100),2) for x,y in zip(var[2],var[1])]
        retrycount=[x-y for x,y in zip(var[1],var[2])]
        
        retcount_per_gantry,pickup_rate_pergantry=pickup_retry_per_gantry(pickup_rate,gantry_per_componentloc,retrycount)
        results=pickup_retry_per_gantry(pickup_rate,gantry_per_componentloc,retrycount)
        
        Spooling_dict['retcount_per_gantry']=results[0]
        #Spooling_dict['pickup_rate_pergantry']=results[1]
        Spooling_dict['pickup_rate_pergantry']=pickup_rate_pergantry['Average']
        global_pickup_rate=mean((pickup_rate_pergantry['Average'].values()))#global pickup success=average of mean pickup rate per gantry
        Spooling_dict['global_pickup_rate']=global_pickup_rate
        print('Spooling Dict ',Spooling_dict)
        return Spooling_dict
        #return retcount_per_gantry,pickup_rate_pergantry,global_pickup_rate #optional: pickup_rate,retrycount,gantry_per_componentloc
    except Exception as E:
        print(E)
        print('Error in line {}'.format(sys.exc_info()[-1].tb_lineno))


def pickup_retry_per_gantry(pickup_rate,gantry_per_componentloc,retrycount):
    #uniq_gantry= {key:None for key in list(set(gantry_per_componentloc))}
    #uniq_gantry.fromkeys(list(set(gantry_per_componentloc)))
    try:
        d=defaultdict(list)
        for i,v in list(zip(gantry_per_componentloc,retrycount)):#dictionary with retrycount per gantry
            d[i].append(v)
        p=defaultdict(list)
        for i,v in list(zip(gantry_per_componentloc,pickup_rate)):#dictionary with pickuprate per gantry
            p[i].append(v)
        p['Average']={i:round(np.mean(p[i]),2) for i in p.keys()}
        #p['Average']=[round(mean(x),2) for x in list(dict(p).values())]
        return dict(d),dict(p)
    except Exception as E:
        print(E)
        print('Error in line {}'.format(sys.exc_info()[-1].tb_lineno))


""" if __name__=='__main__':
    print('Testing') """


""" if __name__ == '__main__':
    f='OutputLogfile.xml.xml'
    LineBoardId='a74ff8e8-ad30-48a4-bf80-4935aac5144c'
    Recipe='TB228G\FP-T = 320 x 210'
    Id='625'
    count_picks=[]
    Components_Consumed=[]
    ComponentsPlaced=[]
    gantry_per_componentloc=[]
    print(Pickup(f,LineBoardId,Recipe,Id)) """
