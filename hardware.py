from gpiozero import Button, DigitalInputDevice, LED
import time

class Hardware:
    def __init__(self, callbacks):
        """
        Initialize the hardware class.

        :param callbacks: A dictionary of callback functions (e.g., {'play': func_play, 'next': func_next})
        """

        self.callbacks = callbacks

        # Define hardware components
        self.button_play = Button(config.PLAY_BUTTON_PIN, pull_up=True, bounce_time=0.03)
        self.button_next = Button(config.NEXT_BUTTON_PIN, pull_up=True, bounce_time=0.03)
        self.button_prev = Button(config.PREV_BUTTON_PIN, pull_up=True, bounce_time=0.03)

        self.switch_a = DigitalInputDevice(config.SWITCH_PIN_A, pull_up=True, bounce_time=0.5)

        self.button_led = LED(config.LED_PIN)

        # Attach hardware callbacks to buttons
        self.button_play.when_pressed = lambda: self._handle_button('play')
        self.button_next.when_pressed = lambda: self._handle_button('next')
        self.button_prev.when_pressed = lambda: self._handle_button('prev')

        self.switch_a.when_activated = lambda: self._handle_button('switch')
        self.switch_a.when_deactivated = lambda: self._handle_button('switch')

    def _handle_button(self, button_type):
        """
        Internal method to handle button presses and trigger the appropriate callback.
        """
        if button_type in self.callbacks:
            self.callbacks[button_type]()  # Call the linked callback function
        else:
            print(f"No callback defined for {button_type}")

    def blink_led(self, times=3, leave_on=False):
        """
        Blink the LED a specified number of times.
        """
        self.button_led.off()  # Ensure the LED is off initially

        for _ in range(times):
            self.button_led.on()
            time.sleep(0.3)  # LED on for 0.3 seconds
            self.button_led.off()
            time.sleep(0.2)  # LED off for 0.2 seconds

        if leave_on:
            self.button_led.on()

    def led_on(self, on = True):
        """
        Turn led on.
        """
        self.button_led.on()

    def led_on(self, on = True):
        """
        Turn led off.
        """
        self.button_led.off()