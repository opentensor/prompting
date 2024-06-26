class MaxRetryError(Exception):
    """Exception raised when the maximum number of retries is exceeded."""

    def __init__(self, message="Maximum number of retries exceeded"):
        self.message = message
        super().__init__(self.message)


class TaskCreationError(Exception):
    """Exception raised when the task creation fails."""

    def __init__(self, message="Task creation failed"):
        self.message = message
        super().__init__(self.message)
