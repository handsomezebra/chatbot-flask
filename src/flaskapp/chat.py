import json
import os
import time
import datetime

import openai
from flask import Blueprint, Response, current_app, render_template, request, stream_with_context

from .search import search_news, search_text

bp = Blueprint("chat", __name__, template_folder="templates", static_folder="static")

@bp.get("/")
def index():
    return render_template("index.html")

prompt_template = """You are a helpful assistant. Current time is {datetime}. I will give you a list of articles with title and text. Please answer questions.

Articles:
{context}

Answer:
"""

@bp.post("/chat")
def chat_handler():
    request_message = request.json["message"]

    @stream_with_context
    def response_stream():
        text_list = []

        news_result_list = []  # search_news(request_message)
        time.sleep(1)
        web_result_list = search_text(request_message)
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
                {"role": "user", "content": request_message},
            ],
            stream=True,
        )
        for event in response:
            #current_app.logger.info(event)
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return Response(response_stream())
