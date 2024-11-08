class CompletedException(Exception):
    """
    Exception raised when a message needs to be marked as completed
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class AbandonedException(Exception):
    """
    Exception raised when a message needs to be abandoned
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class DeadLetteredException(Exception):
    """
    Exception raised when a message needs to be dead lettered
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)
