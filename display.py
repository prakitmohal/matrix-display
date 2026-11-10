import os, unicodedata

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics          # real panel (on the Pi)
except ImportError:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics  # emulator (on your PC)

LINES_PER_PAGE = 4

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

here = os.path.dirname(__file__)

font = graphics.Font()
font.LoadFont(os.path.join(here, "fonts", "5x7.bdf"))
big_font = graphics.Font()
big_font.LoadFont(os.path.join(here, "fonts", "6x10.bdf"))

white = graphics.Color(255, 255, 255)
yellow = graphics.Color(255, 255, 0)
orange = graphics.Color(255, 140, 0)
cyan = graphics.Color(0, 255, 255)

# colors used by the weather icons, as (red, green, blue)
SUN = (255, 200, 0)
CLOUD = (170, 170, 185)
DARK_CLOUD = (110, 110, 130)
RAIN = (0, 130, 255)
ICE = (160, 220, 255)
SNOW = (255, 255, 255)
BOLT = (255, 230, 0)
MOON = (235, 235, 200)
STAR = (200, 200, 255)

REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'",       # curly single quotes
    "\u201c": '"', "\u201d": '"',       # curly double quotes
    "\u2013": "-", "\u2014": "-",       # en and em dashes
    "\u2026": "...",                    # ellipsis
}


def clean(text):
    # the font only has plain letters and symbols, so turn fancy punctuation into plain text
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)
    text = unicodedata.normalize("NFKD", text)       # splits an accented letter into letter + accent
    return text.encode("ascii", "ignore").decode()   # keeps the letter, drops the accent and anything else unknown

def width_of(text, which=None):
    f = which or font
    return sum(f.CharacterWidth(ord(c)) for c in text)


def wrap(text):
    lines = []
    current = ""
    for word in text.split():
        # a single word wider than the panel gets chopped
        while width_of(word) > options.cols:
            cut = len(word)
            while width_of(word[:cut]) > options.cols:
                cut -= 1
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:cut])
            word = word[cut:]
        trial = word if not current else current + " " + word
        if width_of(trial) <= options.cols:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_pages(text):
    lines = wrap(clean(text))
    return [lines[i:i + LINES_PER_PAGE] for i in range(0, len(lines), LINES_PER_PAGE)]


def show_page(page):
    global canvas
    canvas.Clear()
    y = 7
    for line in page:
        graphics.DrawText(canvas, font, 1, y, white, line)
        y += 8
    canvas = matrix.SwapOnVSync(canvas)


# ---------- weather icons, drawn with shapes instead of pixel-by-pixel ----------

def pixel(x, y, color):
    canvas.SetPixel(x, y, color[0], color[1], color[2])


def fill_circle(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                pixel(x, y, color)


def fill_rect(x1, y1, x2, y2, color):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            pixel(x, y, color)


def draw_cloud(ox, oy, color):
    fill_circle(ox + 7, oy + 8, 4, color)
    fill_circle(ox + 12, oy + 5, 5, color)
    fill_circle(ox + 17, oy + 8, 4, color)
    fill_rect(ox + 7, oy + 8, ox + 17, oy + 12, color)


def draw_sun(cx, cy, r, color, rays=True):
    fill_circle(cx, cy, r, color)
    if rays:
        for k in range(r + 2, r + 5):
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                pixel(cx + dx * k, cy + dy * k, color)
        for k in range(r, r + 3):
            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                pixel(cx + dx * k, cy + dy * k, color)

def draw_moon(cx, cy, r, color):
    fill_circle(cx, cy, r, color)
    fill_circle(cx + 3, cy - 2, r - 1, (0, 0, 0))     # a dark circle bitten out of it makes the crescent

def draw_icon(name, ox, oy):
    # every icon fits in a 22 x 22 box whose top-left corner is (ox, oy)
    if name == "sun":
        draw_sun(ox + 11, oy + 11, 5, SUN)
    
    elif name == "moon":
        draw_moon(ox + 10, oy + 11, 7, MOON)
        for x, y in [(3, 4), (17, 4), (19, 12), (16, 19), (4, 17)]:
            pixel(ox + x, oy + y, STAR)

    elif name == "partly_night":
        draw_moon(ox + 7, oy + 7, 5, MOON)
        draw_cloud(ox + 1, oy + 7, CLOUD)
    
    elif name == "partly":
        draw_sun(ox + 7, oy + 7, 4, SUN)
        draw_cloud(ox + 1, oy + 7, CLOUD)

    elif name == "cloud":
        draw_cloud(ox, oy + 5, CLOUD)

    elif name == "fog":
        for row, shift in [(4, 0), (8, 3), (12, 0), (16, 3)]:
            fill_rect(ox + 2 + shift, oy + row, ox + 18 + shift, oy + row, CLOUD)

    elif name in ("rain", "drizzle", "ice"):
        draw_cloud(ox, oy + 1, DARK_CLOUD)
        color = ICE if name == "ice" else RAIN
        for x, y in [(6, 15), (11, 17), (16, 15), (9, 20), (14, 20)]:
            pixel(ox + x, oy + y, color)
            if name != "drizzle":
                pixel(ox + x, oy + y + 1, color)

    elif name == "snow":
        draw_cloud(ox, oy + 1, CLOUD)
        for x, y in [(5, 15), (10, 17), (15, 15), (8, 20), (13, 20), (18, 19)]:
            pixel(ox + x, oy + y, SNOW)

    elif name in ("storm", "hail"):
        draw_cloud(ox, oy + 1, DARK_CLOUD)
        for x, y in [(13, 14), (12, 15), (11, 16), (10, 17), (11, 17), (12, 17),
                     (11, 18), (10, 19), (9, 20), (10, 18)]:
            pixel(ox + x, oy + y, BOLT)
        if name == "hail":
            for x, y in [(5, 17), (16, 18), (6, 20), (17, 21)]:
                pixel(ox + x, oy + y, SNOW)


def show_weather(w):
    # layout on a 64 x 32 panel:
    #   top left (22 x 22): icon      right: label and temperature      bottom row: high and low
    global canvas
    canvas.Clear()

    draw_icon(w["icon"], 1, 1)

    graphics.DrawText(canvas, font, 26, 7, yellow, w["label"])
    graphics.DrawText(canvas, big_font, 26, 19, white, str(w["now"]) + "F")

    low_text = "LO " + str(w["low"])
    graphics.DrawText(canvas, font, 1, 31, orange, "HI " + str(w["high"]))
    graphics.DrawText(canvas, font, options.cols - width_of(low_text), 31, cyan, low_text)   # right-aligned

    canvas = matrix.SwapOnVSync(canvas)
