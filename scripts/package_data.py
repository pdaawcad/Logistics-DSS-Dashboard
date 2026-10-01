"""Package the synthetic data and references, with SHA-256 manifest."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[1]
summary = json.loads((root / 'data/summary.json').read_text(encoding='utf-8-sig'))
checks = summary['quality_checks'] if 'quality_checks' in summary else summary['validation_checks']
assert all(c['passed'] for c in checks)
for table, expected in summary['record_counts'].items():
    with (root / 'data' / f'{table}.csv').open(encoding='utf-8-sig', newline='') as f:
        count = sum(1 for _ in csv.DictReader(f))
    assert count == expected, (table, count, expected)
report = ['# ผลตรวจคุณภาพข้อมูลจำลอง', '',
          'ข้อมูลนี้เป็นข้อมูลจำลอง ไม่ใช่ผลการดำเนินงานจริงของบริษัทขนส่ง', '',
          f'ผ่านการตรวจ {len(checks)} เงื่อนไข และจำนวนแถว CSV ตรงกับ summary.json ทุกตาราง', '',
          '| เงื่อนไข | ผล | รายละเอียด |', '|---|---|---|']
report += [f"| {c['check']} | PASS | {c['detail']} |" for c in checks]
(root / 'DATA_QUALITY.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
output = root / 'outputs/ubon-2026-10-02/Logistics-Synthetic-Data.zip'
excluded = {'mot_distance_api.json', 'osrm_chiangmai.json'}
files = sorted(p for p in root.rglob('*') if p.is_file()
               and p.suffix not in {'.zip', '.pyc'}
               and not p.name.endswith('.inspect.ndjson')
               and p.name not in excluded
               and '__pycache__' not in p.parts)
manifest = '\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}' for p in files)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in files:
        z.write(p, p.relative_to(root).as_posix())
    z.writestr('SHA256SUMS.txt', manifest + '\n')
with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
    for p in files:
        assert hashlib.sha256(z.read(p.relative_to(root).as_posix())).digest() == hashlib.sha256(p.read_bytes()).digest()
print(json.dumps({'zip': str(output), 'files': len(files) + 1,
                  'bytes': output.stat().st_size, 'checks_passed': len(checks)}, ensure_ascii=False))
