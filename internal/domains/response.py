class Response:
    def __init__(self, err: ValueError, data):
        self.is_success = True
        self.err_code = ""
        if err is not None:
            self.is_success = False
            self.err_code = str(err)
        self.data = data
