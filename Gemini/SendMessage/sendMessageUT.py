#!/usr/bin/env python3

import google.generativeai as genai
import asyncio

async def main():
    api_key = "${ops_gemini_api_key}"
    gemini_model = "${ops_gemini_model}"
    input_text = """${ops_gemini_input_text}"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(gemini_model)
    message = await model.generate_content_async(input_text)
    message_text = message.text
    print(message_text)
    
    
if __name__ == "__main__":
    asyncio.run(main())