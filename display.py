import os

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

font = graphics.Font()
font.LoadFont(os.path.join(os.path.dirname(__file__), "fonts", "5x7.bdf"))
white = graphics.Color(255, 255, 255)


def width_of(text):
    return sum(font.CharacterWidth(ord(c)) for c in text)


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
    lines = wrap(text)
    return [lines[i:i + LINES_PER_PAGE] for i in range(0, len(lines), LINES_PER_PAGE)]


def show_page(page):
    global canvas
    canvas.Clear()
    y = 7
    for line in page:
        graphics.DrawText(canvas, font, 1, y, white, line)
        y += 8
    canvas = matrix.SwapOnVSync(canvas)
