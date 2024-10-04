import json
import subprocess
import time
import uuid
import tempfile
from pathlib import Path
import importlib
from pydantic import BaseModel

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from polyfactory.factories.pydantic_factory import ModelFactory

class Metadata(BaseModel):
    name: str = Field(..., description="The name of the object. Must be a DNS subdomain-compliant string.")

    class Config:
        schema_extra = {
            "required": ["name"]
        }


def build_resource_classes(resource_definitions: list[dict]):
    objects = []
    for resource_definition in resource_definitions:

        spec_schema = resource_definition['spec']['versions'][-1]['schema']

        resource_name = resource_definition['spec']['names']['singular']

        base = {
            "$id": f"{resource_name}.json",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": resource_definition['spec']['names']['kind'],
            **spec_schema
        }

        path = Path('./tmp/schemas').resolve() / f"{resource_name}.json"
        with path.open('w') as tmp_file:
            json.dump(base, tmp_file)

        time.sleep(0.1)
        result = subprocess.run(
            ['datamodel-codegen', '--input', path, '--input-file-type', 'jsonschema', '--output', f'./tmp/models/{resource_name}.py'],
            capture_output=True,
            text=True
        )
        print(result.stderr)

        objects.append({
            'name': resource_name,
            'kind': resource_definition['spec']['names']['kind'],
            'path': path,
            'group': resource_definition['spec']['group'],
            'version': resource_definition['spec']['versions'][-1]['name']
        })

    return objects

def resource_mocker(objects):
    n = 100

    resources = []
    for object in objects:
        module = importlib.import_module(f'tmp.models.{object["name"]}')

        Resource = getattr(module, object['kind'])

        class FullResource(Resource):
            apiVersion: str = Field(default_factory=lambda: f"{object['group']}/{object['version']}")
            kind: str = Field(default_factory=lambda: f"{object['kind']}")
            metadata: Metadata

        class Factory(ModelFactory[FullResource]):
            __model__ = FullResource
            __use_defaults__ = True

        instances = [Factory.build() for _ in range(n)]
        resources.extend(instances)
    return resources

