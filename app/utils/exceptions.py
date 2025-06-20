class EventOddsChangedError(Exception):
    """Exception raised when the odds of a bet change.
    and exceed the maximum bet odd allowed."""

    def __init__(self, message="The odds of the bet have changed."):
        super().__init__(message)
