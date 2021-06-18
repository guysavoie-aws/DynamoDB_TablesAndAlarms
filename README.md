
# List DynamoDB Tables and CloudWatch Alarms
 
A Python script to generate a list of DynamoDB tables, related CloudWatch alarms, and given a list of important metrics, a list of tables with no alarms set for specific important metrics.
 
## Introduction
 
Amazon DynamoDB is a powerful serverless database that offers virtually unlimited scale when used efficiently. DynamoDB tables are easily provisioned through CLI, API, AWS Console, AWS CloudFormation, AWS Amplify and other services.


**DynamoDB Tables**
Summarizing the complete inventory of DynamoDB tables already provisioned across one or more regions is tedious for a non-trivial number of DynamoDB tables. Core attributes for DynamoDB tables commonly include:
 - capacity mode (provisioned, on demand) 
 - tags
 - current table size and item count 
 - global table 
 - global secondary indexes and local secondary indexes

**Monitoring with CloudWatch Alarms**
In [AWS Well Architected](https://aws.amazon.com/architecture/well-architected) effective monitoring of resources is a concern within the [Operational Excellence](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar) and https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar pillars.

Following best practices for [monitoring Amazon DynamoDB for operational awareness](https://aws.amazon.com/blogs/database/monitoring-amazon-dynamodb-for-operational-awareness/) improves visibility into the correct functioning of your DynamoDB tables.

## Pre-requisites
  
* An AWS Account with administrator access
* A bash command-line environment such as:
	* Mac Terminal
	* Windows bash shell
	* AWS Cloud9
	* AWS CloudShell
* Access to the [AWS CLI](https://aws.amazon.com/cli/) setup and configured
* [Python](https://www.python.org/) set up and configured
* [Pandas](https://pandas.pydata.org/) set up and configured

## Setup Steps

**Initial Setup**
1. Clone this repository to a folder in your working environment, or download to a working folder via the green button above.

2. Verify the AWS CLI is setup and running by running ```aws dynamodb describe-limits```. You should see no errors.

3. Open **DDB_TablesAndAlarm.py** with your code editor of choice to complete any desired configuration.

**Region Configuration**
When executed, the script will list all tables in all regions. To limit the script to tables within a subset of regions, find the following code, uncomment it, and enter a list of comma separated regions to query for DynamoDB tables:

	```# limitToRegionList = {'us-east-1'}```

**Tag Configuration**	
To limit the script to tables with a given tag, find the following code, uncomment it, and set the desired key and value properties to limit the query for DynamoDB tables:

```# limitToTablesWithTag = {'Key':'Owner','Value':'blueTeam'}```

**HTML Output**
To save the output to **html** as well as **csv**, find the following code and uncomment it:

```# saveHTML=True```

**Output Path**
To save the output to a path other than the current working directory, find the following code and change it to your prefered save path:

```savePath = os.getcwd()+'/'```

**Table Attributes to Include**
To configure the core table attributes to include in **tables.csv** find the following code and change it to your preferred attributes:

```tableKeysToCopy = ['TableName','TableStatus','Replicas','TableSizeBytes','ItemCount']```
```tableDictsToCopy = ['ProvisionedThroughput','BillingModeSummary']```
 
 **Alarm Attributes to Include**
To configure the core table attributes to include in **alarms.csv** find the following code and change it to your preferred attributes:

 ```alarmKeysToCopy = ['AlarmName','AlarmStatus','ActionsEnabled','StateValue','MetricName','Namespace','Statistic']```

**Important Missing Alarms to List if Missing**
To configure the missing metrics based alarms to be searched and included in **missedAlarms.csv** find the following code and change it to your preferred metrics:

```importantAlarms = ['ConsumedReadCapacityUnits','ConsumedWriteCapacityUnits','ReadThrottleEvents','WriteThrottleEvents','ThrottledRequests','SuccessfulRequestLatency','SystemErrors']```
```importantGlobalAlarms = ['ReplicationLatency']```

 ## Running the Script
In your bash command line environment, execute the script with the installed Python interpreter:

```python DDB_TablesAndAlarm.py```

You will see the following console output:

> Listing DynamoDB Tables, GSIs, LSIs per region...
> Alarms...
> Missing Alarms...
> Process exited with code: 0

 ## Script Output
When run against an AWS account, this script produces tabular CSV files with core attributes for:

 - DynamoDB tables (**tables.csv / tables.html**)
 - DynamoDB Global Secondary Indexes (**gsis.csv / gsis.html**)
 - DynamoDB Local Secondary Indexes (**lsis.csv / lsis.html**)
 - CloudWatch alarms for DynamoDB tables (**tables.csv / tables.html**)
 - Missing CloudWatch alarms (from a list of important metrics to query) (**missedAlarms.csv / missedAlarms.html**)

## Next Steps

Please contribute to this code sample by issuing a Pull Request or creating an Issue.

Share your feedback to: guypsavoie@gmail.com
