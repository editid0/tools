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

# https://stackoverflow.com/a/59155127/15622854
from datetime import datetime, timedelta
import hashlib
import io
import json
import os
import dotenv
from flask import Blueprint, Response, jsonify, render_template, request
import humanize
import qrcode

tools_blueprint = Blueprint("tools", __name__)

dotenv.load_dotenv()
DAILY_AI_LIMIT = os.getenv(
    "DAILY_AI_LIMIT", 100
)  # This value is much lower on the server


# @tools_blueprint.route("/ai_color_palette")
# def ai_color_palette():
#     return render_template("aicolorpalette.html")


@tools_blueprint.route("/base_64_to_image")
def base_64_to_image():
    return render_template("base642image.html")


@tools_blueprint.route("/diff_editor")
def diff_editor():
    return render_template("diffeditor.html")


@tools_blueprint.route("/foreground_helper")
def foreground_helper():
    return render_template("foreground.html", path=request.path)


@tools_blueprint.route("/background_helper")
def background_helper():
    return render_template("foreground.html", path=request.path)


@tools_blueprint.route("/hex_to_hsl")
def hex_to_hsl():
    return render_template("hex2hsl.html")


@tools_blueprint.route("/hex_to_rgb")
def hex_to_rgb():
    return render_template("hex2rgb.html")


# @tools_blueprint.route("/image_to_palette")
# def image_to_palette():
#     return render_template("im2palette.html")


@tools_blueprint.route("/image_to_base64")
def image_to_base64():
    return render_template("image2base64.html")


@tools_blueprint.route("/json_editor")
def json_editor():
    return render_template("json_editor.html")


@tools_blueprint.route("/json_to_yaml")
def json_to_yaml():
    return render_template("json2yaml.html")


@tools_blueprint.route("/markdown_editor")
def markdown_editor():
    return render_template("markdownEditor.html")


@tools_blueprint.route("/meta_tag_generator")
def meta_tag_generator():
    return render_template("metatags.html")


@tools_blueprint.route("/palette_generator")
def palette_generator():
    return render_template("palettegen.html")


@tools_blueprint.route("/qr_code_generator")
def qr_code_generator():
    return render_template("qrcodegen.html")


@tools_blueprint.route("/qr_code_generator/generate", methods=["GET"])
def qr_code_generator_generate():
    data = request.args
    text = data.get("text", "").strip()

    # Validate input
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Limit text length (QR codes typically have practical limits around 2000-4000 characters)
    if len(text) > 2000:
        return jsonify({"error": "Text too long. Maximum 2000 characters allowed"}), 400

    # Basic sanitization - remove control characters but keep newlines
    text = "".join(
        char
        for char in text
        if char == "\n" or (char.isprintable() and ord(char) < 0xFFFF)
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bts = io.BytesIO()
    img.save(bts, format="PNG")
    return Response(bts.getvalue(), mimetype="image/png")


@tools_blueprint.route("/regex_generator")
def regex_generator():
    return render_template("regexgenerator.html")


# @tools_blueprint.route("/svg_to_image")
# def svg_to_image():
#     return render_template("svg2image.html")


@tools_blueprint.route("/timestamp_converter")
def timestamp_converter():
    return render_template("timestampconv.html")


@tools_blueprint.route("/uuid_generator")
def uuid_generator():
    return render_template("uuidgen.html")


@tools_blueprint.route("/password_generator")
def password_generator():
    return render_template("passwordgenerator.html")


@tools_blueprint.route("/socketio")
def socketio():
    return render_template("redirto_socketio.html")


@tools_blueprint.route("/clipboard_to_image")
def clipboard_to_image():
    return render_template("clipboard2file.html")


@tools_blueprint.route("/lorem_ipsum_generator")
def lorem_ipsum_generator():
    return render_template("loremipsum.html")


@tools_blueprint.route("/url_encode_decode")
def url_encode_decode():
    return render_template("urlencdec.html")


@tools_blueprint.route("/hash_generator")
def hash_generator():
    return render_template("hasher.html")


@tools_blueprint.route("/ai_color_palette")
def aiv3():
    """
    Use chatgpt memory function to hardcode the coventry college colors
    """
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
    if ip_hash not in data[today_string]:
        data[today_string][ip_hash] = 0
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
        message = f"You have exceeded the limit of {DAILY_AI_LIMIT} requests per day. Please try again in {resets}."
        remaining = 0
    else:
        remaining = DAILY_AI_LIMIT - data[today_string][ip_hash]
        message = ""
    return render_template("aicolor2.html", remaining=remaining, message=message)


@tools_blueprint.route("/contrast_checker")
def contrast_checker():
    return render_template("contrastchecker.html")
