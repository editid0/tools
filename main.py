from flask import Flask, render_template, request
import requests, re
import dotenv
import os
from openai import OpenAI

dotenv.load_dotenv()

# SnipSpace?

app = Flask(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)

tools = [
    {
        'name': 'Hex to RGB',
        'description': 'Converts hex color codes to RGB values.',
        'link': '/hex2rgb',
        'image': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/haskell/haskell-original.svg'
    },
    {
        'name': 'RGB to Hex',
        'description': 'Converts RGB values to hex color codes.',
        'link': '/rgb2hex',
        'image': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/haskell/haskell-original.svg'
    },
]

@app.route('/')
def index():
    return render_template('index.html', tools=tools)

@app.route('/hex2rgb')
@app.route('/rgb2hex')
def hex2rgb():
    return render_template('hex2rgb.html', path=request.path)

@app.route('/foreground')
@app.route('/background')
def foreground():
    return render_template('foreground.html', path=request.path)

def extract_hex_codes(text):
    # Regular expression pattern for hex color codes
    pattern = r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b"
    # Find all matches in the text
    return re.findall(pattern, text)

@app.route('/colorai')
def colorai():
    color = request.args.get('color')
    fgbg = request.args.get('fgbg')
    print(f'color: {color}, fgbg: {fgbg}')
    # local AI
    # req = requests.get(f'http://192.168.7.254:57372?color={color}&fgbg={fgbg}')
    # return req.json()
    # openAI
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are an AI designed to help pick out complementary colors that are accessible to users, depending on whether you are provided with a foreground (text) color, or a background color you will provide with a suitable choice for the other one, and provide a short sentence explaining why it\'s the ideal choice, as well as other possible choices if there are any.",
        },
        {
            "role": "user",
            "content": f"{fgbg} {color}",
        }
    ],
    model="gpt-4o-mini",
    )
    res = chat_completion.choices[0].message.content
    colors = extract_hex_codes(res)
    return {'reason': res, 'choices': colors}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5738)