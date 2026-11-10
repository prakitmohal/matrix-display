import time
import dad_joke
import display

SECONDS_PER_PAGE = 4

while True:
    joke = dad_joke.get_joke()
    print (joke)

    for page in pages:
        display.show_page(page)
        time.sleep(SECONDS_PER_PAGE)
