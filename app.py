from aws_cdk import core, aws_iam as iam
from deployment.titiler.config import StackSettings
from deployment.titiler.titiler_stacks import titilerLambdaStack, titilerECSStack

settings = StackSettings()

app = core.App()

perms = []
if settings.buckets:
    perms.append(
        iam.PolicyStatement(
            actions=["s3:GetObject", "s3:HeadObject"],
            resources=[f"arn:aws:s3:::{bucket}*" for bucket in settings.buckets],
        )
    )

# # If you use dynamodb mosaic backend you should add IAM roles to read/put Item and maybe create Table
# stack = core.Stack()
# perms.append(
#     iam.PolicyStatement(
#         actions=[
#             "dynamodb:GetItem",
#             "dynamodb:PutItem",
#             "dynamodb:CreateTable",
#             "dynamodb:Scan",
#             "dynamodb:BatchWriteItem",
#         ],
#         resources=[f"arn:aws:dynamodb:{stack.region}:{stack.account}:table/*"],
#     )
# )


# Tag infrastructure
for key, value in {
    "Project": settings.name,
    "Stack": settings.stage,
    "Owner": settings.owner,
    "Client": settings.client,
}.items():
    if value:
        core.Tag.add(app, key, value)

DEPLOY_ENV = core.Environment(account='138863487738', region='us-east-1')

ecs_stackname = f"{settings.name}-ecs-{settings.stage}"
titilerECSStack(
    app,
    ecs_stackname,
    cpu=settings.task_cpu,
    memory=settings.task_memory,
    mincount=settings.min_ecs_instances,
    maxcount=settings.max_ecs_instances,
    permissions=perms,
    env=DEPLOY_ENV
)

lambda_stackname = f"{settings.name}-lambda-{settings.stage}"
titilerLambdaStack(
    app,
    lambda_stackname,
    memory=settings.memory,
    timeout=settings.timeout,
    concurrent=settings.max_concurrent,
    permissions=perms,
    env=DEPLOY_ENV
)

app.synth()