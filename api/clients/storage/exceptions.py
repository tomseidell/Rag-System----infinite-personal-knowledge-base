class StorageException(Exception):
    def __init__(self, operation):
        self.operation = operation
        self.message = f"Storage operation: {self.operation} failed"
        super().__init__(self.message)