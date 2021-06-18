import boto3
import json
import datetime
import sys
import pandas as pd
import os

YES_STRING = '[YES]'
NO_STRING = '-'

#------------------------------------------------------
# limitToRegionList = {'us-east-1'}
# limitToTablesWithTag = {'Key':'Owner','Value':'blueTeam'}
# saveHTML=True
savePath = os.getcwd()+'/'


tableKeysToCopy = ['TableName','TableStatus','Replicas','TableSizeBytes','ItemCount']
tableDictsToCopy = ['ProvisionedThroughput','BillingModeSummary']
alarmKeysToCopy = ['AlarmName','AlarmStatus','ActionsEnabled','StateValue','MetricName','Namespace','Statistic']

importantAlarms = ['ConsumedReadCapacityUnits','ConsumedWriteCapacityUnits','ReadThrottleEvents','WriteThrottleEvents','ThrottledRequests','SuccessfulRequestLatency','SystemErrors']
importantGlobalAlarms = ['ReplicationLatency']


#------------------------------------------------------
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

#------------------------------------------------------
def saveDataframe(filename,dfTable,htmlTitle):
    dfTable.to_csv(savePath+filename+'.csv', index=False)    
    if 'saveHTML' in globals():
        with open(savePath+filename+'.html', "w") as file:
            file.write('<html lang="en"><head><meta charset="utf-8"><title>'+htmlTitle+'</title></head><body><H1>'+htmlTitle+'</H1>');
            file.write(dfTable.to_html(classes='table table-striped',index=False))
            file.write('</body></html>');

#------------------------------------------------------
if not ('limitToRegionList' in globals()) or (len(limitToRegionList) == 0):
    response = boto3.client("ec2").describe_regions()
    regions = response['Regions']
    limitToRegionList = []
    for region in regions:
        limitToRegionList.append(region['RegionName'])

#------------------------------------------------------
''' List all DynamoDB Tables in Account '''
#------------------------------------------------------
print("Listing DynamoDB Tables, GSIs, LSIs per region...\r\n")

myTables = []
gsi = []
lsi = []

for regionName in limitToRegionList:
    dynamodb = boto3.client("dynamodb",region_name=regionName)
    
    tablePaginator = dynamodb.get_paginator('list_tables')
    tableIterator = tablePaginator.paginate()
#    response = dynamodb.list_tables()
    for tablePage in tableIterator:
        for myTableName in tablePage['TableNames']: 
            #------------------------------------------------------
            ''' Tables '''
            #------------------------------------------------------
            tableDescription = dynamodb.describe_table(TableName=myTableName)['Table']
            tableSummary={}
            tableSummary['RegionName']=regionName
            globalSecondaryIndexes = []
            localSecondaryIndexes = []

            for keyToCopy in tableKeysToCopy:
                if keyToCopy in tableDescription:
                    tableSummary[keyToCopy]=tableDescription[keyToCopy]
            for dictToAdd in tableDictsToCopy:
                if dictToAdd in tableDescription:
                    tableSummary.update(tableDescription[dictToAdd])
                    
            tagsForTable=dynamodb.list_tags_of_resource(ResourceArn=tableDescription['TableArn'])
            if len(tagsForTable['Tags']) > 0:
#                print(myTableName)
#                print(tagsForTable['Tags'])
                reducedTags = {sub['Key'] : sub['Value'] for sub in tagsForTable['Tags']}
            else:
                reducedTags=NO_STRING
            tableSummary['Tags']=reducedTags
            
            if 'GlobalSecondaryIndexes' in tableDescription:
                tableSummary['GSIs']=YES_STRING
            else:
                tableSummary['GSIs']=NO_STRING
            if 'LocalSecondaryIndexes' in tableDescription:
                tableSummary['LSIs']=YES_STRING
            else:
                tableSummary['LSIs']=NO_STRING
            if 'Replicas' in tableDescription:
                tableSummary['Replicas']=YES_STRING
            else:
                tableSummary['Replicas']=NO_STRING
                        
            if not('limitToTablesWithTag' in globals()) or (len(limitToTablesWithTag)==0) or (any(d['Key'] == limitToTablesWithTag['Key'] and d['Value'] == limitToTablesWithTag['Value'] for d in tagsForTable['Tags'])):
                myTables.append(tableSummary.copy())
            
            #------------------------------------------------------
            ''' GSIs '''
            #------------------------------------------------------
            if 'GlobalSecondaryIndexes' in tableDescription:
                globalSecondaryIndexes = tableDescription['GlobalSecondaryIndexes']
                for singleGSI in globalSecondaryIndexes:
                    singleGSI['TableName'] = myTableName
                    singleGSI['RegionName'] = regionName  
