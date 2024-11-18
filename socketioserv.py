from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
load_dotenv()
from markupsafe import Markup

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('socketio.html')

@app.context_processor
def utility_processor():
    to_return = {}
    to_return["bulma"] = Markup('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">')
    to_return["fontawesome"] = Markup('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />')
    to_return['analytics'] = Markup('<script defer src="https://st.editid.uk/script.js" data-website-id="fd60c701-ca5b-4ddc-9a0d-5602adf865d5"></script>') if os.getenv("IS_PRODUCTION") else ''
    return to_return
    
@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    # sanitize message
    message = message.replace('<', '&lt;').replace('>', '&gt;')
    # respond with message only to specific client
    socketio.send(message, to=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5739, debug=True)