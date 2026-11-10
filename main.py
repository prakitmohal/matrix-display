import time
import dad_joke
import weather
import display

SECONDS_PER_PAGE = 4

while True:
    w = weather.get_weather()
    if w:
        display.show_weather(w)
        time.sleep(SECONDS_PER_PAGE*2)

    joke = dad_joke.get_joke()
    for page in display.make_pages("DAD JOKE: " + joke):
        display.show_page(page)
        time.sleep(SECONDS_PER_PAGE)
