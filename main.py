from datetime import datetime, timedelta
import hashlib
import io
import json
from flask import Flask, Response, render_template, request
import requests, re
import dotenv
import os
from openai import OpenAI
import openai
from pydantic import BaseModel
import humanize
import git
from markupsafe import Markup
from thefuzz import fuzz
from PIL import Image, ImageDraw, ImageFont

repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha[:7]
full_sha = repo.head.object.hexsha

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


DAILY_AI_LIMIT = os.getenv(
    "DAILY_AI_LIMIT", 100
)  # This value is much lower on the server

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)  # create a .env file and set OPENAI_API_KEY to '' if it's causing errors
client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)

if os.getenv("SENTRY_DSN"):
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
    )
app = Flask(__name__)

if __name__ == "__main__":
    from tools import tools_blueprint

    app.register_blueprint(tools_blueprint)


@app.context_processor
def utility_processor():
    to_return = {}
    to_return["sha"] = sha
    to_return["bulma"] = Markup(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">'
    )
    to_return["fontawesome"] = Markup(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />'
    )
    to_return["analytics"] = (
        Markup(
            '<script defer src="https://st.editid.uk/script.js" data-website-id="072a1296-3bf0-4db8-a5b0-e538f2e772bb"></script>'
        )
        if os.getenv("IS_PRODUCTION")
        else ""
    )
    return to_return


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


our_tools = [
    {
        "name": "AI Color Palette Generator",
        "url": "/ai_color_palette",
        "description": "Generate a color palette based on a description.",
    },
    {
        "name": "Base64 to Image",
        "url": "/base_64_to_image",
        "description": "Convert a base64 image to a file.",
    },
    {
        "name": "Diff Editor",
        "url": "/diff_editor",
        "description": "Generate a diff between two files.",
    },
    {
        "name": "Foreground Color Helper",
        "url": "/foreground_helper",
        "description": "Generate accessible foreground colors for a given background color.",
    },
    {
        "name": "Background Color Helper",
        "url": "/background_helper",
        "description": "Generate accessible background colors for a given foreground color.",
    },
    {
        "name": "Hex to HSL",
        "url": "/hex_to_hsl",
        "description": "Convert a hex color to HSL and vice versa.",
    },
    {
        "name": "Hex to RGB",
        "url": "/hex_to_rgb",
        "description": "Convert a hex color to RGB and vice versa.",
    },
    {
        "name": "Image to Color Palette",
        "url": "/image_to_palette",
        "description": "Generate a color palette from an image.",
    },
    {
        "name": "Image to Base64",
        "url": "/image_to_base64",
        "description": "Convert an image to base64.",
    },
    {
        "name": "JSON Editor",
        "url": "/json_editor",
        "description": "Edit and format JSON.",
    },
    {
        "name": "JSON to YAML",
        "url": "/json_to_yaml",
        "description": "Convert JSON to YAML and vice versa.",
    },
    {
        "name": "Markdown editor",
        "url": "/markdown_editor",
        "description": "Edit, format and view Markdown.",
    },
    {
        "name": "Meta Tag Generator",
        "url": "/meta_tag_generator",
        "description": "Generate meta tags for your website.",
    },
    {
        "name": "Color Palette Generator",
        "url": "/palette_generator",
        "description": "Generate a color palette.",
    },
    {
        "name": "QR Code Generator",
        "url": "/qr_code_generator",
        "description": "Generate a QR code.",
    },
    {
        "name": "AI Regex Generator",
        "url": "/regex_generator",
        "description": "Generate a regex using a description.",
    },
    {
        "name": "SVG to Image",
        "url": "/svg_to_image",
        "description": "Convert a SVG image to a PNG, WebP, or JPG.",
    },
    {
        "name": "Timestamp Converter",
        "url": "/timestamp_converter",
        "description": "Convert a timestamp to a readable format.",
    },
    {
        "name": "UUID Generator",
        "url": "/uuid_generator",
        "description": "Generate a V1, V3, V4 or V5 UUID.",
    },
    {
        "name": "Password Generator",
        "url": "/password_generator",
        "description": "Generate a password.",
    },
    {
        "name": "Socket.IO Tester",
        "url": "/socketio",
        "description": "Test Socket.IO connections.",
    },
    {
        "name": "Clipboard to Image",
        "url": "/clipboard_to_image",
        "description": "Save an image from your clipboard.",
    },
    {
        "name": "Lorem Ipsum Generator",
        "url": "/lorem_ipsum_generator",
        "description": "Generate Lorem Ipsum text.",
    },
    {
        "name": "URL Encoder/Decoder",
        "url": "/url_encode_decode",
        "description": "Encode and decode strings using URL encoding.",
    },
    {
        "name": "Hash Generator",
        "url": "/hash_generator",
        "description": "Generate a hash for a string",
    },
]


@app.route("/")
def index():
    return render_template("index.html", tools=our_tools, hash=sha, full_sha=full_sha)


