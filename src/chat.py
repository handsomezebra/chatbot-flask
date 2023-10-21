import json
import os
import time
import datetime

import openai

from search import search_news, search_text


prompt_template = """You are a helpful assistant. Current time is {datetime}. I will give you a list of articles with title and text. Please answer questions.

Articles:
{context}

Answer:
"""

def call_chat_api(question):
    text_list = []

    news_result_list = search_news(question)
    time.sleep(1)
    web_result_list = search_text(question)
    time.sleep(1)

    for result in news_result_list + web_result_list:
        text = result["title"] + "\n" + result["body"]
        text_list.append(text)

    full_text = "\n\n".join(text_list)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": prompt_template.format(datetime=now, context=full_text)},
            {"role": "user", "content": question},
        ],
        stream=True,
    )

    for event in response:
        yield event
