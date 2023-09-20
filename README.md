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

 * Create storage account 

#### Azure Function App Hosted on Linux Consumption Plan
his sample Azure Resource Manager template deploys an Azure Function App on Linux Consumption plan and required resource including the app setting to deploy using zip package when remote build is needed.


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FMohamed-M-Zain%2Fazure-boards-automate-state-transition-parent-serverless%2Fmain%2Fzainfunction.json)



#### Architecture of project
##### Deployment with Azure Functions with HTTP Trigger



![architecture-diagram](https://github.com/Mohamed-M-Zain/azure-boards-automate-state-transition-parent-serverless/assets/144002170/42117d1c-769b-46e7-aa0e-ba48471fcada)




### Setup
1. Create a new Azure DevOps [personal access tokens](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows)
2. Update the rules in the JSON configuration file for each child work item type. In this example we are going to update the Task (rule.task.json). You will need an entry for each state.
   ```
   {
     "type": "Task",
     "rules": [
        {
          "ifChildState": "In progress",
          "notParentStates": [ "In progress", "Resolved", "Pending" ],
          "setParentStateTo": "In progress",
          "allChildren": false
         },
         {
          "ifChildState": "New",
          "notParentStates": [ "In progress", "Resolved", "New", "Pending" ],
          "setParentStateTo": "In progress",
          "allChildren": false
         },
         {
          "ifChildState": "Completed",
          "notParentStates": [],
          "setParentStateTo": "Completed",
          "allChildren": true
        }
      ]
    }
   ```

   **ifChildStates**: If the the work item status is this

   **notParentStates**: If the parent state is not one of these

   **setParentStateTo**: Then set the parent state to this

   **allChildren**: If true, then all child items need to be this state to update the parent

   #### Example 1

   User Story is set to New and it has 4 Tasks that are also new. As soon as a task is set to "In progress" then set the User Story to "In progress".

   ```
   {
     "ifChildState": "In progress",
     "notParentStates": [ "In progress", "Resolved" ],
     "setParentStateTo": "In progress",
     "allChildren": false
   },
   ```

   #### Example 2

   If User Story is "In progress" and all the child Tasks are set to "Completed". Then lets set the User Story to "Completed"

   ```
   {
    "ifChildState": "Completed",
    "notParentStates": [],
    "setParentStateTo": "Completed",
    "allChildren": false
   },
   ```

**Note:** If the states in your organization are **Active** and **Closed**, you should consider modifying the state configuration in the `rules.json` file.
* **In Progress**------------->**Active**
* **Completed**------------->**Closed**

3. In Storage account, create Container and upload the "rules.json" in it and copy URL of file and save it in NotePad.
  ![create_Container](https://github.com/Mohamed-M-Zain/azure-boards-automate-state-transition-parent-serverless/blob/main/images%20of%20project/photo1.png)
  ![upload_file](https://github.com/Mohamed-M-Zain/azure-boards-automate-state-transition-parent-serverless/blob/main/images%20of%20project/photo2.png)

4. create Shared access tokens to grant access to storage account resources for a specific time range without sharing your storage account key, copy SAS_taken and save it in NotePad.
   ![SAS_TOKEN](https://github.com/Mohamed-M-Zain/azure-boards-automate-state-transition-parent-serverless/blob/main/images%20of%20project/photo3.png)
   
5. take Zip_package.zip and upload it in new Container and copy URL of Zip_package.zip and save it in NotePad.
    **Note:** make anonymous access level in this state is container(anonymous read access for containers and blob)
   
7. deploy ARM Template to Azure.

 ![deploy_to_azure](https://github.com/Mohamed-M-Zain/azure-boards-automate-state-transition-parent-serverless/blob/main/images%20of%20project/photo4.png)






