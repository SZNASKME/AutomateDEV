import google.generativeai as genai
import asyncio

INPUT_TEXT = "What is SLA?"
API_KEY = "AIzaSyC-bDt5TonYSmKzKfxdGPnLn7pmdVGdxq4"
PROJECT_NAME = "275082005270"
MODEL = "gemini-1.5-flash"

async def getMessages(model: genai.GenerativeModel):
    response = await model.generate_content_async(INPUT_TEXT)
    return response

async def main():
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL)
    message = await getMessages(model)
    if message:
        message_text = message.text
    else:
        message_text = "Failed to get message"
    print(message_text)


if __name__ == "__main__":
    asyncio.run(main())
