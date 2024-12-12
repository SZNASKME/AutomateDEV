from __future__ import (print_function)
from time import sleep
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import event


class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension
    """

    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()

        # Flag to control the event loop below
        self.run = True

    def extension_start(self, fields):
        """Required method that serves as the starting point for work performed
        for a task instance.

        Parameters
        ----------
        fields : dict
            populated with field values from the associated task instance
            launched in the Controller

        Returns
        -------
        ExtensionResult
            once the work is done, an instance of ExtensionResult must be
            returned. See the documentation for a full list of parameters that
            can be passed to the ExtensionResult class constructor
        """

        # Get the value of the 'sleep_value' field
        sleep_value = fields.get('sleep_value', 3)

        # loop that publishes events continuously as long as self.run is True
        while self.run:
            # Publish an event
            event.publish(
                'publisher_event',
                {}
            )

            # sleep before publishing next event
            sleep(sleep_value)

        # Return the result with a payload marking the end of extension_start()
        return ExtensionResult(
            unv_output='extension_start() finished'
        )

    def extension_cancel(self):
        """Optional method that allows the Extension to do any cleanup work
        before finishing
        """
        # Set self.run to False which will end the event loop above
        self.run = False
