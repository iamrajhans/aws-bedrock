import boto3
import uuid
from helper import (
    create_bedrock_agent, wait_for_agent_status,
    prepare_agent_and_check_status,wait_for_agent_alias_status
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

bedrock_agent_runtime = boto3.client(service_name='bedrock-agent-runtime', region_name='us-west-2')
message = "Hello, I bought a mug from your store yesterday, and it broke. I want to return it."

sessionId = str(uuid.uuid4())

invoke_agent_response = bedrock_agent_runtime.invoke_agent(
    agentId=agentId,
    agentAliasId=agentAliasId,
    inputText=message,
    sessionId=sessionId,
    endSession=False,
    enableTrace=True,
)
event_stream = invoke_agent_response["completion"]
for event in event_stream:
    print(event)
