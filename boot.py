from machine import Pin

button = Pin(15, Pin.IN, Pin.PULL_UP)

# the app will start when booted if the button on pin 15 is 
# not engaged (default behavior). If the button is depressed
# then app.py is not run and you can work with the python files.
# if button.value() == 1:   
if button.value() == 0:
    import app

