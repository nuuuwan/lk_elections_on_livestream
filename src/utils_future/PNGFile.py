import math
import os

from PIL import Image, ImageDraw, ImageFont
from utils import File, Log

log = Log("PNGFile")


class PNGFile(File):

    @staticmethod
    def get_font(watermark_text, width, height):
        diag = math.sqrt(width**2 + height**2)
        font_size = int(1.25 * diag / len(watermark_text))
        font_path = os.path.join("media", "fonts", "Afacad-Regular.ttf")
        font = ImageFont.truetype(font_path, font_size)
        return font, font_size

    @staticmethod
    def get_text_info(draw, watermark_text, width, height):
        font, font_size = PNGFile.get_font(watermark_text, width, height)
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width, text_height = (
            text_bbox[2] - text_bbox[0],
            text_bbox[3] - text_bbox[1],
        )
        angle = math.degrees(math.atan2(height, width))
        return text_width, text_height, angle, font, font_size

    @staticmethod
    def get_text_im(watermark_text, watermark_color, width, height, draw):

        text_width, text_height, angle, font, font_size = (
            PNGFile.get_text_info(draw, watermark_text, width, height)
        )
        padding = font_size * 4
        text_img = Image.new(
            "RGBA",
            (text_width + padding * 2, text_height + padding * 2),
            (255, 255, 255, 0),
        )
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text(
            (padding, padding),
            watermark_text,
            fill=watermark_color,
            font=font,
        )

        text_img = text_img.rotate(angle, expand=1)
        return text_img

    def add_watermark(self, watermark_text, watermark_color=(0, 0, 0, 4)):
        img = Image.open(self.path).convert("RGBA")
        width, height = img.size
        img = img.resize((width, height))
        draw = ImageDraw.Draw(img)
        text_img = PNGFile.get_text_im(
            watermark_text, watermark_color, width, height, draw
        )

        x = (width - text_img.width) // 2
        y = (height - text_img.height) // 2

        img.paste(text_img, (x, y), text_img)
        img.save(self.path)
        log.info(f"[add_watermark] Wrote {self.path}")

        return self

    def resize(self, width, height):
        im = Image.open(self.path)
        cur_width, cur_height = im.size

        scale_width = width / cur_width
        scale_height = height / cur_height

        scale = min(scale_width, scale_height)
        im_resized = im.resize(
            (int(cur_width * scale), int(cur_height * scale))
        )

        new_im = Image.new("RGB", (width, height), (255, 255, 255))
        new_im.paste(
            im_resized,
            (
                (width - im_resized.width) // 2,
                (height - im_resized.height) // 2,
            ),
        )
        new_im.save(self.path)
        log.info(f"[resize] Wrote {self.path}")
        return self

    def add_padding(self, p_padding):
        img = Image.open(self.path)
        width, height = img.size

        new_width = int(width * (1 + p_padding * 2))
        new_height = int(height * (1 + p_padding * 2))
        new_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))
        new_img.paste(
            img, ((new_width - width) // 2, (new_height - height) // 2)
        )
        new_img.save(self.path)
        log.info(f"[add_padding] Wrote {self.path}")
        return self
