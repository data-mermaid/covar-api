import os
from aws_cdk import (
    core,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_events as events,
    aws_events_targets as targets,
    aws_elasticloadbalancingv2 as elb,
    aws_certificatemanager as certs,
    aws_route53 as route53,
)


class StacApiStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(
            self,
            'covar-vpc',
            vpc_name='dev-base-infrastructure/vpc'
        )

        cluster = ecs.Cluster.from_cluster_attributes(
            self,
            'covar-service-cluster',
            cluster_name='covar-service-cluster',
            vpc=vpc,
            security_groups=[]
        )

        lb = elb.ApplicationLoadBalancer(
            self,
            "LoadBalancer",
            vpc=vpc,
            internet_facing=True,
        )

        stac_api = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "stac-api",
            cluster=cluster,
            domain_zone=route53.HostedZone.from_lookup(
                self, "HostedZone", domain_name='tessellata.net'
            ),
            domain_name='api.tessellata.net',
            certificate=certs.Certificate.from_certificate_arn(
                self, 'domain-cert',
                certificate_arn='arn:aws:acm:us-east-1:138863487738:certificate/2832b798-d241-4d89-8b11-bdc9a377f173'
            ),
            load_balancer=lb,
            public_load_balancer=True,
            protocol=elb.ApplicationProtocol.HTTPS,
            redirect_http=True,
            cpu=1024,
            memory_limit_mib=2048,
            desired_count=2,
            # cloud_map_options=ecs.CloudMapOptions(
            #     cloud_map_namespace=namespace, name="mgmtapi"
            # ),
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(
                    "./stac-api/backend/"
                ),
                container_port=8080,
                environment={
                    "STAC_URL": "http://api.tessellata.net",
                    "TITILER_ENDPOINT": "https://titiler.tessellata.net",
                    "PORT": "27017",
                    "USER": os.getenv("MONGO_USER"),
                    "PASSWORD": os.getenv("MONGO_PASS"),
                    "HOST": "stac-monog-1ADLUZEF6X1HP-70e2bcd902084e54.elb.us-east-1.amazonaws.com",
                },
                enable_logging=True,
            ),
        )

        mongodb = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            'monogdb-service',
            cpu=2048,
            memory_limit_mib=4096,
            # task_definition=,
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry('mongo'),
                container_port=27017,
                environment={
                    "MONGO_INITDB_ROOT_USERNAME": os.getenv("MONGO_USER"), # TODO make more secure.
                    "MONGO_INITDB_ROOT_PASSWORD": os.getenv("MONGO_PASS") # TODO make more secure.
                },
                enable_logging=True,
            ),
            cluster=cluster,
            desired_count=1,
            listener_port=27017,
        )
