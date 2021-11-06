import json
import urllib.parse
import urllib.request
from typing import Dict, List, IO

from chalicelib.environment import read_environ_var

boundary = '--------python'


token = read_environ_var('SLACK_BOT_TOKEN')


def post_text_to_slack(channel: str, text: str) -> None:
    req = urllib.request.Request('https://slack.com/api/chat.postMessage')
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    data = {
        'channel': channel,
        'text': text,
    }
    with urllib.request.urlopen(req, json.dumps(data).encode()) as res:
        json_dict = json.load(res)
        print(json_dict)


def post_image_to_slack(channel: str, png_file: IO[bytes]) -> None:
    req = urllib.request.Request('https://slack.com/api/files.upload')
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    data = multipart_form_data({'initial_comment': 'Done!', 'channels': channel, 'filetype': 'png'}, [png_file.name])
    with urllib.request.urlopen(req, data) as res:
        json_dict = json.load(res)
        print(json_dict)


def multipart_form_data(original_data: Dict[str, str], file_name_list: List[str]) -> bytes:
    value = b''
    for key, data in original_data.items():
        value += f'''
--{boundary}
Content-Disposition: form-data; name="{key}"

{data}
'''.encode()
    for file_name in file_name_list:
        with open(file_name, 'rb') as f:
            byte_data = f.read()
        value += f'''
--{boundary}
Content-Disposition: form-data; name="file"; filename="{file_name}"
Content-Type: image/png

'''.encode() + byte_data + f'''

--{boundary}'''.encode()
    value += b'--\n'
    return value[1:]
