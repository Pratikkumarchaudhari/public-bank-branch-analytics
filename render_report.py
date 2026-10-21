"""Render the branch analysis and growth audit into a standalone HTML report."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def write_report(summary):
    data=json.dumps(summary,ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
    template=(ROOT/'report_template.html').read_text(encoding='utf-8')
    text=template.replace('__BRANCH_SCRIPT__',(ROOT/'dashboard.js').read_text(encoding='utf-8'),1).replace('__BRANCH_DATA__',data,1)
    (ROOT/'report.html').write_text(text,encoding='utf-8')
    return text

if __name__=='__main__':write_report(json.loads((ROOT/'outputs/summary.json').read_text()))
