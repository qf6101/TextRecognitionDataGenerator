from ..data_generator import FakeTextDataGenerator
from PIL import Image, ImageDraw
import random
from ..utils import after_rotate


class CompoundGenerator:

    def __init__(
            self,
            count=-1,
            language="en",
            size=32,
            skewing_angle=0,
            random_skew=False,
            blur=0,
            random_blur=False,
            background_type=0,
            distorsion_type=0,
            distorsion_orientation=0,
            is_handwritten=False,
            width=-1,
            text_color="#282828",
            orientation=0,
            space_width=1.0,
            character_spacing=0,
            margins=(5, 5, 5, 5),
            fit=False,
            line_margin=5,
            box_skewing_angle=0,
            box_random_skew=False
    ):
        self.count = count
        self.language = language
        self.size = size
        self.skewing_angle = skewing_angle
        self.random_skew = random_skew
        self.blur = blur
        self.random_blur = random_blur
        self.background_type = background_type
        self.distorsion_type = distorsion_type
        self.distorsion_orientation = distorsion_orientation
        self.is_handwritten = is_handwritten
        self.width = width
        self.text_color = text_color
        self.orientation = orientation
        self.space_width = space_width
        self.character_spacing = character_spacing
        self.margins = margins
        self.fit = fit
        self.generated_count = 0
        self.line_margin = line_margin
        self.box_skewing_angle = box_skewing_angle
        self.box_random_skew = box_random_skew

        random.seed()

    def line_noise(self):
        range = 1
        return random.randint(-range, range), random.randint(-range, range), \
               random.randint(-range, range), random.randint(-range, range)

    def gen(self, args):
        images = []
        widths = []
        heights = []

        for text in args.texts:
            img, width, height = FakeTextDataGenerator.generate(
                self.generated_count,
                text,
                args.font,
                None,
                self.size,
                None,
                self.skewing_angle,
                self.random_skew,
                self.blur,
                self.random_blur,
                self.background_type,
                self.distorsion_type,
                self.distorsion_orientation,
                self.is_handwritten,
                0,
                self.width,
                args.alignment,
                self.text_color,
                self.orientation,
                self.space_width,
                self.character_spacing,
                self.margins,
                self.fit,
                args.bold
            )

            images.append(img)
            widths.append(width)
            heights.append(height)

        width = max(widths)

        dst = Image.new('RGBA',
                        (width + args.box_margins[0] * 2, self.size * len(args.texts) + args.box_margins[1] * 2))
        img_locs = []

        for idx, img_ in enumerate(images):
            img = Image.new('RGBA', (width, self.size))
            if args.alignment == 0:
                img.paste(img_, (0, 0))
                bkg_ = Image.new("L", (width - img_.width, self.size), 255).convert("RGBA")
                img.paste(bkg_, (img_.width, 0))
                dst.paste(img, (args.box_margins[0], idx * self.size + args.box_margins[1]))

                loc = (
                    (args.box_margins[0], idx * self.size + args.box_margins[1]),
                    (args.box_margins[0] + img_.width, idx * self.size + args.box_margins[1]),
                    (args.box_margins[0] + img_.width, idx * self.size + args.box_margins[1] + img_.height),
                    (args.box_margins[0], idx * self.size + args.box_margins[1] + img_.height)
                )
            elif args.alignment == 1:
                img.paste(img_, ((img.width - img_.width)//2, 0))
                bkg_ = Image.new("L", ((img.width - img_.width)//2, self.size), 255).convert("RGBA")
                img.paste(bkg_, (0, 0))
                img.paste(bkg_, ((img.width + img_.width)//2, 0))
                dst.paste(img, (args.box_margins[0], idx * self.size + args.box_margins[1]))
                diff = (dst.width - img_.width)//2
                loc = (
                    (diff, idx * self.size + args.box_margins[1]),
                    (img_.width + diff, idx * self.size + args.box_margins[1]),
                    (img_.width + diff, idx * self.size + args.box_margins[1] + img_.height),
                    (diff, idx * self.size + args.box_margins[1] + img_.height)
                )

            img_locs.append(loc)

        bkg_ = Image.new("L", (dst.width, args.box_margins[1]), 255).convert("RGBA")
        dst.paste(bkg_, (0, 0))
        dst.paste(bkg_, (0, dst.height - args.box_margins[1]))
        bkg_ = Image.new("L", (args.box_margins[0], dst.height), 255).convert("RGBA")
        dst.paste(bkg_, (0, 0))
        dst.paste(bkg_, (dst.width - args.box_margins[0], 0))

        if args.box_lines[0] > 0:
            draw = ImageDraw.Draw(dst)
            ln = self.line_noise()
            draw.line((self.line_margin + ln[0], self.line_margin + ln[1], self.line_margin + ln[2],
                       dst.height - self.line_margin + ln[3]), fill='black')

        if args.box_lines[1] > 0:
            draw = ImageDraw.Draw(dst)
            ln = self.line_noise()
            draw.line((self.line_margin + ln[0], self.line_margin + ln[1], dst.width - self.line_margin + ln[2],
                       self.line_margin + ln[3]), fill='black')

        if args.box_lines[2] > 0:
            draw = ImageDraw.Draw(dst)
            ln = self.line_noise()
            draw.line(
                (dst.width - self.line_margin + ln[0], self.line_margin + ln[1], dst.width - self.line_margin + ln[2],
                 dst.height - self.line_margin + ln[3]), fill='black')

        if args.box_lines[3] > 0:
            draw = ImageDraw.Draw(dst)
            ln = self.line_noise()
            draw.line(
                (self.line_margin + ln[0], dst.height - self.line_margin + ln[1], dst.width - self.line_margin + ln[2],
                 dst.height - self.line_margin + ln[3]), fill='black')

        box_random_angle = random.randint(0 - self.box_skewing_angle, self.box_skewing_angle)
        box_random_angle = self.box_skewing_angle if not self.box_random_skew else box_random_angle
        dst = dst.rotate(box_random_angle, expand=True)

        img_locs = after_rotate(dst.width, dst.height, (dst.width/2, dst.height/2), -box_random_angle, img_locs)

        # draw = ImageDraw.Draw(dst)
        # for i in img_locs:
        #     print(i)
        #     draw.line((i[0], i[1]), fill='black')
        #     draw.line((i[1], i[2]), fill='black')
        #     draw.line((i[2], i[3]), fill='black')
        #     draw.line((i[3], i[0]), fill='black')

        return dst, img_locs
