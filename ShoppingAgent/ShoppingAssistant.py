#!/usr/bin/env python
# coding: utf-8

# In[33]:


# imports

import os
import json
import gradio as gr
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI
from io import BytesIO
from PIL import Image
from IPython.display import Audio, display


# In[34]:


# Initialization
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
MODEL = "gpt-4o-mini"
openai = OpenAI()


# In[35]:


# set our bot's persona
system_message = "You are a helpful assistant in a gem shop. "
system_message += "Give short, courteous answers, no more than 1 sentence. "
system_message += "Always be accurate. If you don't know the answer, say so."


# In[53]:


# Define the Art Request function
def artist(gem):
    image_response = openai.images.generate(
            model="dall-e-3",
            prompt=f"An image representing a {gem} gem or stone, in a complimentary setting and highlighting everything unique about it, in a vibrant style",
            size="1024x1024",
            n=1,
            response_format="b64_json",
        )
    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    return Image.open(BytesIO(image_data))



# In[37]:


gem_prices = {"amethyst": "$799", "tigers eye": "$199", "diamond": "$1400", "emerald": "$499"}

def get_gem_price(gem_name):
    print(f"Tool get_gem_price called for {gem_name}")
    gem = gem_name.lower()
    return gem_prices.get(gem, "Unknown")


# In[38]:


# Define the audio output function
def talker(message):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=message)

    audio_stream = BytesIO(response.content)
    output_filename = "output_audio.mp3"
    with open(output_filename, "wb") as f:
        f.write(audio_stream.read())

    # Play the generated audio
    display(Audio(output_filename, autoplay=True))


# In[39]:


# There's a particular dictionary structure that's required to describe our function:

price_function = {
    "name": "get_gem_price",
    "description": "Get the price of a gem based on the type provided. Call this whenever you need to know the gem price, for example when a customer asks 'How much is an amethyst?'",
    "parameters": {
        "type": "object",
        "properties": {
            "gem_name": {
                "type": "string",
                "description": "The gem the customer wants",
            },
        },
        "required": ["gem_name"],
        "additionalProperties": False
    }
}


# In[40]:


# And this is included in a list of tools:

tools = [{"type": "function", "function": price_function}]


# In[41]:


# Define our Chat function. Tuned for Gradio.

def chat(history):
    messages = [{"role": "system", "content": system_message}] + history
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    image = None
    
    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        response, gem = handle_tool_call(message)
        messages.append(message)
        messages.append(response)
        image = artist(gem)
        response = openai.chat.completions.create(model=MODEL, messages=messages)
        
    reply = response.choices[0].message.content
    history += [{"role":"assistant", "content":reply}]

    # Comment out or delete the next line if you'd rather skip Audio for now..
    talker(reply)
    
    return history, image


# In[42]:


# Function for calling tools:

def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    gem = arguments.get('gem_name')
    price = get_gem_price(gem)
    response = {
        "role": "tool",
        "content": json.dumps({"gem_name": gem,"price": price}),
        "tool_call_id": tool_call.id
    }
    return response, gem


# In[54]:


# Gradio Interface Setup
# Passing in inbrowser=True in the last line will cause a Gradio window to pop up immediately.
with gr.Blocks() as ui:
    with gr.Row():
        chatbot = gr.Chatbot(height=500, type="messages")
        image_output = gr.Image(height=500)
    with gr.Row():
        entry = gr.Textbox(label="Chat with our AI Assistant:")
    with gr.Row():
        clear = gr.Button("Clear")

    # Bind text input to the chatbot
    entry.submit(do_entry, inputs=[entry, chatbot], outputs=[entry, chatbot]).then(
        chat, inputs=chatbot, outputs=[chatbot, image_output]
    )
    clear.click(lambda: None, inputs=None, outputs=chatbot, queue=False)

ui.launch(inbrowser=True)


# In[ ]:




