if __name__ == "__main__":
    print("#" * 20)
    print("#" * 20)
    print("This file is not meant to be run directly.")
    print("#" * 20)
    print("#" * 20)
    print("Do not run this file.")
    print("#" * 20)
    print("#" * 20)
    exit()

from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from openai import OpenAI
from pydantic import BaseModel
from thefuzz import fuzz
from dotenv import load_dotenv
load_dotenv()
import os, hashlib, json, humanize, openai, re

ai_blueprint = Blueprint("ai", __name__)

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

# ------------------------------
# 
# Foreground/Background AI
# 
# ------------------------------

class Color(BaseModel):
    reason: str
    choices: list[str]

@ai_blueprint.route("/color", methods=["POST", "GET"])
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
    except openai.LengthFinishReasonError as e:
        return {
    except openai.OpenAIError as e:
        # Handle other OpenAI-specific errors
        return {
            "reason": f"OpenAI API error: {str(e)}",
            "choices": ["#000000"],
            "remaining": remaining
        }
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        return {
            "reason": "Invalid response format from AI",
            "choices": ["#000000"],
            "remaining": remaining
        }
                "reason": "Too many attempts. Please try again.",
                "choices": ["#000000"],
            }
        else:
            return {
                "reason": "Something went wrong. Please try again.",
                "choices": ["#000000"],
            }
        
# ------------------------------
# 
# Foreground/Background AI
# 
# ------------------------------

# ------------------------------
#
# Regex AI
#
# ------------------------------

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


@ai_blueprint.route("/regexai", methods=["POST"])
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
        try:
            tool_calls2 = tool_calls2
        except NameError:
            tool_calls2 = None
        return {
            "regex": res.regexs,
            "test_cases": res.test_cases,
            "message": "",
            "tool": bool(tool_calls),
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
    
# ------------------------------
#
# Regex AI
#
# ------------------------------

# ------------------------------
# 
# Color Palette AI
#
# ------------------------------

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


@ai_blueprint.route("/aiv2back", methods=["POST"])
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

# ------------------------------
# 
# Color Palette AI
#
# ------------------------------