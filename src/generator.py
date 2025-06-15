import json
import logging
import threading
import time
import requests

from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from src import RepositoryApplication
from src.services import RateLimited, SkippableError
from src.services.github import GitHubService
from src.services.gitlab import GitLabService


class Generator:
    def __init__(
        self,
        database_url: str,
        debug: bool = False
    ):
        self.database_url = database_url
        self.debug = debug
        self.github_service = GitHubService()
        self.gitlab_service = GitLabService()

        self.worker_pool_chunk_size = 20
        self.lock = threading.Lock()
        self.sleep_time_between_chunk = 2  # Seconds
        self.total_work_items = 0
        self.current_work_items = 0

    def build(
        self,
        target_file: str
    ):
        # Fetch the latest database from F-Droid
        database = self.fetch_latest_database()

        # Convert into PopularApplications
        apps = self.convert_apps(database['packages'].items())

        # Inject stars using the service backend
        apps = self.inject_stars(apps)

        # Export the apps to the database
        self.save_to_file(target_file, self.serialize_apps(apps))

    def convert_apps(
        self,
        apps: [any]
    ) -> [RepositoryApplication]:
        converted = []

        for namespace, application in apps:
            app = RepositoryApplication(namespace, application)
            converted.append(app)

        return converted

    def process_application(
        self,
        app: RepositoryApplication
    ) -> RepositoryApplication:
        self.lock.acquire()
        self.current_work_items += 1
        log_app_count = f'({self.current_work_items}/{self.total_work_items})'
        self.lock.release()

        try:
            if not app.has_service():
                logging.info(f'{log_app_count} Skipped {app.namespace} as it does not have a valid repo service.')
                return app

            if app.is_github():
                app.stars = self.github_service.get_stars(app.api_url)
            elif app.is_gitlab():
                app.stars = self.gitlab_service.get_stars(app.api_url)

            logging.info(f'{log_app_count} Processed {app.namespace} from {app.source_code_service}...')
        except SkippableError as e:
            logging.warning(e)
        except RateLimited as e:
            logging.error(e)
            raise e
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise e

        return app

    def inject_stars(
        self,
        apps: [RepositoryApplication]
    ) -> [RepositoryApplication]:
        self.total_work_items = len(apps)
        self.current_work_items = 0

        processed = []
        for chunk in Generator.chunks(apps, self.worker_pool_chunk_size):
            # Convert a list of file paths into a list of markdown files, async chunked work
            processed = processed + Generator.parallel_work(
                chunk, self.process_application)

            logging.info(f'Sleeping for {self.sleep_time_between_chunk} seconds...')
            time.sleep(self.sleep_time_between_chunk)

        return processed

    def serialize_apps(
        self,
        apps: [RepositoryApplication]
    ):
        serialized = {}

        for app in apps:
            serialized = {**serialized, **app.to_dict()}

        return json.dumps(serialized, indent=2 if self.debug else 0)

    def fetch_latest_database(
        self
    ) -> any:
        response = requests.get(
            self.database_url, headers={'accept': 'application/json'})

        return json.loads(response.content)

    @staticmethod
    def parallel_work(
        work_items: list,
        process_list_fn: Callable
    ) -> list:
        """
        This function takes a list of work items, chunks them into lists of a specified size and then
        calls a process callback function over each of those chunks. This function allows you to run chunks of work
        in parallel. The function will then await completion of all the work chunks and return the processed list.
        """
        with ThreadPoolExecutor() as ex:
            futures = [ex.submit(process_list_fn, work_item) for work_item in work_items]

        return [future.result() for future in futures]

    @staticmethod
    def chunks(lst: list, n: int):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @staticmethod
    def save_to_file(
        target_file_path: str,
        contents: any
    ):
        logging.info(f'Wrote db to {target_file_path}')

        with open(target_file_path, 'w') as handler:
            handler.write(contents)
