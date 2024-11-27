
import requests
import re
import time

ops_copilot_token_url = "https://defaulte1c0d62271bd42f6ba07ab2b2645df.6c.environment.api.powerplatform.com/powervirtualagents/botsbyschema/cr68d_agentTest/directline/token?api-version=2022-03-01-preview"
ops_copilot_conversation_id_url = "https://directline.botframework.com/v3/directline/conversations/"
ops_copilot_base_message_url = "https://directline.botframework.com/v3/directline/conversations/"
ops_copilot_input_text = "What is stonebrance?"
ops_copilot_maximum_retry = 3
ops_copilot_retry_interval = 10



json_template = {
  "locale": "th-TH"
}

message_template = {
  "type": "message",
  "from": {
    "id": "user1"
  },
  "text": "",
  "locale": "th-TH"
}

def get_token():
    response = requests.get(ops_copilot_token_url, json = json_template)
    return response.json()["token"]

def getConversationId(auth):
    response = requests.post(ops_copilot_conversation_id_url, headers=auth, json = json_template)
    return response.json()["conversationId"]

def sendMessage(message_url, auth, message):
    message_template["text"] = message
    response = requests.post(message_url, headers = auth, json = message_template)
    return response.json()


def getMessages(message_url, auth):
    response = requests.get(message_url, headers = auth, json = json_template)
    return response.json()

def createAuthHeader(token):
    return {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json"}

def updateMessageURL(conversation_id):
    return ops_copilot_base_message_url + conversation_id + "/activities"

def trimMessage(message):
    return re.sub(r'\[\d+\]',"",message)

def findValueBfs(data, target_key):
    queue = [data]
    while queue:
        current = queue.pop(0)
        if isinstance(current, dict):
            for key, value in current.items():
                if key == target_key:
                    return value
                if isinstance(value, (dict, list)):
                    queue.append(value)
        elif isinstance(current, list):
            queue.extend(current)
    return None

def main():
    token = get_token()
    auth = createAuthHeader(token)
    conversation_id = getConversationId(auth)
    message_url = updateMessageURL(conversation_id)
    answer = None
    current_conversation_id = 0
    answer_conversation_id = 0
    message = ops_copilot_input_text
    message_template["text"] = message
    response_message = sendMessage(message_url, auth, message)
    if response_message['id'].split('|')[0] == conversation_id:
        for _ in range(ops_copilot_maximum_retry):
            response_answer = getMessages(message_url, auth)
            for activity in response_answer["activities"]:
                current_conversation_id = int(activity["id"].split('|')[1])
                if ("value" in activity 
                    and "state" in activity["value"] 
                    and activity["value"]["state"] == "completed"
                    and current_conversation_id > answer_conversation_id
                    ):
                    answer_conversation_id = int(activity["id"].split('|')[1])
                    answer = activity["value"]["observation"]["search_result"]["Text"]["Content"]
                    break
            if answer:
                break
            time.sleep(ops_copilot_retry_interval)
            
            
    trim_answer = trimMessage(answer)
    print(trim_answer)

if __name__ == "__main__":
    main()