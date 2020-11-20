from aws_cdk import core, aws_iam as iam
from deployment.titiler.config import StackSettings
from deployment.titiler.titiler_stacks import titilerLambdaStack, titilerECSStack
from deployment.stac_api.stac_api import StacApiStack

settings = StackSettings()

app = core.App()

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

titilerECSStack(
    app,
    f"{settings.name}-ecs-{settings.stage}",
    cpu=settings.task_cpu,
    memory=settings.task_memory,
    mincount=settings.min_ecs_instances,
    maxcount=settings.max_ecs_instances,
    env=DEPLOY_ENV
)

# titilerLambdaStack(
#     app,
#     f"{settings.name}-lambda-{settings.stage}",
#     memory=settings.memory,
#     timeout=settings.timeout,
#     concurrent=settings.max_concurrent,
#     env=DEPLOY_ENV
# )

StacApiStack(
    app,
    f"stac-api-{settings.stage}",
    env=DEPLOY_ENV
)

app.synth()