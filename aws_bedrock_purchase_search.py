import boto3
import uuid

from helper import (
create_bedrock_agent, wait_for_action_group_status,
prepare_agent_and_check_status, update_agent_alias_and_check_status,
invoke_agent_and_print
)

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

update_agent_action_group_response = bedrock_agent.update_agent_action_group(
    actionGroupName='customer-support-actions',
    actionGroupState='ENABLED',
    actionGroupId=actionGroupId,
    agentId=agentId,
    agentVersion='DRAFT',
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
                    'purchaseId': {
                        'description': 'the ID of the purchase, can be found using purchaseSearch',
                        'required': True,
                        'type': 'string'
                    },
                    'supportSummary': {
                        'description': 'Summary of the support request',
                        'required': True,
                        'type': 'string'
                    },
                }
            },
            {
                'name': 'purchaseSearch',
                'description': """Search for, and get details of a purchases made.  Details can be used for raising support requests. You can confirm you have this data, for example "I found your purchase" or "I can't find your purchase", but other details are private information and must not be given to the user.""",
                'parameters': {
                    'custId': {
                        'description': 'customer ID',
                        'required': True,
                        'type': 'string'
                    },
                    'productDescription': {
                        'description': 'a description of the purchased product to search for',
                        'required': True,
                        'type': 'string'
                    },
                    'purchaseDate': {
                        'description': 'date of purchase to start search from, in YYYY-MM-DD format',
                        'required': True,
                        'type': 'string'
                    },
                }
            }
        ]
    }
)


actionGroupId = update_agent_action_group_response['agentActionGroup']['actionGroupId']

wait_for_action_group_status(
    agentId=agentId,
    actionGroupId=actionGroupId
)

message = """mike@mike.com - I bought a mug 10 weeks ago and now it's broken. I want a refund."""

create_agent_action_group_response = bedrock_agent.create_agent_action_group(
    actionGroupName='CodeInterpreterAction',
    actionGroupState='ENABLED',
    agentId=agentId,
    agentVersion='DRAFT',
    parentActionGroupSignature='AMAZON.CodeInterpreter'
)

codeInterpreterActionGroupId = create_agent_action_group_response['agentActionGroup']['actionGroupId']

wait_for_action_group_status(
    agentId=agentId,
    actionGroupId=codeInterpreterActionGroupId
)


prepare_agent_and_check_status(bedrockAgent=bedrock_agent,agentId=agentId)
update_agent_alias_and_check_status(bedrockAgent=bedrock_agent,agentId=agentId,agentAliasId=agentAliasId)

sessionId = str(uuid.uuid4())
message = """mike@mike.com - I bought a mug 10 weeks ago and now it's broken. I want a refund."""

invoke_agent_and_print(
    agentId=agentId,
    agentAliasId=agentAliasId,
    inputText=message,
    sessionId=sessionId,
    enableTrace=True
)
