from src.services import Service, SkippableError


class GitLabService(Service):
    API_KEY: str = ''

    def get_stars(
        self,
        url: str
    ) -> int:
        repo_info = self.get_repo_info('GitLab', url, GitLabService.API_KEY)

        if 'star_count' not in repo_info:
            raise SkippableError(f'Could not find "star_count" in repository response.')

        return repo_info['star_count']