#                    print(singleGSI)
                    gsi.append(singleGSI.copy())

            #------------------------------------------------------
            ''' LSIs '''
            #------------------------------------------------------
            if 'LocalSecondaryIndexes' in tableDescription:
                localSecondaryIndexes = tableDescription['LocalSecondaryIndexes']
                for singleLSI in localSecondaryIndexes:
                    singleLSI['TableName'] = myTableName
                    singleLSI['RegionName'] = regionName  
#                    print(singleLSI)
                    lsi.append(singleLSI.copy())
            
tables = pd.DataFrame(myTables)
tables.drop(columns=['NumberOfDecreasesToday','LastDecreaseDateTime','LastUpdateToPayPerRequestDateTime'],inplace=True,errors='ignore' )
tables.sort_values(by = ['RegionName', 'TableName'],inplace=True)

saveDataframe('tables',tables,'DynamoDB Tables')


gsitoCSV = pd.DataFrame(gsi)
saveDataframe('gsis',gsitoCSV,"Global Secondary Indexes")

lsitoCSV = pd.DataFrame(lsi)
saveDataframe('lsis',lsitoCSV,"Local Secondary Indexes")

#------------------------------------------------------
''' Metrics and Alarms '''
#------------------------------------------------------
cloudWatch = boto3.client("cloudwatch")

#------------------------------------------------------
''' Alarms '''
#------------------------------------------------------

print("")
print("Alarms...")


myMetricAlarms = []

alarmPaginator = cloudWatch.get_paginator('describe_alarms')
alarmIterator = alarmPaginator.paginate()
for alarmPage in alarmIterator:
    for myMetricAlarm in alarmPage['MetricAlarms']:
        alarmSummary = {}
    #    alarmDictsToAdd = {'Dimensions'}
        if 'Namespace' in myMetricAlarm and myMetricAlarm['Namespace'] == 'AWS/DynamoDB':
            alarmSummary['TableName']=myMetricAlarm['Dimensions'][0]['Value']
            for keyToCopy in alarmKeysToCopy:
                if keyToCopy in myMetricAlarm:
                    alarmSummary[keyToCopy]=myMetricAlarm[keyToCopy]
            for dictToAdd in tableDictsToCopy:
                if dictToAdd in myMetricAlarm:
                    alarmSummary.update(myMetricAlarm[dictToAdd])
            myMetricAlarms.append(alarmSummary.copy())

alarms = pd.DataFrame(myMetricAlarms)
saveDataframe('alarms',alarms,"Existing DynamoDB Cloudwatch Alarms")

#------------------------------------------------------
''' Composite Alarms '''
#------------------------------------------------------

# TO DO
# myCompositeAlarms = alarms['CompositeAlarms']
# print(myCompositeAlarms)


#------------------------------------------------------
''' Missing Alarms '''
#------------------------------------------------------


print("")
print("Missing Alarms...")

missingMetricAlarms=[]

for table in myTables:
    missedAlarmsOnTable = []
    missedDict = {}

    missedDict['Region Name'] = table['RegionName']
    missedDict['Table Name'] = table['TableName']
    
    if 'Replicas' in table and table['Replicas']==YES_STRING:
        missedDict['Global'] = YES_STRING
        for alarmToCheck in importantGlobalAlarms:
            if not any(d['TableName'] == table['TableName'] and d['MetricName'] == alarmToCheck for d in myMetricAlarms):
                missedAlarmsOnTable.append(alarmToCheck)
    else:
        missedDict['Global'] = NO_STRING
    for alarmToCheck in importantAlarms:
        if not any(d['TableName'] == table['TableName'] and d['MetricName'] == alarmToCheck for d in myMetricAlarms):
            missedAlarmsOnTable.append(alarmToCheck)
            
    if len(missedAlarmsOnTable) == 0:
        strListOfMissingAlarms=NO_STRING
    else:
        strListOfMissingAlarms = ",".join(missedAlarmsOnTable)
    missedDict['No CloudWatch Alarms For'] = strListOfMissingAlarms
    missingMetricAlarms.append(missedDict.copy())

missedAlarms = pd.DataFrame(missingMetricAlarms)
missedAlarms.to_csv('~/environment/missedAlarms.csv',index=False)
saveDataframe('missedAlarms',missedAlarms,"DynamoDB Tables - Important Metric Alarms not found")


#------------------------------------------------------

sys.exit(0)
