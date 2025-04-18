class File:
    def __init__(self, file_id, file_name, file=None, contents=[]):
        self.file_id = file_id
        self.file_name = file_name
        self.file = file
        self.contents = contents
