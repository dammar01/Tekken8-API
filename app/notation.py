from PIL import Image, ImageFont, ImageDraw
from dotenv import load_dotenv
from .model import Notation
import re, os

load_dotenv()


def convert_notation(data: str):
    # Replace symbols with words
    data = data.replace(" ", ",'next',")
    data = data.replace(".", ",")
    data = data.replace(":", ",'colon',")
    data = data.replace("*", ",'hold',")
    data = data.replace("<", ",'delay1',")
    data = data.replace(">", ",'delay2',")
    data = data.replace("~", ",~,")
    data = data.replace("(", "[,")
    data = data.replace(")", ",]")

    # Convert capital letters to the format ^lowercase
    data = re.sub(r"([A-Z])", lambda match: f"^{match.group(1).lower()}", data)
    data = re.sub(r"([a-zA-Z]+)\+(\d+)", r"\1,\2", data)
    return data


def draw_character_name(name: str):
    font = ImageFont.truetype("arial.ttf", 64)
    raw_width = len(str(name)) + 2
    img_size = (int(os.getenv("NAME_TEXT_WIDTH")) * raw_width, 64)
    im = Image.new("RGB", img_size)
    d = ImageDraw.Draw(im)
    d.line((0, 0) + im.size, fill=128)
    d.text((0, 0), f"{name}:", fill="white", font=font)
    return im


def draw_starter_frame(frame: int):
    font = ImageFont.truetype("arial.ttf", 128)
    raw_width = len(str(frame)) + 2
    img_size = (int(os.getenv("FRAME_TEXT_WIDTH")) * raw_width, 128)
    im = Image.new("RGB", img_size)
    d = ImageDraw.Draw(im)
    d.text((0, 0), f"{frame}F", fill="white", font=font)
    return im


def draw_notation(notation: list):
    images = []
    for raw in notation:
        if raw != "":
            try:
                img = Image.open(f"./app/public/button/{raw}.png")
                images.append(img)
            except FileNotFoundError:
                return {"error": f"Notation '{raw}' not found.", "data": notation}
    if not images:
        return {"error": "No images to merge."}

    new_width = sum(img.width for img in images)
    new_height = max(img.height for img in images)
    new_image = Image.new("RGB", (new_width, new_height))

    current_x = 0
    for img in images:
        new_image.paste(img, (current_x, 0))
        current_x += img.width
    return new_image


def get_img_notation(data: Notation):
    converted = convert_notation(data.notation)
    img_notation = draw_notation(converted.split(","))
    if isinstance(img_notation, dict):
        return img_notation

    if data.character_name is not None:
        p = 5
        img_frame = draw_starter_frame(data.starter_frame)
        img_chara_name = draw_character_name(data.character_name)
        results = Image.new(
            "RGB",
            (
                img_notation.width + img_frame.width,
                img_notation.height + img_chara_name.height + p,
            ),
        )
        results.paste(img_chara_name, (0, 0))
        results.paste(img_frame, (0, img_chara_name.height + p))
        results.paste(img_notation, (img_frame.width, img_chara_name.height + p))
    else:
        img_frame = draw_starter_frame(data.starter_frame)
        results = Image.new(
            "RGB",
            (
                img_notation.width + img_frame.width,
                img_notation.height,
            ),
        )
        results.paste(img_frame, (0, 0))
        results.paste(img_notation, (img_frame.width, 0))
    return results
