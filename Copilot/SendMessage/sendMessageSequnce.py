import requests
import aiohttp
import asyncio
import json
import time

CONVERSATION_ID = ""
GET_TOKEN_URL = "https://defaulte1c0d62271bd42f6ba07ab2b2645df.6c.environment.api.powerplatform.com/powervirtualagents/botsbyschema/cr68d_agentTest/directline/token?api-version=2022-03-01-preview"
GET_CONVERSATION_ID_URL = "https://directline.botframework.com/v3/directline/conversations/"
BASE_MESSAGE_URL = "https://directline.botframework.com/v3/directline/conversations/"



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
    response = requests.get(GET_TOKEN_URL, json = json_template)
    return response.json()["token"]

def getConversationId(auth):
    response = requests.post(GET_CONVERSATION_ID_URL, headers=auth, json = json_template)
    return response.json()["conversationId"]

async def sendMessage(message_url, auth, message):
    message_template["text"] = message
    async with aiohttp.ClientSession() as session:
        async with session.post(message_url, headers = auth, json = message_template) as response:
            return await response.json()

async def getMessages(message_url, auth):
    async with aiohttp.ClientSession() as session:
        async with session.get(message_url, headers = auth, json = json_template) as response:
            return await response.json()

############################################################################################################

def createAuthHeader(token):
    return {"Authorization": f"Bearer {token}",
            "Content-Type": "application/json"}

def updateMessageURL(conversation_id):
    return BASE_MESSAGE_URL + conversation_id + "/activities"





async def main():
    token = get_token()
    auth = createAuthHeader(token)
    conversation_id = getConversationId(auth)
    CONVERSATION_ID = conversation_id
    print("Conversation ID: ", CONVERSATION_ID)
    message_url = updateMessageURL(conversation_id)
    print("Message URL: ", message_url)
    answer = ""
    current_conversation_id = 0
    answer_conversation_id = 0
    while True:
        message = input("Enter message: ")
        if message == "exit":
            break
        message_template["text"] = message
        start_time = time.time()
        response_message = await sendMessage(message_url, auth, message)
        print(response_message)
        if response_message['id'].split('|')[0] == conversation_id:
            print("Message sent successfully")
            getting_answer = True
            while getting_answer:
                response_answer = await getMessages(message_url, auth)
                for activity in response_answer["activities"]:
                    current_conversation_id = int(activity["id"].split('|')[1])
                    if ("value" in activity 
                        and "state" in activity["value"] 
                        and activity["value"]["state"] == "completed"
                        and current_conversation_id > answer_conversation_id
                        ):
                        answer_conversation_id = int(activity["id"].split('|')[1])
                        answer = activity["value"]["observation"]["search_result"]["Text"]["Content"]
                        getting_answer = False
                        end_time = time.time()
                        break
            print("Answer: ", answer)
            print("ID", current_conversation_id)
            print("Time: ", end_time - start_time)
            print("Get answer successfully")

if __name__ == "__main__":
    asyncio.run(main())
        
        