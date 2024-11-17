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
from main import app, request, render_template

@app.route('/ai_color_palette')
def ai_color_palette():
    return render_template('aicolorpalette.html')

@app.route('/base_64_to_image')
def base_64_to_image():
    return render_template('base642image.html')

@app.route('/diff_editor')
def diff_editor():
    return render_template('diffeditor.html')

@app.route('/foreground_helper')
def foreground_helper():
    return render_template('foreground.html', path=request.path)

@app.route('/background_helper')
def background_helper():
    return render_template('foreground.html', path=request.path)

@app.route('/hex_to_hsl')
def hex_to_hsl():
    return render_template('hex2hsl.html')

@app.route('/hex_to_rgb')
def hex_to_rgb():
    return render_template('hex2rgb.html')

@app.route('/image_to_palette')
def image_to_palette():
    return render_template('im2palette.html')

@app.route('/image_to_base64')
def image_to_base64():
    return render_template('image2base64.html')

@app.route('/json_editor')
def json_editor():
    return render_template('jsoneditor.html')

@app.route('/json_to_yaml')
def json_to_yaml():
    return render_template('json2yaml.html')

@app.route('/markdown_editor')
def markdown_editor():
    return render_template('markdowneditor.html')

@app.route('/meta_tag_generator')
def meta_tag_generator():
    return render_template('metatags.html')

@app.route('/palette_generator')
def palette_generator():
    return render_template('palettegen.html')

@app.route('/qr_code_generator')
def qr_code_generator():
    return render_template('qrcodegen.html')

@app.route('/regex_generator')
def regex_generator():
    return render_template('regexgenerator.html')

@app.route('/svg_to_image')
def svg_to_image():
    return render_template('svg2image.html')

@app.route('/timestamp_converter')
def timestamp_converter():
    return render_template('timestampconverter.html')

@app.route('/uuid_generator')
def uuid_generator():
    return render_template('uuidgen.html')