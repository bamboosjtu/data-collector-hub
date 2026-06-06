"""Extract field lists from sample batch files for tables.yaml."""
import json, sys, os

BATCHES = r"c:\Users\theTruth\Documents\projects\vibe-demo\downloader-dcp\tests\outputs"

def load_batch(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def infer_type(values):
    """Infer column type from a list of non-None values."""
    types = set()
    for v in values:
        if isinstance(v, bool):
            types.add("integer")
        elif isinstance(v, int):
            types.add("integer")
        elif isinstance(v, float):
            types.add("number")
        elif isinstance(v, (list, dict)):
            types.add("json")
        elif isinstance(v, str):
            types.add("string")
    if not types:
        return "string"
    if types == {"integer"}:
        return "integer"
    if types == {"number"}:
        return "number"
    if types == {"integer", "number"}:
        return "number"
    if "json" in types:
        return "json"
    return "string"

SKIP_FIELDS = {"extra", "traceId", "children", "singleList"}

def analyze_rows(rows, prefix=""):
    """Analyze rows and return {field: (type, nullable)} dict."""
    field_values = {}
    field_nulls = {}
    total = len(rows)
    for row in rows:
        for k, v in row.items():
            if k in SKIP_FIELDS:
                continue
            if k not in field_values:
                field_values[k] = []
                field_nulls[k] = 0
            if v is None:
                field_nulls[k] += 1
            else:
                field_values[k].append(v)
    result = {}
    for k in sorted(field_values.keys()):
        non_null = field_values[k]
        t = infer_type(non_null) if non_null else "string"
        nullable = field_nulls[k] > 0
        result[k] = (t, nullable)
    return result

def yaml_columns(fields, pk_fields=None):
    """Generate YAML column definitions."""
    pk_fields = pk_fields or []
    lines = []
    for name, (typ, nullable) in sorted(fields.items()):
        n = "false" if name in pk_fields else ("true" if nullable else "false")
        lines.append(f"      {name}: {{type: {typ}, nullable: {n}}}")
    return "\n".join(lines)

# 1. plan_sgcc_year - project level
print("=" * 60)
print("dcp_plan_projects (from plan_sgcc_year raw top-level)")
print("=" * 60)
data = load_batch(os.path.join(BATCHES, "job_real_sgcc_year_current_41d69538", "batches", "001_plan_sgcc_year.json"))
raw_rows = []
for row in data["tables"][0]["rows"]:
    raw = row.get("raw", {})
    raw_rows.append(raw)
fields = analyze_rows(raw_rows)
pk = ["year", "prjCode"]
# Add year from scope
fields_with_year = {"year": ("string", False), **fields}
print(yaml_columns(fields_with_year, pk))
print(f"\n# Total fields: {len(fields_with_year)}")

# 2. plan_sgcc_year - single project level
print("\n" + "=" * 60)
print("dcp_plan_single_projects (from plan_sgcc_year singleList)")
print("=" * 60)
single_rows = []
for row in data["tables"][0]["rows"]:
    raw = row.get("raw", {})
    for item in raw.get("singleList", []):
        single_rows.append(item)
fields = analyze_rows(single_rows)
pk = ["year", "singleProjectCode"]
fields_with_year = {"year": ("string", False), **fields}
print(yaml_columns(fields_with_year, pk))
print(f"\n# Total fields: {len(fields_with_year)}")

# 3. plan_progress - three levels
print("\n" + "=" * 60)
print("plan_progress - three levels")
print("=" * 60)
data = load_batch(os.path.join(BATCHES, "job_real_progress_43ceede9", "batches", "001_plan_progress.json"))

def flatten_progress(rows):
    """Recursively flatten children, yielding (type, row) tuples."""
    for row in rows:
        raw = row.get("raw", {})
        yield raw.get("type"), raw
        for child in raw.get("children", []):
            yield from flatten_progress([{"raw": child}])

type1_rows, type2_rows, type3_rows = [], [], []
for row in data["tables"][0]["rows"]:
    raw = row.get("raw", {})
    t = raw.get("type")
    if t == 1:
        type1_rows.append(raw)
    elif t == 2:
        type2_rows.append(raw)
    elif t == 3:
        type3_rows.append(raw)
    for child in raw.get("children", []):
        ct = child.get("type")
        if ct == 2:
            type2_rows.append(child)
        elif ct == 3:
            type3_rows.append(child)
        for grandchild in child.get("children", []):
            type3_rows.append(grandchild)

print(f"type=1: {len(type1_rows)}, type=2: {len(type2_rows)}, type=3: {len(type3_rows)}")

# Type 1 - project progress
print("\n--- dcp_plan_project_progress (type=1) ---")
fields1 = analyze_rows(type1_rows)
pk1 = ["prjCode"]
print(yaml_columns(fields1, pk1))
print(f"# Total fields: {len(fields1)}")

# Type 2 - single project progress
print("\n--- dcp_plan_single_project_progress (type=2) ---")
fields2 = analyze_rows(type2_rows)
pk2 = ["singleProjectCode"]
print(yaml_columns(fields2, pk2))
print(f"# Total fields: {len(fields2)}")

# Type 3 - bidding section progress
print("\n--- dcp_plan_bidding_section_progress (type=3) ---")
fields3 = analyze_rows(type3_rows)
pk3 = ["biddingSectionCode"]
print(yaml_columns(fields3, pk3))
print(f"# Total fields: {len(fields3)}")

# 4. plan_dept_key_personnel
print("\n" + "=" * 60)
print("dcp_plan_dept_key_personnel")
print("=" * 60)
data = load_batch(os.path.join(BATCHES, "job_real_dept_key_personnel_d586d692", "batches", "001_plan_dept_key_personnel.json"))
raw_rows = []
for row in data["tables"][0]["rows"]:
    raw = row.get("raw", {})
    raw_rows.append(raw)
fields = analyze_rows(raw_rows)
pk = ["originalIdCard", "positionCode"]
print(yaml_columns(fields, pk))
print(f"# Total fields: {len(fields)}")
