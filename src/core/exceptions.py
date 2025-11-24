class DatabaseException(Exception):
    def __init__(self, operation:str, detail:str):
        self.operation = operation
        self.detail = detail
        self.message = f"Database error occured in: {self.operation}"
        super().__init__(self.message)
        