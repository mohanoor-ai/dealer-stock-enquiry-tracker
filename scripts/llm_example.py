"""Safe optional model call. Default is an offline teaching response."""
import argparse
import json
import os
from urllib.request import Request, urlopen


def ask_llm(question, live=False):
    if not live:
        return 'OFFLINE DEMONSTRATION (not model output): An API is an agreed way for programs to request and return information.'
    model = os.environ.get('OLLAMA_MODEL')
    if not model:
        raise ValueError('Set OLLAMA_MODEL to a model already installed in local Ollama.')
    payload = {'model':model,'prompt':question,'stream':False,'options':{'num_predict':200}}
    request = Request('http://127.0.0.1:11434/api/generate',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urlopen(request,timeout=60) as response:
        result = json.load(response)
    return result['response']

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true')
    args=parser.parse_args()
    try:
        print(ask_llm('Explain an API in simple English.',args.live))
    except (ValueError,OSError,KeyError) as error:
        raise SystemExit(f'Model call failed: {error}')
