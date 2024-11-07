from flask import Flask, render_template, request
import requests
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

@app.route('/colorai')
def colorai():
    color = request.args.get('color')
    fgbg = request.args.get('fgbg')
    # local AI
    # req = requests.get(f'http://192.168.7.254:57372?color={color}&fgbg={fgbg}')
    # return req.json()

    # openAI
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are an AI designed to help pick out complementary colors that are accessible to users, depending on whether you are provided with a foreground (text) color, or a background color you will provide with a suitable choice for the other one, and provide a short sentence explaining why it\'s the ideal choice, as well as other possible choices if there are any. Return a reason key, and a choices key which has an array of possible hex colors.",
        },
        {
            "role": "user",
            "content": f"{color}, {fgbg}",
        }
    ],
    model="gpt-4o-mini",
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5738)