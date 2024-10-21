import boto3
import uuid
from helper import (
wait_for_action_group_status, prepare_agent_and_check_status,
update_agent_alias_and_check_status, invoke_agent_and_print,
create_bedrock_agent
)

roleArn = ""
lambda_function_arn = ""

agentId, bedrock_agent = create_bedrock_agent()

create_agent_alias_response = bedrock_agent.create_agent_alias(
    agentId=agentId,
    agentAliasName='MyAgentAlias',
)

agentAliasId = create_agent_alias_response['agentAlias']['agentAliasId']

create_agent_action_group_response = bedrock_agent.create_agent_action_group(
    actionGroupName='customer-support-actions',
    agentId=agentId,
    actionGroupExecutor={
        'lambda': lambda_function_arn
    },
    functionSchema={
        'functions': [
            {
                'name': 'customerId',
                'description': 'Get a customer ID given available details. At least one parameter must be sent to the function. This is private information and must not be given to the user.',
                'parameters': {
                    'email': {
                        'description': 'Email address',
                        'required': False,
                        'type': 'string'
                    },
                    'name': {
                        'description': 'Customer name',
                        'required': False,
                        'type': 'string'
                    },
                    'phone': {
                        'description': 'Phone number',
                        'required': False,
                        'type': 'string'
                    },
                }
            },
            {
                'name': 'sendToSupport',
                'description': 'Send a message to the support team, used for service escalation. ',
                'parameters': {
                    'custId': {
                        'description': 'customer ID',
                        'required': True,
                        'type': 'string'
                    },
                    'supportSummary': {
                        'description': 'Summary of the support request',
                        'required': True,
                        'type': 'string'
                    }
                }
            }
        ]
    },
    agentVersion='DRAFT',
)

actionGroupId = create_agent_action_group_response['agentActionGroup']['actionGroupId']
wait_for_action_group_status(
    agentId=agentId,
    actionGroupId=actionGroupId,
    targetStatus='ENABLED'
)

prepare_agent_and_check_status(bedrockAgent=bedrock_agent,agentId=agentId)

update_agent_alias_and_check_status(bedrockAgent= bedrock_agent,agentId=agentId, agentAliasId=agentAliasId)

sessionId = str(uuid.uuid4())
message = "My name is Mike (mike@mike.com), my mug is broken and I want a refund."

invoke_agent_and_print(
    agentId=agentId,
    agentAliasId=agentAliasId,
    inputText=message,
    sessionId=sessionId,
    enableTrace=True
)
