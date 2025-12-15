class DocumentException(Exception):
    pass

class DocumentNotFoundException(DocumentException):
    def __init__(self, identifier:str):
        self.identifier = identifier
        self.message = f"Document not found: {identifier}"
        super().__init__(self.message) # wird weitergeleited zu Exception init

class DocumentAlreadyExistsException(DocumentException):
    def __init__(self, identifier:str):
        self.identifier = identifier
        self.message = f"document already exists: {identifier}"
        super().__init__(self.message)


