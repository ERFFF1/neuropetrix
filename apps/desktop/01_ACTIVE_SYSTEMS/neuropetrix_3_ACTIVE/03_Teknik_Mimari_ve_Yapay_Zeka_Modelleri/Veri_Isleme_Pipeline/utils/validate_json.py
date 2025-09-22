import json, sys
from jsonschema import validate, ValidationError
from pathlib import Path

SCHEMA_PATH = Path(__file__).parents[1] / "schema" / "neuroPETrix_case.schema.json"

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python validate_json.py <json_dosyasi>")
        sys.exit(1)
    schema = json.loads(Path(SCHEMA_PATH).read_text())
    for p in sys.argv[1:]:
        data = json.loads(Path(p).read_text())
        try:
            validate(instance=data, schema=schema)
            print(f"[OK] {p}")
        except ValidationError as e:
            print(f"[HATA] {p}: {e.message}")
            sys.exit(2)

if __name__ == "__main__":
    main()
