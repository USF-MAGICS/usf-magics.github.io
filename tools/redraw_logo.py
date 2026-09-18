#!/usr/bin/env python3
"""Redraw the MAGICS mark at high resolution in USF brand colours.

Geometry is measured from the original 512x208 artwork and reproduced exactly;
only the palette changes (USF Green #00543C and USF Gold #FDBB30 replace the
duller greens and olive-gold of the JPEG) and the type is re-set cleanly.
All coordinates below are in the original 512x208 unit space.
"""
from PIL import Image, ImageDraw, ImageFont

USF_GREEN      = (0, 84, 60)       # #00543C
USF_GREEN_LIFT = (13, 106, 76)     # subtle centre highlight
USF_GOLD       = (253, 187, 48)    # #FDBB30
WHITE          = (255, 255, 255)

HELV       = "/System/Library/Fonts/Helvetica.ttc"
HELV_REG   = 0
CAP_RATIO  = 0.717                 # Helvetica cap height / em

RADIUS = 10
T      = 5                         # gold stroke thickness

# gold bracket frame, left half; the right half is mirrored about x = 256
BRACKETS = [
    # (x0, y0, x1, y1)
    (103,  40, 235,  45),   # top-left    bar
    (230,   9, 235,  45),   # top-left    inner tick (up)
    (103,  40, 108,  58),   # top-left    outer tick (down)
    (103, 137, 235, 142),   # bottom-left bar
    (230, 137, 235, 170),   # bottom-left inner tick (down)
    (103, 123, 108, 142),   # bottom-left outer tick (up)
]

WORD        = "MAGICS"
SUB         = "Research Lab"
SUB_CAP     = 24          # cap height of the second line
SUB_WIDTH   = 299         # tracked to the same width as MAGICS
SUB_BASE    = 205         # cap bottom, below the gold frame (which ends at y169)
WORD_CAP    = 48            # cap height, y 66..113
WORD_TOP    = 66
WORD_WIDTH  = 299           # x 107..405
CENTRE_X    = 256

TAGLINE = ["Machine Learning, Artificial Intelligence,",
           "Game Intelligence, Computing at Scale"]
TAG_WIDTH   = 310           # x 101..410
TAG_TOP     = 170
TAG_LINE_H  = 17


def fit_tracked(draw, text, font, target_w):
    """letter spacing needed to set `text` in `font` across target_w"""
    widths = [draw.textlength(ch, font=font) for ch in text]
    gaps = len(text) - 1
    return widths, (target_w - sum(widths)) / float(gaps) if gaps else 0.0


def draw_tracked(draw, x_left, baseline, text, font, widths, track, fill):
    x = x_left
    for ch, w in zip(text, widths):
        draw.text((x, baseline), ch, font=font, fill=fill, anchor="ls")
        x += w + track


