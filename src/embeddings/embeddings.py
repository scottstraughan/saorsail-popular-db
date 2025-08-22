import json
import logging

from sentence_transformers import SentenceTransformer


class Embeddings:
    def __init__(
        self,
        source_repository_file_path: str,
        target_file_path: str,
        model='all-MiniLM-L6-v2'
    ):
        """
        Embeddings generator.
        """
        self.source_repository_file_path = source_repository_file_path
        self.target_file_path = target_file_path
        self.model = model

    def generate(
        self
    ):
        """
        Generate embeddings for a repository.json file and write it to another json file.
        """
        packages = []

        with open(self.source_repository_file_path, mode='r') as file:
            contents = file.read()
            contents = json.loads(contents)

            for packageName in contents['packages']:
                locale = 'en-US'
                metadata = contents['packages'][packageName]['metadata']

                title = contents['packages'][packageName]['metadata']['name']['en-US']
                description = ''

                if 'description' in metadata and locale in metadata['description']:
                    description = metadata['description'][locale]

                packages.append({
                    'namespace': packageName,
                    'search': title + ' - ' + description,
                    'embedding': None
                })

        logging.info(f"Converted {len(packages)} packages")

        model = SentenceTransformer(self.model)
        texts = [package['search'] for package in packages]
        embeddings = model.encode(texts)

        # Add embeddings to each object
        for i, obj in enumerate(packages):
            obj['embedding'] = embeddings[i]

        Embeddings.__save_as_json(packages, self.target_file_path)

    @staticmethod
    def __save_as_json(
        objects: list,
        filename: str
    ):
        """
        Save embeddings to a json file, formatting the numpy arrays.
        """
        json_objects = []
        for obj in objects:
            json_obj = obj.copy()
            if 'embedding' in json_obj:
                json_obj['embedding'] = json_obj['embedding'].tolist()

            json_objects.append(json_obj)

        with open(filename, 'w') as f:
            json.dump(json_objects, f)

        logging.info(f'Saved as JSON: {filename}')

        return json_objects
