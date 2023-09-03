import json
import os

import azure.identity
import openai
from flask import Blueprint, Response, current_app, render_template, request, stream_with_context

bp = Blueprint("chat", __name__, template_folder="templates", static_folder="static")

@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/chat")
def chat_handler():
    request_message = request.json["message"]

    @stream_with_context
    def response_stream():
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request_message},
            ],
            stream=True,
        )
        for event in response:
            current_app.logger.info(event)
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return Response(response_stream())
