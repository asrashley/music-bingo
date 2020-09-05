"""
JSON Schema validators for the various JSON file formats used
by musicbingo
"""
import json
from enum import Enum
import pathlib
import sys
from typing import Callable, Dict
from urllib.parse import urlparse

import fastjsonschema  # type: ignore

from musicbingo.assets import Assets
from musicbingo.models.modelmixin import JsonObject

class JsonSchema(Enum):
    """
    Enumeration of available JSON Schemas
    """
    GAME_TRACKS = 'gameTracks.json'
    GAME_TRACKS_V1_V2 = 'gameTracks_v1_v2.json'
    GAME_TRACKS_V3 = 'gameTracks_v3.json'
    GAME_TRACKS_V4 = 'gameTracks_v4.json'
    DATABASE = 'database.json'


json_validators: Dict[str, Callable[[JsonObject], bool]] = {}

def resolve_external_schema(uri: str) -> JsonObject:
    """
    Load an external Schema file from the schemas directory
    """
    parts = urlparse(uri)
    path = pathlib.PurePosixPath(parts.path)
    schema_filename = Assets.get_schema_filename(path.name)
    with schema_filename.open("rt") as src:
        schema_def = json.load(src)
    return schema_def

def validate_json(schema: JsonSchema, data: JsonObject) -> None:
    """
    Check that data conforms the specified JSON Schema.

    Raises
    ------
    fastjsonschema.JsonSchemaException
        if data is not valid
    IOError
        if Schema file cannot be found
    """
    try:
        validate = json_validators[schema.value]
    except KeyError:
        schema_filename = Assets.get_schema_filename(schema.value)
        with schema_filename.open("rt") as src:
            schema_def = json.load(src)
        handlers = {
            'http': resolve_external_schema,
            'https': resolve_external_schema
        }
        validate = fastjsonschema.compile(schema_def, handlers=handlers)
        json_validators[schema.value] = validate
    validate(data)

def main(filename: str) -> None:
    """
    Check every Schema against the specified file
    """
    valid = False
    errors: Dict[JsonSchema, Exception] = {}
    for scheme in JsonSchema:
        try:
            with open(filename) as src:
                data = json.load(src)
            validate_json(scheme, data)
            print(f'{filename}: Valid {scheme.name}')
            valid = True
            break
        except (fastjsonschema.JsonSchemaException, IOError) as err:
            errors[scheme] = err
    if not valid:
        for scheme in JsonSchema:
            serr = errors[scheme]
            if not isinstance(serr, fastjsonschema.JsonSchemaException):
                print(f'{scheme.name}: {serr}')
                continue
            print(f'{scheme.name}: {serr.message}')
            print(f'    {serr.name}: {serr.path}')
            print(f'    {serr.rule}: {serr.rule_definition}')
            print(f'    {serr.definition}')
            print(f'    {serr.value}')

if __name__ == '__main__':
    main(sys.argv[1])