def extract_hex_codes(text):
    # Regular expression pattern for hex color codes
    pattern = r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b"
    # Find all matches in the text
    return re.findall(pattern, text)


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route("/color/<foreground>/<background>")
def color_generator(foreground, background):
    if len(foreground) not in [4, 7] or len(background) not in [4, 7]:
        return {"reason": "Invalid color", "choices": []}
    im = Image.new("RGB", (400, 100), background)
    d = ImageDraw.Draw(im)
    d.text((0, 0), foreground, fill=foreground, font=ImageFont.load_default(size=70))
    b = io.BytesIO()
    im.save(b, "PNG")
    return Response(b.getvalue(), mimetype="image/png")


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
    # check if the count is greater than DAILY_AI_LIMIT
    if data[today_string][ip_hash] > DAILY_AI_LIMIT:
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
        remaining = DAILY_AI_LIMIT - data[today_string][ip_hash]
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
            store=True,
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


class RegexAI(BaseModel):
    regexs: list[str]
    test_cases: list[str]


def match_regex(regex: str, test_case: str) -> bool:
    return bool(re.match(regex, test_case))


tools = [
    {
        "type": "function",
        "function": {
            "name": "match_regex",
            "description": "Matches a regex against a test case.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "regex": {
                        "type": "string",
                        "description": "The regex to match.",
                    },
                    "test_case": {
                        "type": "string",
                        "description": "The test case to match the regex against.",
                    },
                },
                "required": ["regex", "test_case"],
                "additionalProperties": False,
            },
        },
    }
]


@app.route("/regexai", methods=["POST"])
def regexai():
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
    # check if the count is greater than DAILY_AI_LIMIT
    if data[today_string][ip_hash] > DAILY_AI_LIMIT:
        # create variable resets that is time until midnight of the next day
        resets = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.now()
        # convert to human readable format using humanize
        resets = humanize.naturaldelta(resets, minimum_unit="seconds")
        return {
            "message": f"You have exceeded the limit of {DAILY_AI_LIMIT} requests per day. Please try again in {resets}.",
            "remaining": 0,
        }
    else:
        remaining = DAILY_AI_LIMIT - data[today_string][ip_hash]
    data = request.get_json()
    regex_query = data["regex"]
    try:
        messages = [
            {
                "role": "system",
                "content": "You are an AI designed to help generate regular expressions, and test cases that help check if the regex is valid. Refuse innapropriate requests. Make sure that at least 2 of the test cases match the regex, and at least 1 of the test cases do not match the regex. Use the tools provided to validate the regex.",
            },
            {
                "role": "user",
                "content": f"Generate a regular expression that matches: {regex_query}",
            },
        ]
        chat_completion = client.beta.chat.completions.parse(
            messages=messages,
            model="gpt-4o-mini",
            response_format=RegexAI,
            store=True,
            tools=tools,
            # max_completion_tokens=600,
        )
        tool_calls = chat_completion.choices[0].message.tool_calls
        if tool_calls:
            messages.append(chat_completion.choices[0].message)
            print(f"Used {len(tool_calls)} tools")
            for tool_call in tool_calls:
                function_id = tool_call.id
                args = json.loads(tool_call.function.arguments)
                regex_ = args["regex"]
                test_case = args["test_case"]
                result_ = match_regex(regex_, test_case)
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(
                            {
                                "result": result_,
                            }
                        ),
                        "tool_call_id": function_id,
                    }
                )
            chat_completion = client.beta.chat.completions.parse(
                messages=messages,
                model="gpt-4o-mini",
                response_format=RegexAI,
                store=True,
                tools=tools,
                # max_completion_tokens=600,
            )
            tool_calls2 = chat_completion.choices[0].message.tool_calls
            if tool_calls2:
                messages.append(chat_completion.choices[0].message)
                print(f"Used {len(tool_calls)} tools")
                for tool_call in tool_calls:
                    function_id = tool_call.id
                    args = json.loads(tool_call.function.arguments)
                    regex_ = args["regex"]
                    test_case = args["test_case"]
                    result_ = match_regex(regex_, test_case)
                    messages.append(
                        {
                            "role": "tool",
                            "content": json.dumps(
                                {
                                    "result": result_,
                                }
                            ),
                            "tool_call_id": function_id,
                        }
                    )
                chat_completion = client.beta.chat.completions.parse(
                    messages=messages,
                    model="gpt-4o-mini",
                    response_format=RegexAI,
                    store=True,
                    # max_completion_tokens=600,
                )
            else:
                tool_calls2 = None
        response = chat_completion.choices[0].message
        res = response.parsed
        # print(str(chat_completion.usage.total_tokens) + ' tokens used')
        if response.refusal:
            return {
                "regex": [],
                "test_cases": [],
                "message": res.refusal,
            }
        return {
            "regex": res.regexs,
            "test_cases": res.test_cases,
            "message": "",
            "tool": True if tool_calls else False,
            "tool2": True if tool_calls2 else False,
            "remaining": remaining,
        }
    except openai.LengthFinishReasonError:
        print("Error: LengthFinishReasonError")
        return {
            "regex": [],
            "test_cases": [],
            "message": "Too many attempts. Please try again.",
        }
    except Exception as e:
        # raise e
        return {
            "regex": [],
            "test_cases": [],
            "message": "Something went wrong. Please try again.",
        }


