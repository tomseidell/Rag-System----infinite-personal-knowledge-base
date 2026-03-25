class OpenaiException(Exception):
    def __init__(self, operation: str, detail: str):
        self.operation = operation
        self.detail = detail
        super().__init__(f"LLM {operation} failed: {detail}")
