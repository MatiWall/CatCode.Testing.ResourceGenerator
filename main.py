import json
import logging
from enum import Enum

from generator.mocker import build_resource_classes, resource_mocker

logger = logging.getLogger(__name__)
import subprocess
from pathlib import Path
import requests
import git
import os
import yaml

from settings import BASE_DIR, config


# Clone the repository
def clone_repo(repo_url, clone_dir: Path):
    if not not clone_dir.exists():
        clone_dir.mkdir(parents=True, exist_ok=True)
    git.Repo.clone_from(repo_url, clone_dir)

def update_repo(clone_dir):
    subprocess.run(['git', 'pull'], cwd=clone_dir)

# Read files from the repository
def read_files(directory):
    objects = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = directory / file
            with file_path.open('r') as f:
                obj = yaml.safe_load(f)

            objects.append(obj)
    return objects

# Custom JSON encoder for Enums
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value  # Serialize enum as its value
        return super().default(obj)

def insert_files_to_etcd(files):

    for file in files: # all logic is left for the CoreAI
        resp = requests.post(
            f"{config.core_api}/resource/v1",
            data=json.dumps(file, cls=EnumEncoder),
            headers={'Content-Type': 'application/json'}
        )

        if resp.status_code == 200:
            logger.info(f'Success fully inserted {file} to etcd with key {resp.json()["key"]}')
        else:
            logger.warning(f'Failed to insert file {file} with error: \n {resp.content}')





# Main function
def main():

    CLONE_REPO = BASE_DIR/ f'clones/'

    try:
        update_repo(CLONE_REPO)
    except:
        clone_repo(
            'https://github.com/MatiWall/CatCode.Catalog.Models.git',
            CLONE_REPO
        )
    files = read_files(CLONE_REPO / 'kinds')

    resources = build_resource_classes(files)
    resources = resource_mocker(resources)

    insert_files_to_etcd([r.model_dump() for r in resources])


if __name__ == "__main__":
    main()