"""
Utility functions
"""

import os
import math


def load_dict(lang):
    """Read the dictionnary file and returns all words in it.
    """

    with open(
            os.path.join(os.path.dirname(__file__), "dicts", lang + ".txt"),
            "r",
            encoding="utf8",
            errors="ignore",
    ) as d:
        lang_dict = [l for l in d.read().splitlines() if len(l) > 0]
    return lang_dict


def load_fonts(lang):
    """Load all fonts in the fonts directories
    """

    if lang == "cn":
        return [
            os.path.join(os.path.dirname(__file__), "fonts/cn", font)
            for font in os.listdir(os.path.join(os.path.dirname(__file__), "fonts/cn"))
        ]
    else:
        return [
            os.path.join(os.path.dirname(__file__), "fonts/latin", font)
            for font in os.listdir(
                os.path.join(os.path.dirname(__file__), "fonts/latin")
            )
        ]


def after_rotate(w, h, rotn_center, angle, query):
    angle = angle % 360.0
    angle = - math.radians(angle)
    matrix = [
        round(math.cos(angle), 15), round(math.sin(angle), 15), 0.0,
        round(-math.sin(angle), 15), round(math.cos(angle), 15), 0.0
    ]

    def transform(x, y, matrix):
        (a, b, c, d, e, f) = matrix
        return a * x + b * y + c, d * x + e * y + f

    matrix[2], matrix[5] = transform(-rotn_center[0],
                                     -rotn_center[1], matrix)
    matrix[2] += rotn_center[0]
    matrix[5] += rotn_center[1]

    xx = []
    yy = []
    for x, y in ((0, 0), (w, 0), (w, h), (0, h)):
        x, y = transform(x, y, matrix)
        xx.append(x)
        yy.append(y)
    nw = int(math.ceil(max(xx)) - math.floor(min(xx)))
    nh = int(math.ceil(max(yy)) - math.floor(min(yy)))

    # We multiply a translation matrix from the right.  Because of its
    # special form, this is the same as taking the image of the
    # translation vector as new translation vector.
    matrix[2], matrix[5] = transform((nw - w) / 2.0,
                                     (nh - h) / 2.0,
                                     matrix)

    outp = []
    for q in query:
        rotated = [transform(i[0], i[1], matrix) for i in q]
        outp.append(rotated)
    return outp
