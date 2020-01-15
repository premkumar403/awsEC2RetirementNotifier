# awsEC2RetirementNotifier
Python Lambda function to trigger slack notifications and any HTTP endpoint. The main goal is to give more information about the EC2 instance which is scheduled for retirement. If there are multiple kubernets clusters are hosted in different/same regions in the same account. It is harder to know this kube node is scheduled for retirement and what would be the impact. 

Idea is to use one lambda function per cluster and each triggers alert notification, only when an instance in that particular cluster is scheduled for retirement.