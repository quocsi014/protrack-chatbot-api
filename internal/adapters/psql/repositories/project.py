from .repo import Repo


class ProjectRepo(Repo):
    def get_member_ids(self, project_id):
        self.cursor.execute(
            "SELECT userId FROM memberships WHERE projectId = %s",
            (project_id,)
        )
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]
