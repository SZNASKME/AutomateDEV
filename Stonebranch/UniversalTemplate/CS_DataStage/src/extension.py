from __future__ import (print_function)
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import logger


class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension
    """

    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()

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

        # Get the value of the 'action' field
        action_field = fields.get('action', [])
        if len(action_field) != 1:
            # 'action' field was not specified or is invalid
            action = ''
        else:
            action = action_field[0]

        if action.lower() == 'print':
            # Print to standard output...
            print("Hello STDOUT!")
        else:
            # Log to standard error...
            logger.info('Hello STDERR!')

        # Return the result with a payload containing a Hello message...
        return ExtensionResult(
            unv_output='Hello Extension!'
        )
