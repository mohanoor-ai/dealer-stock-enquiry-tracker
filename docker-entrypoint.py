import os
import uvicorn
uvicorn.run('backend_v2.app:app',host='0.0.0.0',port=int(os.environ.get('PORT','8090')),access_log=False)
