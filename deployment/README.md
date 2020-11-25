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
  - Keep in mind this is running in ECS, as a container. While the container gets ephemeral storage, We still need to configure the volume in the ECS task definition (which we did not get to). Even then, the data could be lost on restart. So in the short term, I was looking at creating an EBS volume that could be mounted to the container, but then only one container can use it at one time. Possibly EFS is an option. Ideally the API could use a more managed service so there is less complexity. An easy migration might be RDS (postgres?), a difficult migration but most cost effective would be DynamoDB.
  