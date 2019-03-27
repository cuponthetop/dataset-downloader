from typing import Dict, Union
from logging import getLogger

logger = getLogger(__name__)


# This function will NOT work with JSON containing . as a part of attribute key
def json_accessor(json: Dict, key: str) -> Union[Dict, int, float, str]:
    if not key:
        return json

    keys = key.split('.')
    temp_json = json
    for key in keys:
        try:
            if isinstance(temp_json, dict):
                temp_json = temp_json[key]
            elif isinstance(temp_json, list):
                temp_json = temp_json[int(key)]
            else:
                raise Exception('json is not instance of dict or list, {json}'.format(json=temp_json))
        except KeyError as e:
            logger.warning("Unable to find attribute {key} in JSON {json}".format(key=key, json=json))
            raise e
        except IndexError as e:
            logger.warning("Unable to find list element at {key} in JSON {json}".format(key=key, json=json))
            raise e
    return temp_json
