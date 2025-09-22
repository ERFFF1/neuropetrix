from jinja2 import Template
from pathlib import Path
import argparse, json

TEMPLATE = (Path(__file__).parent / "assets" / "report_template.md").read_text()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patient_hash", required=True)
    ap.add_argument("--study_uid", required=True)
    ap.add_argument("--suggestion", required=True)
    ap.add_argument("--notes", default="")
    ap.add_argument("--out", default="report.md")
    args = ap.parse_args()
    md = Template(TEMPLATE).render(
        patient_hash=args.patient_hash,
        study_uid=args.study_uid,
        suggestion=args.suggestion,
        notes=args.notes
    )
    Path(args.out).write_text(md)
    print(f"Rapor yazıldı: {args.out}")

if __name__ == "__main__":
    main()
