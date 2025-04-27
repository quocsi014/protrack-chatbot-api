from .repo import Repo
from internal.domains import File


class FileRepo(Repo):
    def get_file(self, file_id):
        self.cursor.execute(
            '''
            SELECT f.id as id, fp.url as url, f.name as name
            FROM files f
            JOIN file_property_entity fp ON f.id = fp.fileId
            WHERE f.id = %s
            ''',
            (file_id,)
        )

        row = self.cursor.fetchone()
        if row:
            file_id, file_url, file_name = row
            return File(file_id=file_id,
                        file_name=file_name,
                        file_url=file_url)
        else:
            return None

    def update_sync_status(self, status, file_id):
        self.cursor.execute(
            '''
            update files set isSync = %s
            where id = %s
            ''', status, file_id
        )
        self.conn.commit()