@app.route("/about")
def about():
    return render_template("about.html")


class ColorPalette(BaseModel):
    colors: list[str]


@app.route("/aipalette", methods=["POST"])
def aipalette():
    data = request.get_json()
    theme = data.get("theme", "")
    theme = theme[:100]
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
    # check if the count is greater than DAILY_AI_LIMIT
    if data[today_string][ip_hash] > DAILY_AI_LIMIT:
        # create variable resets that is time until midnight of the next day
        resets = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.now()
        # convert to human readable format using humanize
        resets = humanize.naturaldelta(resets, minimum_unit="seconds")
        return {
            "message": f"You have exceeded the limit of {DAILY_AI_LIMIT} requests per day. Please try again in {resets}.",
            "remaining": 0,
        }
    else:
        remaining = DAILY_AI_LIMIT - data[today_string][ip_hash]
    messages = [
        {
            "role": "system",
            "content": "You are a color palette generator. You must return a list of 5 colors formatted in hex format, include the hashtag at the start of each one. If you are unable to return a list of 5 colors, make any unavailable colors #000000. Try to create a color palette based on the specified theme, or if theme is random then pick a random complementary color palette.",
        }
    ]
    if theme:
        messages.append(
            {
                "role": "system",
                "content": "Theme: " + theme,
            }
        )
    else:
        messages.append(
            {
                "role": "user",
                "content": "Theme: Random",
            }
        )
    response = client.beta.chat.completions.parse(
        messages=messages,
        model="gpt-4o-mini",
        response_format=ColorPalette,
        store=True,
    )
    response = response.choices[0].message
    if response.refusal:
        return {
            "reason": "Too many attempts. Please try again.",
            "choices": ["#000000"],
        }
    res = json.loads(response.content)
    colors = [c.upper().strip() for c in res["colors"]]
    return {
        "colors": colors,
        "remaining": remaining,
    }


class PaletteGen2(BaseModel):
    colors: list[str]


def aiv2_backend(prompt, ip_hash) -> tuple[list[str], bool]:
    possible = [
        "coventry college",
        "coventry",
        "cov col",
        "cov college",
        "cov",
        "cov coll",
        "coventry col",
        "coventry coll",
        "city college",
        "cov city college",
    ]
    if any(fuzz.ratio(prompt.lower(), p) > 80 for p in possible):
        return ["#0070ba", "#009fe3", "#81ba25", "#cad400"], True
    # Moderate first:
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=[{"type": "text", "text": prompt}],
    )
    if response.results[0].flagged:
        return [], False
    messages = [
        {
            "role": "system",
            "content": "Generate a color palette with the exact number of HEX values (between 1 and 8) that best fits the given theme or description. Choose colors that complement each other and reflect the mood, style, or purpose described. Only return the amount of colors needed, and make sure they are in HEX format, no matter what, include the # at the start. As an example, google would return 4 colors, youtube would return 3 colors, and facebook would return 1 color.",
        },
        {
            "role": "user",
            "content": f"Theme: {prompt}",
        },
    ]
    response = client.beta.chat.completions.parse(
        messages=messages,
        model="gpt-4o-mini",
        response_format=PaletteGen2,
        store=True,
        metadata={"ip_hash": ip_hash},
    )
    response = response.choices[0].message
    res = response.parsed.colors
    return res, True


@app.route("/aiv2back", methods=["POST"])
def aiv2back():
    post_data = request.get_json()
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
    # check if the count is greater than DAILY_AI_LIMIT
    if data[today_string][ip_hash] > DAILY_AI_LIMIT:
        # create variable resets that is time until midnight of the next day
        resets = (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.now()
        # convert to human readable format using humanize
        resets = humanize.naturaldelta(resets, minimum_unit="seconds")
        print("failsafe")
        return {
            "message": f"You have exceeded the limit of {DAILY_AI_LIMIT} requests per day. Please try again in {resets}.",
            "remaining": 0,
        }
    else:
        remaining = DAILY_AI_LIMIT - data[today_string][ip_hash]
    if not post_data.get("theme"):
        post_data["theme"] = "random"
    if len(post_data.get("theme")) > 100:
        return {"colors": ["#ff0000"], "acceptable": False, "remaining": remaining}
    color_array, acceptable = aiv2_backend(post_data.get("theme"), str(ip_hash))
    if not acceptable:
        return {"colors": ["#ff0000"], "acceptable": False, "remaining": remaining}
    return {"colors": color_array, "acceptable": True, "remaining": remaining}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5738)
