# Deployment

The API is comprised of a STAC API (with additional endpoints), a MongoDB, and a [Titiler](https://github.com/developmentseed/titiler) lambda API. In this directory you will find subdirectories for each. 

## Current State

- TiTiler is deplolyed as a Lambda function and API Gateway, with a route53 routing to titiler.tessellata.net. 
  - This deployment is done using Github actions where the Titiler repo is cloned during the workflow and deployed to AWS. 
  - The ECS version is still in the Stack file.
  - The CDK stack file was overridden (the one in the Titiler repo) here because it was causing errors.
- The STAC api was deployed and running, but Mongo was crashing every few minutes. This was happening on the last day of the hackathon and we decided to put our efforts in to getting content for the presentation.
  - The stack as is can be deployed again. From the ECS console, you can navigate to the mongo task and see the container starting and stopping. The logs can be viewed in Cloudwatch logs.
  - There wasn't an apparent solution at the time, but could be because we didn't mount a `/data/db` volume. Logs are difficult to decipher.
