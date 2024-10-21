import boto3
import uuid
from helper import (
    create_bedrock_agent, wait_for_agent_status,
    prepare_agent_and_check_status,wait_for_agent_alias_status,
    update_agent_alias_and_check_status, invoke_agent_and_print
)

agentId, bedrock_agent = create_bedrock_agent()

wait_for_agent_status(
    agentId=agentId,
    targetStatus='NOT_PREPARED'
)


prepare_agent_and_check_status(bedrockAgent=bedrock_agent, agentId=agentId)

create_agent_alias_response = bedrock_agent.create_agent_alias(
    agentId=agentId,
    agentAliasName='MyAgentAlias',
)

agentAliasId = create_agent_alias_response['agentAlias']['agentAliasId']

wait_for_agent_alias_status(
    agentId=agentId,
    agentAliasId=agentAliasId,
    targetStatus='PREPARED'
)

bedrock = boto3.client(service_name='bedrock', region_name='us-west-2')

create_guardrail_response = bedrock.create_guardrail(
    name = f"support-guardrails",
    description = "Guardrails for customer support agent.",
    topicPolicyConfig={
        'topicsConfig': [
            {
                "name": "Internal Customer Information",
                "definition": "Information relating to this or other customers that is only available through internal systems.  Such as a customer ID. ",
                "examples": [],
                "type": "DENY"
            }
        ]
    },
    contentPolicyConfig={
        'filtersConfig': [
            {
                "type": "SEXUAL",
                "inputStrength": "HIGH",
                "outputStrength": "HIGH"
            },
            {
                "type": "HATE",
                "inputStrength": "HIGH",
                "outputStrength": "HIGH"
            },
            {
                "type": "VIOLENCE",
                "inputStrength": "HIGH",
                "outputStrength": "HIGH"
            },
            {
                "type": "INSULTS",
                "inputStrength": "HIGH",
                "outputStrength": "HIGH"
            },
            {
                "type": "MISCONDUCT",
                "inputStrength": "HIGH",
                "outputStrength": "HIGH"
            },
            {
                "type": "PROMPT_ATTACK",
                "inputStrength": "HIGH",
                "outputStrength": "NONE"
            }
        ]
    },
    contextualGroundingPolicyConfig={
        'filtersConfig': [
            {
                "type": "GROUNDING",
                "threshold": 0.7
            },
            {
                "type": "RELEVANCE",
                "threshold": 0.7
            }
        ]
    },
    blockedInputMessaging = "Sorry, the model cannot answer this question.",
    blockedOutputsMessaging = "Sorry, the model cannot answer this question."
)

guardrailId = create_guardrail_response['guardrailId']
guardrailArn = create_guardrail_response['guardrailArn']

bedrock = boto3.client(service_name='bedrock', region_name='us-west-2')

create_guardrail_version_response = bedrock.create_guardrail_version(
    guardrailIdentifier=guardrailId
)

guardrailVersion = create_guardrail_version_response['version']
agentDetails = bedrock_agent.get_agent(agentId=agentId)

bedrock_agent.update_agent(
    agentId=agentId,
    agentName=agentDetails['agent']['agentName'],
    agentResourceRoleArn=agentDetails['agent']['agentResourceRoleArn'],
    instruction=agentDetails['agent']['instruction'],
    foundationModel=agentDetails['agent']['foundationModel'],
    guardrailConfiguration={
        'guardrailIdentifier': guardrailId,
        'guardrailVersion': guardrailVersion
    }

)

prepare_agent_and_check_status(bedrockAgent=bedrock_agent, agentId=agentId)
update_agent_alias_and_check_status(bedrockAgent=bedrock_agent, agentId=agentId, agentAliasId=agentAliasId)

sessionId = str(uuid.uuid4())
message="Thanks! What was my customer ID that you used"

invoke_agent_and_print(
    agentId=agentId,
    agentAliasId=agentAliasId,
    inputText=message,
    sessionId=sessionId,
    enableTrace=False
)
