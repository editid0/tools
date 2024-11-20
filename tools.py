if __name__ == "__main__":
    print("#"*20)
    print("#"*20)
    print("This file is not meant to be run directly.")
    print("#"*20)
    print("#"*20)
    print("Do not run this file.")
    print("#"*20)
    print("#"*20)
    exit()

#https://stackoverflow.com/a/59155127/15622854
from flask import Blueprint, render_template, request

tools_blueprint = Blueprint('tools', __name__)

@tools_blueprint.route('/ai_color_palette')
def ai_color_palette():
    return render_template('aicolorpalette.html')

@tools_blueprint.route('/base_64_to_image')
def base_64_to_image():
    return render_template('base642image.html')

@tools_blueprint.route('/diff_editor')
def diff_editor():
    return render_template('diffeditor.html')

@tools_blueprint.route('/foreground_helper')
def foreground_helper():
    return render_template('foreground.html', path=request.path)

@tools_blueprint.route('/background_helper')
def background_helper():
    return render_template('foreground.html', path=request.path)

@tools_blueprint.route('/hex_to_hsl')
def hex_to_hsl():
    return render_template('hex2hsl.html')

@tools_blueprint.route('/hex_to_rgb')
def hex_to_rgb():
    return render_template('hex2rgb.html')

@tools_blueprint.route('/image_to_palette')
def image_to_palette():
    return render_template('im2palette.html')

@tools_blueprint.route('/image_to_base64')
def image_to_base64():
    return render_template('image2base64.html')

@tools_blueprint.route('/json_editor')
def json_editor():
    return render_template('json_editor.html')

@tools_blueprint.route('/json_to_yaml')
def json_to_yaml():
    return render_template('json2yaml.html')

@tools_blueprint.route('/markdown_editor')
def markdown_editor():
    return render_template('markdownEditor.html')

@tools_blueprint.route('/meta_tag_generator')
def meta_tag_generator():
    return render_template('metatags.html')

@tools_blueprint.route('/palette_generator')
def palette_generator():
    return render_template('palettegen.html')

@tools_blueprint.route('/qr_code_generator')
def qr_code_generator():
    return render_template('qrcodegen.html')

@tools_blueprint.route('/regex_generator')
def regex_generator():
    return render_template('regexgenerator.html')

@tools_blueprint.route('/svg_to_image')
def svg_to_image():
    return render_template('svg2image.html')

@tools_blueprint.route('/timestamp_converter')
def timestamp_converter():
    return render_template('timestampconv.html')

@tools_blueprint.route('/uuid_generator')
def uuid_generator():
    return render_template('uuidgen.html')

@tools_blueprint.route('/password_generator')
def password_generator():
    return render_template('passwordgen.html')

@tools_blueprint.route("/socketio")
def socketio():
    return render_template("redirto_socketio.html")

@tools_blueprint.route("/clipboard_to_image")
def clipboard_to_image():
    return render_template("clipboard2file.html")

@tools_blueprint.route('/lorem_ipsum_generator')
def lorem_ipsum_generator():
    return render_template('loremipsum.html')

@tools_blueprint.route('/url_encode_decode')
def url_encode_decode():
    return render_template('urlencdec.html')

