from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_s3 as s3,
)
import aws_cdk as core
from aws_cdk import aws_s3 as s3
from constructs import Construct

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket for text files
        bucket = s3.Bucket(self, 
            "information-bucket",
            bucket_name="information-bucket-1231230123",  # Logical ID
            versioned=True,  # Enable versioning
            removal_policy=core.RemovalPolicy.DESTROY  # Retain the bucket after stack deletion
        )

        # Define the IAM role for the Lambda function with necessary permissions
        lambda_role = iam.Role(self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),  # Lambda service can assume this role
            description="Role with S3 full access and Secrets Manager read/write access",
        )
        # Attach S3 Full Access policy to the role
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        # Attach Secrets Manager read/write permissions to the role
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue", "secretsmanager:PutSecretValue"],
                resources=["*"]  # You can restrict to specific secrets using ARNs if needed
            )
        )
        # add permission to write to cloudwatch logs
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=["*"]
            )
        )

        # Create Lambda function
        lambda_function = _lambda.Function(self, "ProcessTextFileFunction",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="create_chunks.lambda_handler",
            code=_lambda.Code.from_asset("infrastructure/lambda/my_deployment_package.zip"),  
            role=lambda_role,
            environment={
                "BUCKET_NAME": bucket.bucket_name
            },
        )
        bucket.grant_read_write(lambda_function)

        notification = s3n.LambdaDestination(lambda_function)
        # Add the event notification to the bucket with a prefix filter
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            notification,
            s3.NotificationKeyFilter(prefix="texts/", suffix=".txt")  # Only trigger for objects with the prefix "uploads/"
        )

        # Output the S3 bucket name
        core.CfnOutput(self, "BucketName", value=bucket.bucket_name)