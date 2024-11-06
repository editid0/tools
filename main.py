from flask import Flask, render_template

app = Flask(__name__)
tools = [
    {
        'name': 'Git',
        'description': 'Git is a free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency.',
        'link': 'https://git-scm.com/',
        'image': 'https://git-scm.com/images/logos/downloads/Git-Icon-1788C.png'
    },
]

@app.route('/')
def index():
    return render_template('index.html', tools=tools)

@app.route('/hex2rgb')
def hex2rgb():
    return render_template('hex2rgb.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5738)