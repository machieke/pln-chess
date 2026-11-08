import json,os
from pathlib import Path
Path('/data/pln-chess-cycle8-ui-final/owned-server.json').write_text(json.dumps({'pid':os.getpid(),'pgid':os.getpgrp(),'token':'c13f0f3b32f54c2e9725c213136cee65'}))
os.execv('/data/pln-chess-cycle6-delivery/.venv/bin/python',['/data/pln-chess-cycle6-delivery/.venv/bin/python', '-m', 'pln_chess', 'serve', '--checkpoint', '/data/pln-chess-cycle8-clean-output/model/C8-default.json', '--port', '18769'])
