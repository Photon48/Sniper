import base64
import requests
from openai import OpenAI

import json
import streamlit as st
from prompts import prompt_template

#initalize dotenv API Key
from dotenv import load_dotenv
load_dotenv()
#Initalize Open AI
client = OpenAI()
api_key = st.secrets["OPENAI_API_KEY"]


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


# Function to run our LLM + Vision request
def llm_call(user_goal, base64_image, GRID_SIZE, ocr_strings):
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt_template(user_goal, GRID_SIZE, ocr_strings)
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}",
              "detail": "low"
            }
          }
        ]
      }
    ],
    "max_tokens": 800
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

  response_json = response.json()
  print(response_json['choices'][0]['message']['content'])

  try:
      json_data = json.loads(response_json['choices'][0]['message']['content'].replace('\n', '').replace("```","").replace("json",""))
  except json.JSONDecodeError:
      print("The response could not be parsed as JSON.")
 
  return json_data[0]['best_option']
