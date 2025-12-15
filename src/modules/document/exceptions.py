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



#utils
class PDFProcessingException(Exception):
    def __init__(self, detail:str):
        self.detail = detail
        self.message = f"PDF processing failed: {detail}"
        super().__init__(self.message)


class TextSplittingException(Exception):
    def __init__(self,detail:str):
        self.detail = detail
        self.message= f"Splitting text failed: {detail}"
        super().__init__(self.message)
