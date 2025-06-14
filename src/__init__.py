import urllib.parse


class RepositoryApplication:
    def __init__(
        self,
        namespace: str,
        application: any
    ):
        self.namespace = namespace
        self.application = application
        self.source_code_url = self.get_source_code_url()
        self.api_url = RepositoryApplication.get_api_url(self.source_code_url)
        self.source_code_service = 'GitHub' if self.is_github() else 'GitLab' if self.is_gitlab() else None

        self.stars = 0

    def get_source_code_url(
        self
    ) -> str | None:
        if 'sourceCode' not in self.application['metadata']:
            return None

        return self.application['metadata']['sourceCode']

    def is_github(
        self
    ) -> bool:
        if not self.source_code_url:
            return False

        return 'github' in self.source_code_url

    def is_gitlab(
        self
    ) -> bool:
        if not self.source_code_url:
            return False

        return 'gitlab' in self.source_code_url

    def has_service(self):
        return self.is_github() or self.is_gitlab()

    def to_dict(
        self
    ) -> dict:
        return {self.namespace: {
            'stars': self.stars
        }}

    @staticmethod
    def get_api_url(
        source_code_url: str
    ) -> str | None:
        if source_code_url is None:
            return None

        if 'github' in source_code_url:
            return source_code_url.replace('//github.com', '//api.github.com/repos').rstrip('/')

        if 'gitlab' in source_code_url:
            path = source_code_url.replace('https://gitlab.com/', '')
            path = urllib.parse.quote_plus(path)
            return f'https://gitlab.com/api/v4/projects/{path}'

        return None
