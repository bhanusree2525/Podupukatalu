import io
import json
import pandas as pd
from typing import List, Dict, Any


def export_to_csv_bytes(rows: List[Dict[str, Any]]) -> bytes:
    df = pd.DataFrame(rows)
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    return csv_buf.getvalue().encode("utf-8")


def export_to_json_bytes(rows: List[Dict[str, Any]]) -> bytes:
    return json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8")
