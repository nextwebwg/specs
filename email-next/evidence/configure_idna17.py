"""Record explicit local ICU library/data pins; does not install dependencies."""
import argparse,hashlib,json
from pathlib import Path
from unicode17_provider import ICU17,isolated_idna

def configure(library,data_library,destination):
    library=Path(library).resolve(strict=True);data_library=Path(data_library).resolve(strict=True)
    root=Path(__file__).resolve().parent/'vendor_idna17'
    cfg={'library':str(library),'libraries':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [library,data_library]},'idna_root':str(root),'idna_files':json.loads((root/'source-hashes.json').read_text())}
    p=ICU17(cfg);isolated_idna(p,cfg)
    Path(destination).write_text(json.dumps(cfg,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--library',required=True);p.add_argument('--data-library',required=True);p.add_argument('--output',required=True);a=p.parse_args();configure(a.library,a.data_library,a.output)
