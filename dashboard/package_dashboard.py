"""Create the deployable static Dashboard bundle without build dependencies."""
from pathlib import Path
import hashlib, json, zipfile

root=Path(__file__).resolve().parent
target=root.parent/'outputs/ubon-2026-10-02/UBON-FLOW-Dashboard.zip'
target.parent.mkdir(parents=True,exist_ok=True)
files=[root/n for n in ['index.html','styles.css','app.js','favicon.svg','vercel.json','package.json','README.md']]
files+=sorted((root/'assets').glob('*'))
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(root).as_posix())
    z.writestr('SHA256SUMS.txt','\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix() for p in files)+'\n')
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
print(json.dumps({'path':str(target),'bytes':target.stat().st_size,'files':len(files)+1},ensure_ascii=False))
