#!/usr/bin/env python3
import requests
import re
import time

json_template = {
  #"locale": "th-TH"
}

message_template = {
  "type": "message",
  "from": {
    "id": "user1"
  },
  "text": "",
  #"locale": "th-TH"
}

def getToken():
    response = requests.get("${ops_copilot_token_url}", json = json_template)
    return response.json()["token"]

def getConversationId(auth):
    response = requests.post("${ops_copilot_base_message_url}", headers=auth, json = json_template)
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
    return "${ops_copilot_base_message_url}" + conversation_id + "/activities"

def trimMessage(message):
    return re.sub(r'\[\d+\]',"",message)

def main():
    token = getToken()
    auth = createAuthHeader(token)
    conversation_id = getConversationId(auth)
    message_url = updateMessageURL(conversation_id)
    answer = ""
    current_conversation_id = 0
    answer_conversation_id = 0
    message = """${ops_copilot_input_text}"""
    max_retry = int("${ops_copilot_max_retry}")
    retry_interval = int("${ops_copilot_retry_interval}")
    message_template["text"] = message
    response_message = sendMessage(message_url, auth, message)
    if response_message['id'].split('|')[0] == conversation_id:
        for _ in range(max_retry + 1):
            response_answer = getMessages(message_url, auth)
            for activity in response_answer["activities"]:
                current_conversation_id = int(activity["id"].split('|')[1])
                if ("type" in activity
                    and activity["type"] == "event"
                    and "value" in activity 
                    and "state" in activity["value"] 
                    and activity["value"]["state"] == "completed"
                    and current_conversation_id > answer_conversation_id
                    ):
                    answer_conversation_id = int(activity["id"].split('|')[1])
                    answer = activity["value"]["observation"]["search_result"]["Text"]["Content"]
                    break
                elif ("type" in activity
                    and activity["type"] == "message"
                    and "channelData" in activity
                    and "pva:gpt-feedback" in activity["channelData"]
                    and "completionState" in activity["channelData"]["pva:gpt-feedback"]
                    and activity["channelData"]["pva:gpt-feedback"]["completionState"] == "answered"
                    and current_conversation_id > answer_conversation_id
                    ):
                    answer_conversation_id = int(activity["id"].split('|')[1])
                    answer = activity["channelData"]["pva:gpt-feedback"]["summarizationOpenAIResponse"]["result"]["textSummary"]
                    break
            if answer:
                break
            time.sleep(retry_interval)
        if answer:
            trim_answer = trimMessage(answer)
            print(trim_answer)  
        else:
            exit(1)

if __name__ == "__main__":
    main()