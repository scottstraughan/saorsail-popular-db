import logging
import time
from argparse import ArgumentParser

from src.popular.generator import Generator
from src.popular.services.github import GitHubService
from src.popular.services.gitlab import GitLabService


def load_command_line_args():
    """
    Load the relevant command line arguments
    :return:
    """
    argument_parser = ArgumentParser()

    argument_parser.add_argument('-u',
                                 '--databaseUrl',
                                 dest='database_url',
                                 help='The F-Droid database URL',
                                 required=True)

    argument_parser.add_argument('-f',
                                 '--exportFile',
                                 dest='export_file_path',
                                 help='Export file path',
                                 required=False)

    argument_parser.add_argument('-gh',
                                 '--githubApiKey',
                                 dest='github_api_key',
                                 help='A GitHub API key, used to pull information from API.',
                                 required=False)

    argument_parser.add_argument('-gl',
                                 '--gitlabApiKey',
                                 dest='gitlab_api_key',
                                 help='A GitLab API key, used to pull information from API.',
                                 required=False)

    argument_parser.add_argument('-d',
                                 '--debug',
                                 dest='debug_mode',
                                 help='Enable debug mode, will cause stack trace to print.',
                                 required=False,
                                 default=False,
                                 action='store_true')

    return argument_parser.parse_args()


if __name__ == '__main__':
    debug = False

    try:
        # Parse arguments
        args = load_command_line_args()
        debug = args.debug_mode

        logging.basicConfig(level=logging.INFO)

        file_path = args.export_file_path if args.export_file_path else 'export.json'

        # Set some require attributes
        GitHubService.API_KEY = args.github_api_key
        GitLabService.API_KEY = args.gitlab_api_key

        # Start time
        start_time = round(time.time() * 1000)

        # Vars
        print('Generating repository database....')

        builder = Generator(args.database_url, debug)
        builder.build(file_path)

        # Print success and time took
        time_diff_in_seconds = (round(time.time() * 1000) - start_time) / 1000

        print(f'Success, took {time_diff_in_seconds}s.')
        exit(0)
    except Exception as e:
        if debug:
            raise e

        print('Error: ' + str(e.__str__().encode('ascii', errors='ignore').decode('ascii')))
        exit(1)
