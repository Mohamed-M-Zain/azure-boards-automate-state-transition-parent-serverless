# Azure Boards - Automate Parent State Transitions (Serverless Azure Functions )

## Overview
This project was created to help automate the updating of parent state transitions depending on the state of the child work items. By utilizing Serverless Azure Functions and ARM templates, you can streamline the process of transitioning parent work items when child work items are moved to specific states.

This API receives an Azure Boards work item update web hook event. The API will load the work item, check against a series of rules, and update it's parent work item accordingly.

For example, if your User Story is New and you create a task and set that task to active, the User Story should automatically be set to Active.

Another scenario (if we chose to handle so by enabling in rules), if all child tasks are completed, automatically set the parent work item to completed as well.

### Prerequisites
Before you get started with this project, make sure you have the following prerequisites in place:

* Azure DevOps Account: You should have access to an Azure DevOps organization where you can create and manage work items.

* Azure Subscription: You need an active Azure subscription to deploy Serverless Azure Functions and ARM templates.

#### Azure Function App Hosted on Linux Consumption Plan
his sample Azure Resource Manager template deploys an Azure Function App on Linux Consumption plan and required resource including the app setting to deploy using zip package when remote build is needed.


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/[https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2Fquickstarts%2Fmicrosoft.storage%2Fstorage-account-create%2Fazuredeploy.json])

#### Architecture of project
##### Deployment with Azure Functions with HTTP Trigger



![architecture-diagram](https://github.com/Mohamed-M-Zain/azure-boards-automate-state-transition-parent-serverless/assets/144002170/42117d1c-769b-46e7-aa0e-ba48471fcada)




###### Setup
1. Create a new Azure DevOps [personal access tokens](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows)



