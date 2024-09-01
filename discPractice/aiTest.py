import os
import requests
from dotenv import find_dotenv, load_dotenv
from huggingface_hub import InferenceClient

# get api token from .env file
load_dotenv(find_dotenv(), override=True)
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")


# uses a text2speech moddel from huggingface to generate speech from text
def text2speech(message):
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}

    payloads = {"inputs": message}
    response = requests.post(API_URL, headers=headers, json=payloads)
    
    with open ('audio.flac', 'wb') as file:
        file.write(response.content)


# gives an answer based off of context, could be used to answer questions about who said what in a discord chat
def askQnA(payload):
    API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return (response.json()['answer'])
'''output = askQnA({
	"inputs": {
    "question": "What is my name?",
	"context": "My name is Clara and I live in Berkeley."
    }
})
print(output)
'''


# uses meta Llama ai to answer questions like a chatbot
def ask_chatAI(message):
    client = InferenceClient(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    token=HUGGINGFACEHUB_API_TOKEN,
    )
    answer =""
    for message in client.chat_completion(messages=[{"role": "user", "content": message}], max_tokens=250,stream=True): 
        answer+=message.choices[0].delta.content
    return answer


st = "hellothisisworld"
print(st.index("this"))
