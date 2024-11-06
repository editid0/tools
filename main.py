from flask import Flask, render_template, request

app = Flask(__name__)
tools = [
    {
        'name': 'Hex to RGB and RGB to Hex',
        'description': 'Converts hex to rgb and rgb to hex',
        'link': '/hex2rgb',
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5738)