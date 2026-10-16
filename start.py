import argparse
from pathlib import Path
import os
import uvicorn

if __name__ == '__main__':
    os.chdir(Path(__file__).resolve().parent)
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8090)
    parser.add_argument('--legacy', action='store_true', help='Run the preserved original application')
    args = parser.parse_args()
    print(f'Open in your browser: http://127.0.0.1:{args.port}', flush=True)
    print('Stop with Ctrl+C.', flush=True)
    uvicorn.run('backend.app:app' if args.legacy else 'backend_v2.app:app', host='127.0.0.1', port=args.port)

