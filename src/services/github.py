from src.services import Service, SkippableError


class GitHubService(Service):
    API_KEY: str = ''

    def get_stars(
        self,
        url: str
    ) -> int:
        repo_info = self.get_repo_info('GitHub', url, GitHubService.API_KEY)

        if 'stargazers_count' not in repo_info:
            raise SkippableError(f'Could not find "stargazers_count" in repository response.')

        return repo_info['stargazers_count']
