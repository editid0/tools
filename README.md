# ModuTools (In development)

Tools is a platform for developers, with all your everyday developer tools in one place, and it is ad free. Click the link below.

[Modutools](https://modu.tools)

<!-- Table of Contents -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#Additional-Information">Additional Information</a></li>
  </ol>
</details>

<!-- Details about the project -->

## About the Project

Tools is created using Python and HTML, CSS is done using Bulma Framework. Tools has a lot of simple utilities all packaged up into a single website, and there is no ads on the website so use the website distraction free. Some of the most used utilities are Hex to RGB Converter, JSON Editor and Markdown editor.

<!-- What tools are used to make the project -->

### Built With

-   [Python](https://www.python.org/doc/)
-   HTML
-   [Bulma](https://bulma.io/documentation/)
-   [Font Awesome](https://fontawesome.com/)
-   [Umami](https://umami.is/)
-   [JSDiff](https://github.com/kpdecker/jsdiff)
-   [Highlight.js](https://highlightjs.org/)
-   [Color-Thief](https://github.com/lokesh/color-thief)
-   [JSON Editor](https://github.com/josdejong/jsoneditor)
-   [JS-YAML](https://www.npmjs.com/package/js-yaml)
-   [Marked](https://www.npmjs.com/package/marked)
-   [github-markdown-css](https://github.com/sindresorhus/github-markdown-css)
-   [uuid](https://www.npmjs.com/package/uuid)
-   [QRCode.js](https://davidshimjs.github.io/qrcodejs/)
-   [chroma.js](https://gka.github.io/chroma.js/)

<!-- Add more if needed -->

<!-- How to isntall and run the project -->

## Installation

### Windows:

1. Install requirements:

```
py -3 pip install -r requirements.txt
```

2. Run the webserver:

```
py -3 main.py
```

> If this is your first time running, ensure that the script outputs that it is creating a .env file and a data.json file.

### Linux/Mac

1. Install requirements

```sh
pip3 install -r requirements.txt
```

2. Run webserver

```sh
python3 main.py
```

> If this is your first time running, ensure that the script outputs that it is creating a .env file and a data.json file.

## Additional Information

1. Reporting Bugs:
   Feel free to report any bugs to the Issues section on github.

2. Features:
   If you have any new feature recommendations, feel free to drop them in Discussions/Ideas on Github.

## Compatibility

The tools on this list aren't guaranteed to be available, and the compatibility isn't guaranteed either, the tools were tested on 21/01/2025.

| Tool                        | Firefox | Chrome |
| --------------------------- | ------- | ------ |
| AI colour palette generator | ✅      | ✅     |
| Base 64 to image            | ✅      | ✅     |
| Diff editor                 | ✅      | ✅     |
| Foreground colour helper    | ✅      | ✅     |
| Background colour helper    | ✅      | ✅     |
| Hex to HSL                  | ✅      | ✅     |
| Hex to RGB                  | ✅      | ✅     |
| Image to base 64            | ✅      | ✅     |
| JSON editor                 | ✅      | ✅     |
| JSON to YAML                | ✅      | ✅     |
| Markdown editor             | ✅      | ✅     |
| Meta tag generator          | ✅      | ✅     |
| Colour palette generator    | ✅      | ✅     |
| QR code generator           | 🆗 1    | ✅     |
| AI regex generator          | ✅      | ✅     |
| Timestamp converter         | ✅      | ✅     |
| UUID generator              | ✅      | ✅     |
| Password generator          | ✅      | ✅     |
| Socket.IO tester            | ✅      | ✅     |
| Clipboard to image          | ❌2     | ✅     |
| Lorem ipsum generator       | ✅      | ✅     |
| URL encode/decode           | ✅      | ✅     |
| Hash generator              | ✅      | ✅     |

### Notes

The issues below will be added to the roadmap and fixed as soon as possible, and this page will be updated when they are fixed.

> #### 1
>
> It doesn't render the QR codes on the client, but if you press "Generate", it will render it on the server and send it as an image.

> #### 2
>
> It seems that the data doesn't correctly save, resulting in a blank image file.

> #### 3
>
> Encoding text to URL strings works fine, but decoding doesn't seem to work.
