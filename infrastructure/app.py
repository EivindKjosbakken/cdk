#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.infrastructure_stack import InfrastructureStack
from constants import AWS_REGION, AWS_ACCOUNT_ID

app = cdk.App()
InfrastructureStack(app, "InfrastructureStack",
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
      env=cdk.Environment(account=AWS_ACCOUNT_ID, region=AWS_REGION),
    )

app.synth()
