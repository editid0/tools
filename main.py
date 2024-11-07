from flask import Flask, render_template, request
import requests
import dotenv
import os

# SnipSpace?

app = Flask(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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
    req = requests.get(f'http://192.168.7.254:57372?color={color}&fgbg={fgbg}')
    return req.json()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5738)