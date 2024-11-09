from datetime import datetime, timedelta
import hashlib
import json
from flask import Flask, render_template, request
import requests, re
import dotenv
import os
from openai import OpenAI
import openai
from pydantic import BaseModel
import humanize

# check if .env file exists
if not os.path.exists(".env"):
    # create .env file
    print("Creating .env file...")
    with open(".env", "w") as f:
        f.write("")

    # add OPENAI_API_KEY to .env file
    with open(".env", "a") as f:
        f.write("OPENAI_API_KEY=''")

# check if data.json exists
if not os.path.exists("data.json"):
    # create data.json file
    print("Creating data.json file...")
    with open("data.json", "w") as f:
        f.write("{}")

dotenv.load_dotenv()


# Used for OpenAI
class Color(BaseModel):
    reason: str
    choices: list[str]


# SnipSpace?

app = Flask(__name__)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)  # create a .env file and set OPENAI_API_KEY to '' if it's causing errors
client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)

tools = [
    {
        "name": "Hex to RGB",
        "description": "Converts hex color codes to RGB values.",
        "link": "/hex2rgb",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/haskell/haskell-original.svg",
    },
    {
        "name": "RGB to Hex",
        "description": "Converts RGB values to hex color codes.",
        "link": "/rgb2hex",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/haskell/haskell-original.svg",
    },
    {
        "name": "JSON Editor",
        "description": "Edit JSON data with a drag-and-drop interface.",
        "link": "/jsoneditor",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/json/json-original.svg",
    },
    {
        "name": "Markdown Editor",
        "description": "Edit and preview markdown content.",
        "link": "/markdowneditor",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/markdown/markdown-original.svg",
    },
    {
        "name": "Meta Tag Generator",
        "description": "Generate meta tags for your web pages.",
        "link": "/metatags",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg",
    },
    {
        "name": "Image to Base64",
        "description": "Convert an image to base64 encoded data.",
        "link": "/image2base64",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg",
    },
    {
        "name": "Base64 to Image",
        "description": "Convert base64 encoded data to an image.",
        "link": "/base642image",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg",
    },
    {
        "name": "Hex to HSL",
        "description": "Converts hex color codes to HSL values.",
        "link": "/hex2hsl",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/haskell/haskell-original.svg",
    },
    {
        "name": "HSL to Hex",
        "description": "Converts HSL values to hex color codes.",
        "link": "/hsl2hex",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/haskell/haskell-original.svg",
    },
    {
        "name": "Diff Editor",
        "description": "Generate a diff file between two text files.",
        "link": "/diffeditor",
        "image": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg",
    },
]


@app.route("/")
def index():
    return render_template("index.html", tools=tools)


@app.route("/hex2rgb")
@app.route("/rgb2hex")
def hex2rgb():
    return render_template("hex2rgb.html", path=request.path)


@app.route("/foreground")
@app.route("/background")
def foreground():
    return render_template("foreground.html", path=request.path)


@app.route("/image2base64")
def image2base64():
    return render_template("image2base64.html")


def extract_hex_codes(text):
    # Regular expression pattern for hex color codes
    pattern = r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b"
    # Find all matches in the text
    return re.findall(pattern, text)


@app.route("/color", methods=["POST", "GET"])
def colorai():
    color = request.json.get("color")
    fgbg = request.json.get("fgbg")
    if fgbg.lower() not in ["foreground", "background"]:
        return {"reason": "Invalid fgbg", "choices": []}
    if len(color) != 7 or color[0] != "#":
        return {"reason": "Invalid color", "choices": []}
    print(f"color: {color}, fgbg: {fgbg}")
    # print the user's ip if CF-Connecting-IP isn't set
    if "CF-Connecting-IP" not in request.headers:
        ip = request.remote_addr
    else:
        ip = request.headers["CF-Connecting-IP"]
    # hash the ip
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()
    # check if the ip has been seen before in data.json
    with open("data.json", "r") as f:
        data = json.load(f)
    today_string = datetime.now().strftime("%d-%m-%Y")
    if today_string not in data:
        data[today_string] = {}
    if ip_hash in data[today_string]:
        data[today_string][ip_hash] += 1
    else:
        data[today_string][ip_hash] = 1
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
    # check if the count is greater than 10
    if data[today_string][ip_hash] > 10:
        # create variable resets that is time until midnight of the next day
        resets = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.now()
        # convert to human readable format using humanize
        resets = humanize.naturaldelta(resets, minimum_unit="seconds")
        return {
            "reason": f"You have exceeded the maximum number of attempts for today, your limit resets in {resets}.",
            "choices": ["#000000"],
            "remaining": 0,
        }
    else:
        remaining = 10 - data[today_string][ip_hash]
    # return {'reason': 'Color not found', 'choices': []}
    # local AI
    # req = requests.get(f'http://192.168.7.254:57372?color={color}&fgbg={fgbg}')
    # return req.json()
    # openAI
    try:
        chat_completion = client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI designed to help pick out complementary colors that are accessible to users, depending on whether you are provided with a foreground (text) color, or a background color you will provide with a suitable choice for the other one, and provide a short sentence explaining why it's the ideal choice, as well as other possible choices if there are any. Output a reason and a list of colors in hex format only. Do not provide any RGB values, do not provide color names.",
                },
                {
                    "role": "user",
                    "content": f"{fgbg} color is {color}",
                },
            ],
            model="gpt-4o-mini",
            response_format=Color,
        )
        response = chat_completion.choices[0].message
        if response.refusal:
            return {
                "reason": "Too many attempts. Please try again.",
                "choices": ["#000000"],
            }
        res = json.loads(response.content)
        choices = [c.upper().strip() for c in res["choices"]]
        print(choices)
        return {"reason": res["reason"], "choices": choices, "remaining": remaining}
    except Exception as e:
        if type(e) == openai.LengthFinishReasonError:
            return {
                "reason": "Too many attempts. Please try again.",
                "choices": ["#000000"],
            }
        else:
            return {
                "reason": "Something went wrong. Please try again.",
                "choices": ["#000000"],
            }
    # res = chat_completion.choices[0].message.content
    # colors = extract_hex_codes(res)
    # colors = [c for c in colors if c.upper() != color.upper()]
    # return {'reason': res, 'choices': colors}


@app.route("/assets/<filename>")
def serve_static(filename):
    return app.send_static_file(filename)


@app.route("/jsoneditor")
def jsoneditor():
    return render_template("json_editor.html")


@app.route("/markdowneditor")
def markdowneditor():
    return render_template("markdownEditor.html")


@app.route("/base642image")
def base642image():
    return render_template("base642image.html")


@app.route("/metatags")
def metatags():
    return render_template("metatags.html")


@app.route("/hex2hsl")
@app.route("/hsl2hex")
def hex2hsl():
    return render_template("hex2hsl.html")


@app.route("/diffeditor")
def diffeditor():
    return render_template("diffeditor.html")


@app.route("/like", methods=["POST"])
def like():
    data = request.get_json()
    print(data)  # do something with the data at some point
    return "OK"


@app.route("/dislike", methods=["POST"])
def dislike():
    data = request.get_json()
    print(data)  # do something with the data at some point
    return "OK"


# REMOVE BELOW IN PRODUCTION
# REMOVE BELOW IN PRODUCTION
# REMOVE BELOW IN PRODUCTION


@app.route("/template/<template_name>")
def template(template_name):
    return render_template(f"{template_name}.html")


# REMOVE ABOVE IN PRODUCTION
# REMOVE ABOVE IN PRODUCTION
# REMOVE ABOVE IN PRODUCTION

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5738)
