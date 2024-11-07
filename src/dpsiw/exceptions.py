class CompletedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class AbandonedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class DeadLetteredException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
