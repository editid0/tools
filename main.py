from datetime import datetime
import io, re, dotenv, os, git
from flask import Flask, Response, render_template, request
from markupsafe import Markup
from PIL import Image, ImageDraw, ImageFont

repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha[:7]
full_sha = repo.head.object.hexsha

# check if .env file exists
if not os.path.exists(".env"):
    # create .env file
    print("Creating .env file...")
    with open(".env", "w") as f:
        f.write("")

    # add OPENAI_API_KEY to .env file
    with open(".env", "a") as f:
        f.write("OPENAI_API_KEY=''")

# check if data.json exists
if not os.path.exists("data.json"):
    # create data.json file
    print("Creating data.json file...")
    with open("data.json", "w") as f:
        f.write("{}")

dotenv.load_dotenv()


if os.getenv("SENTRY_DSN"):
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
    )
CREATORS = os.getenv("CREATORS", "editid0 on GitHub")
REPO = os.getenv("REPO", "https://github.com/editid0/tools")
app = Flask(__name__, static_folder="static")

if __name__ == "__main__":
    from tools import tools_blueprint
    from ai import ai_blueprint
    app.register_blueprint(tools_blueprint)
    app.register_blueprint(ai_blueprint)


@app.context_processor
def utility_processor():
    to_return = {}
    to_return["sha"] = sha
    to_return["bulma"] = Markup(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">'
    )
    to_return["fontawesome"] = Markup(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />'
    )
    to_return["analytics"] = (
        Markup(
            '''<script defer src="https://st.editid.uk/script.js" data-website-id="072a1296-3bf0-4db8-a5b0-e538f2e772bb"></script>
            <script>
            !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug getPageViewId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
            posthog.init('phc_1eKoeJ4POr45EQp8vXzF8pR8tNrkomALsHUucX58Lgj', {
                api_host: 'https://eu.i.posthog.com',
                person_profiles: 'always', // or 'always' to create profiles for anonymous users as well
                persistence: 'localStorage',
                opt_out_capturing_by_default: true
            })
            </script>
            '''
        )
        if os.getenv("IS_PRODUCTION")
        else ""
    )
    to_return['year'] = datetime.now().year
    to_return['creators'] = CREATORS
    to_return['repo'] = REPO
    return to_return


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


our_tools = [
    {
        "name": "AI Colour Palette Generator",
        "url": "/ai_color_palette",
        "description": "Generate a colour palette based on a description.",
        "ai": True,
    },
    {
        "name": "Base64 to Image",
        "url": "/base_64_to_image",
        "description": "Convert a base64 image to a file.",
    },
    {
        "name": "Diff Editor",
        "url": "/diff_editor",
        "description": "Generate a diff between two files.",
    },
    {
        "name": "Foreground Colour Helper",
        "url": "/foreground_helper",
        "description": "Generate accessible foreground colours for a given background colour using AI.",
        "ai": True,
    },
    {
        "name": "Background Colour Helper",
        "url": "/background_helper",
        "description": "Generate accessible background colours for a given foreground colour using AI.",
        "ai": True,
    },
    {
        "name": "Hex to HSL",
        "url": "/hex_to_hsl",
        "description": "Convert a hex colour to HSL and vice versa.",
    },
    {
        "name": "Hex to RGB",
        "url": "/hex_to_rgb",
        "description": "Convert a hex colour to RGB and vice versa.",
    },
    {
        "name": "Image to Base64",
        "url": "/image_to_base64",
        "description": "Convert an image to base64.",
    },
    {
        "name": "JSON Editor",
        "url": "/json_editor",
        "description": "Edit and format JSON.",
    },
    {
        "name": "JSON to YAML",
        "url": "/json_to_yaml",
        "description": "Convert JSON to YAML and vice versa.",
    },
    {
        "name": "Markdown editor",
        "url": "/markdown_editor",
        "description": "Edit, format and view Markdown.",
    },
    {
        "name": "Meta Tag Generator",
        "url": "/meta_tag_generator",
        "description": "Generate meta tags for your website.",
    },
    {
        "name": "Colour Palette Generator",
        "url": "/palette_generator",
        "description": "Generate a colour palette.",
    },
    {
        "name": "QR Code Generator",
        "url": "/qr_code_generator",
        "description": "Generate a QR code.",
    },
    {
        "name": "AI Regex Generator",
        "url": "/regex_generator",
        "description": "Generate a regex using a description.",
        "ai": True,
    },
    {
        "name": "Timestamp Converter",
        "url": "/timestamp_converter",
        "description": "Convert a timestamp to a readable format.",
    },
    {
        "name": "UUID Generator",
        "url": "/uuid_generator",
        "description": "Generate a V1, V3, V4 or V5 UUID.",
    },
    {
        "name": "Password Generator",
        "url": "/password_generator",
        "description": "Generate a password.",
    },
    {
        "name": "Socket.IO Tester",
        "url": "/socketio",
        "description": "Test Socket.IO connections.",
    },
    {
        "name": "Clipboard to Image",
        "url": "/clipboard_to_image",
        "description": "Save an image from your clipboard.",
    },
    {
        "name": "Lorem Ipsum Generator",
        "url": "/lorem_ipsum_generator",
        "description": "Generate Lorem Ipsum text.",
    },
    {
        "name": "URL Encoder/Decoder",
        "url": "/url_encode_decode",
        "description": "Encode and decode strings using URL encoding.",
    },
    {
        "name": "Hash Generator",
        "url": "/hash_generator",
        "description": "Generate a hash for a string",
    },
    {
        "name": "Colour Contrast Checker",
        "url": "/contrast_checker",
        "description": "Check the contrast between two colours.",
    }
]


@app.route("/")
def index():
    return render_template("index.html", tools=our_tools, hash=sha, full_sha=full_sha)

@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return app.send_static_file("sitemap.xml")

def extract_hex_codes(text):
    # Regular expression pattern for hex color codes
    pattern = r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b"
    # Find all matches in the text
    return re.findall(pattern, text)


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route("/color/<foreground>/<background>/<text>")
def color_generator(foreground, background, text):
    if not re.match(r"^#[0-9a-fA-F]{6}$", foreground):
        foreground = "#000000"
        background = "#ffffff"
    if not re.match(r"^#[0-9a-fA-F]{6}$", background):
        background = "#ffffff"
        foreground = "#000000"
    if not re.match(r"^#[0-9a-fA-F]{6}$", text):
        text = "#ffffff"
    im = Image.new("RGB", (400, 100), background)
    d = ImageDraw.Draw(im)
    d.text((0, 0), text, fill=foreground, font=ImageFont.load_default(size=70))
    b = io.BytesIO()
    im.save(b, "PNG")
    return Response(b.getvalue(), mimetype="image/png")


@app.route("/assets/<filename>")
def serve_static(filename):
    return app.send_static_file(filename)


@app.route("/like", methods=["POST"])
def like():
    data = request.get_json()
    print(data)  # do something with the data at some point
    return "OK"


@app.route("/dislike", methods=["POST"])
def dislike():
    data = request.get_json()
    print(data)  # do something with the data at some point
    return "OK"


# REMOVE BELOW IN PRODUCTION
# REMOVE BELOW IN PRODUCTION
# REMOVE BELOW IN PRODUCTION


# @app.route("/template/<template_name>")
# def template(template_name):
#     return render_template(f"{template_name}.html")


# REMOVE ABOVE IN PRODUCTION
# REMOVE ABOVE IN PRODUCTION
# REMOVE ABOVE IN PRODUCTION


@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5738)
