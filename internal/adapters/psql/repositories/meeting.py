from .repo import Repo
from internal.domains import Meeting


class MeetingRepo(Repo):
    def get_meeting(self, meeting_id):
        self.cursor.execute(
            '''
            SELECT m.id as id, m.call_id as call_id, m.description as  des
            FROM meetings m
            WHERE m.id = %s
            ''',
            (meeting_id,)
        )

        row = self.cursor.fetchone()
        if row:
            id, call_id, des = row
            return Meeting(id, call_id, des)
        else:
            return None
