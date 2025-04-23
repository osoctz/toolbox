"""
This is a simple chat demo using CogVLM2 model in ChainLit.
"""
import dataclasses
from typing import List
from PIL import Image
import chainlit as cl
from chainlit.input_widget import Slider,Select
import base64
from io import BytesIO
import requests
import json
# chainlit run webui.py --port 8002 --host 0.0.0.0
base_url = "http://127.0.0.1:9000"
base = {"Qwen2.5-VL-72B-Instruct":"http://127.0.0.1:9001","Qwen2.5-72B-Instruct":"http://127.0.0.1:9001"}


@cl.on_chat_start
def on_chat_start():
    print("Welcome use Qwen chat")


async def get_response_from_api(query, history, gen_kwargs, images=None):
    messages = []
    if images is None:
        if len(history) == 0:
            messages.append({"role": "user", "content": query})
        else:
            messages.append({"role": "user", "content": query})
    else:
        img = image_to_base64(images[0])
        img_url = f"data:image/jpeg;base64,{img}"

        if len(history) == 0:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url
                        },
                    },
                ],
            })
        else:
            for h in history:
                messages.append({"role": "user", "content": h[0]})
                messages.append({"role": "assistant", "content": h[1]})

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url
                        },
                    },
                ],
            })

    # print(f"messages: {messages}")
    
    data = {
        "model": gen_kwargs['model_name'],
        "messages": messages,
        "stream": True,
        "max_tokens": 2048,
        "temperature": gen_kwargs['temperature'],
        "top_p": gen_kwargs['top_p'],
    }

    base_url = base[gen_kwargs['model_name']]
    print(base_url)
    response = requests.post(f"{base_url}/v1/chat/completions", json=data, stream=True)
    if response.status_code == 200:
        # 处理流式响应
        for line in response.iter_lines():
            #print(f"line: {line}")
            if line:
                decoded_line = line.decode('utf-8')[6:]
                try:
                    response_json = json.loads(decoded_line)
                    content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    yield content
                except:
                    print("Special Token:", decoded_line)
    else:
        print("Error:", response.status_code)


def image_to_base64(image):
    # image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    output_buffer = BytesIO()
    image.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode("utf-8")
    return base64_str


@dataclasses.dataclass
class Conversation:
    """A class that keeps all conversation history."""
    roles: List[str]
    messages: List[List[str]]
    version: str = "Unknown"

    def append_message(self, role, message):
        self.messages.append([role, message])

    def get_prompt(self):
        if not self.messages:
            return None, []

        last_role, last_msg = self.messages[-2]
        if isinstance(last_msg, tuple):
            query, _ = last_msg
        else:
            query = last_msg

        history = []
        for role, msg in self.messages[:-2]:
            if isinstance(msg, tuple):
                text, _ = msg
            else:
                text = msg

            if role == "USER":
                history.append((text, ""))
            else:
                if history:
                    history[-1] = (history[-1][0], text)

        return query, history

    def get_images(self):
        for role, msg in reversed(self.messages):
            if isinstance(msg, tuple):
                msg, image = msg
                if image is None:
                    continue
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                # width, height = image.size
                # if width > 1344 or height > 1344:
                #     max_len = 1344
                #     aspect_ratio = width / height
                #     if width > height:
                #         new_width = max_len
                #         new_height = int(new_width / aspect_ratio)
                #     else:
                #         new_height = max_len
                #         new_width = int(new_height * aspect_ratio)
                #     image = image.resize((new_width, new_height))
                return [image]
        return None

    def copy(self):
        return Conversation(
            roles=self.roles,
            messages=[[x, y] for x, y in self.messages],
            version=self.version,
        )

    def dict(self):
        if len(self.get_images()) > 0:
            return {
                "roles": self.roles,
                "messages": [
                    [x, y[0] if type(y) is tuple else y] for x, y in self.messages
                ],
            }
        return {
            "roles": self.roles,
            "messages": self.messages,
        }


default_conversation = Conversation(
    roles=("USER", "ASSISTANT"),
    messages=()
)


async def request(conversation: Conversation, settings):
    gen_kwargs = {
        "temperature": settings["temperature"],
        "top_p": settings["top_p"],
        "max_new_tokens": int(settings["max_token"]),
        "top_k": int(settings["top_k"]),
        "do_sample": True,
        "model_name": settings["Model"]
    }
    query, history = conversation.get_prompt()
    images = conversation.get_images()

    chainlit_message = cl.Message(content="", author="CogVLM2")
    text = ""
    async for response in get_response_from_api(query, history, gen_kwargs, images):
        text += response
        conversation.messages[-1][-1] = text
        await chainlit_message.stream_token(text, is_sequence=True)

    await chainlit_message.send()
    return conversation


@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Slider(id="temperature", label="Temperature", initial=0.5, min=0.01, max=1, step=0.05),
            Slider(id="top_p", label="Top P", initial=0.7, min=0, max=1, step=0.1),
            Slider(id="top_k", label="Top K", initial=5, min=0, max=50, step=1),
            Slider(id="max_token", label="Max output tokens", initial=2048, min=0, max=8192, step=1),
            Select(
                id="Model",
                label="Model",
                values=["Qwen2.5-VL-72B-Instruct", "Qwen2.5-72B-Instruct"],
                initial_index=0,
            ),
        ]
    ).send()

    conversation = default_conversation.copy()
    cl.user_session.set("conversation", conversation)
    cl.user_session.set("settings", settings)


@cl.on_settings_update
async def setup_agent(settings):
    cl.user_session.set("settings", settings)


@cl.on_message
async def main(message: cl.Message):
    image = next(
        (
            Image.open(file.path)
            for file in message.elements or []
            if "image" in file.mime and file.path is not None
        ),
        None,
    )

    conv = cl.user_session.get("conversation")  # type: Conversation
    settings = cl.user_session.get("settings")

    text = message.content

    conv_message = (text, image)
    conv.append_message(conv.roles[0], conv_message)
    conv.append_message(conv.roles[1], None)

    conv = await request(conv, settings)
    cl.user_session.set("conversation", conv)
