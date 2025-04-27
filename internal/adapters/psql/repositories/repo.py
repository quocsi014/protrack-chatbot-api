class Repo:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