def text_layer(text, size_px, target_w, S):
    """Render `text` tracked to target_w on its own transparent layer and return
    (layer, ink_bbox). Centring is done on the rendered ink, not on font advance
    widths -- the advance of the final glyph is wider than its ink, which pushed
    the wordmark a few pixels right of true centre."""
    font = ImageFont.truetype(HELV, size_px, index=HELV_REG)
    pad = size_px
    layer = Image.new("RGBA", (int(target_w + pad * 2), int(size_px * 2)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    widths, track = fit_tracked(ld, text, font, target_w)
    draw_tracked(ld, pad, size_px * 1.4, text, font, widths, track, WHITE + (255,))
    return layer, layer.getbbox()


def paste_word_centred(img, cx, cy, cap_units, target_w_units, S, text=None):
    size_px = int(round(cap_units / CAP_RATIO * S))
    layer, bbox = text_layer(text or WORD, size_px, target_w_units * S, S)
    ink = layer.crop(bbox)
    img.paste(ink, (int(round(cx - ink.size[0] / 2.0)),
                    int(round(cy - ink.size[1] / 2.0))), ink)


def render(out_path, panel_w, panel_h, scale, with_tagline, ss=2):
    """panel_w/h in units; artwork is centred horizontally in the panel"""
    S = scale * ss
    dx = panel_w / 2.0 - CENTRE_X          # shift artwork to panel centre
    W, Hh = int(panel_w * S), int(panel_h * S)

    def U(v):      # unit -> device
        return v * S

    img = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # panel: flat USF green with a soft elliptical lift toward the centre
    d.rounded_rectangle([0, 0, W - 1, Hh - 1], radius=U(RADIUS), fill=USF_GREEN + (255,))
    grad = Image.new("RGBA", (1, Hh))
    gp = grad.load()
    for y in range(Hh):
        t = y / float(max(1, Hh - 1))
        gp[0, y] = tuple(int(round(a + (b - a) * t)) for a, b in
                         zip(USF_GREEN_LIFT, USF_GREEN)) + (255,)
    grad = grad.resize((W, Hh))
    mask = Image.new("L", (W, Hh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, Hh - 1], radius=U(RADIUS), fill=255)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)

    # gold frame, both halves
    for (x0, y0, x1, y1) in BRACKETS:
        d.rectangle([U(x0 + dx), U(y0), U(x1 + dx), U(y1)], fill=USF_GOLD + (255,))
        mx0, mx1 = 512 - x1, 512 - x0
        d.rectangle([U(mx0 + dx), U(y0), U(mx1 + dx), U(y1)], fill=USF_GOLD + (255,))

    # wordmark, tracked out to the measured width
    # matches the original: wordmark centred on the frame, not on the bar gap
    paste_word_centred(img, U(CENTRE_X + dx), U(89.5), WORD_CAP, WORD_WIDTH, S)
    d = ImageDraw.Draw(img)

    if with_tagline:
        tsize = int(round(13.2 / CAP_RATIO * S))
        tfont = ImageFont.truetype(HELV, tsize, index=HELV_REG)
        scale_fix = U(TAG_WIDTH) / d.textlength(TAGLINE[0], font=tfont)
        tfont = ImageFont.truetype(HELV, max(1, int(round(tsize * scale_fix))), index=HELV_REG)
        for i, line in enumerate(TAGLINE):
            d.text((U(CENTRE_X + dx), U(TAG_TOP + TAG_LINE_H * (i + 1))),
                   line, font=tfont, fill=WHITE + (255,), anchor="ms")

    if ss > 1:
        img = img.resize((int(panel_w * scale), int(panel_h * scale)), Image.LANCZOS)
    img.save(out_path)
    print("%-28s %dx%d" % (out_path, img.size[0], img.size[1]))


def render_mark(out_path, scale, pad=6, ss=2):
    """Gold frame + wordmark on a transparent ground, for use over a CSS band."""
    S = scale * ss
    x0, x1 = 103 - pad, 409 + pad          # gold frame extent
    y0, y1 = 9 - pad, SUB_BASE + pad       # room for the RESEARCH LAB line
    pw, ph = x1 - x0, y1 - y0
    dx, dy = -x0, -y0
    img = Image.new("RGBA", (int(pw * S), int(ph * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def U(v):
        return v * S

    for (bx0, by0, bx1, by1) in BRACKETS:
        d.rectangle([U(bx0 + dx), U(by0 + dy), U(bx1 + dx), U(by1 + dy)], fill=USF_GOLD + (255,))
        mx0, mx1 = 512 - bx1, 512 - bx0
        d.rectangle([U(mx0 + dx), U(by0 + dy), U(mx1 + dx), U(by1 + dy)], fill=USF_GOLD + (255,))

    paste_word_centred(img, U(CENTRE_X + dx), U(89.5 + dy), WORD_CAP, WORD_WIDTH, S)
    paste_word_centred(img, U(CENTRE_X + dx), U(SUB_BASE - SUB_CAP / 2.0 + dy),
                       SUB_CAP, SUB_WIDTH, S, text=SUB)

    img = img.resize((int(pw * scale), int(ph * scale)), Image.LANCZOS)
    img.save(out_path)
    print("%-28s %dx%d  (transparent)" % (out_path, img.size[0], img.size[1]))


if __name__ == "__main__":
    #            file                      panel_w panel_h scale tagline
    # magics-mark.png is the only image the site uses; render() remains for
    # exporting a standalone badge or banner if one is ever needed.
    render_mark("magics-mark.png", 4)
