#!/usr/bin/env python3
"""Square app/favicon mark derived from the MAGICS badge.

The full wordmark is illegible at 16px, so the square mark keeps the two
distinctive parts that survive at that size: the gold bracket rules and a
white M on USF green.
"""
from PIL import Image, ImageDraw, ImageFont

USF_GREEN      = (0, 84, 60, 255)
USF_GREEN_LIFT = (13, 106, 76, 255)
USF_GOLD       = (253, 187, 48, 255)
WHITE          = (255, 255, 255, 255)
HELV = "/System/Library/Fonts/Helvetica.ttc"

U  = 512          # design grid
SS = 2            # supersample

def render(px_out):
    S = U * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(S * 0.16)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=USF_GREEN)

    grad = Image.new("RGBA", (1, S))
    gp = grad.load()
    for y in range(S):
        t = y / float(S - 1)
        gp[0, y] = tuple(int(round(a + (b - a) * t))
                         for a, b in zip(USF_GREEN_LIFT, USF_GREEN))[:3] + (255,)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=255)
    img.paste(grad.resize((S, S)), (0, 0), mask)
    d = ImageDraw.Draw(img)

    # gold rules, proportionally thicker than the badge so they hold at 16px
    t = int(S * 0.055)
    inset = int(S * 0.17)
    d.rectangle([inset, int(S * 0.20), S - inset, int(S * 0.20) + t], fill=USF_GOLD)
    d.rectangle([inset, int(S * 0.80) - t, S - inset, int(S * 0.80)], fill=USF_GOLD)

    # white M filling the space between the rules
    cap = S * 0.34
    size = int(cap / 0.717)
    f = ImageFont.truetype(HELV, size, index=0)
    d.text((S / 2, S / 2 + cap * 0.03), "M", font=f, fill=WHITE, anchor="mm")

    return img.resize((px_out, px_out), Image.LANCZOS)

sizes = {"favicon-16x16.png": 16, "favicon-32x32.png": 32, "favicon.png": 32,
         "apple-touch-icon.png": 180, "android-chrome-192x192.png": 192,
         "android-chrome-512x512.png": 512}
for name, px in sizes.items():
    render(px).save(name)
    print("%-28s %dpx" % (name, px))

ico = render(256)
ico.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("favicon.ico                  multi-resolution")

# contact sheet so the small sizes can actually be eyeballed
sheet = Image.new("RGBA", (460, 220), (245, 246, 245, 255))
x = 20
for px in (16, 32, 48, 64, 128):
    m = render(px)
    sheet.paste(m, (x, 150 - px), m)
    x += px + 24
sheet.save("favicon_sheet.png")
print("favicon_sheet.png            preview at real sizes")
