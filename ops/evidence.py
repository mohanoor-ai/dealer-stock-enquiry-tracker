"""Fixed read-only incident evidence. No caller-supplied commands or SQL."""
import json
import os
from urllib.request import urlopen


def collect():
    # URL is an operator configuration, not a model argument. Only /health is queried.
    origin=os.environ.get('DEALER_ORIGIN','http://127.0.0.1:8090').rstrip('/')
    try:
        with urlopen(origin+'/health',timeout=5) as response:
            health=json.load(response)
    except Exception:
        health={'status':'unavailable'}
    return {'observed':{'health':health},'proposal': 'Inspect release and database readiness using approved tools' if health.get('status')!='ok' else 'No remediation proposed', 'executed_changes':[]}


if __name__=='__main__':print(json.dumps(collect(),indent=2))
