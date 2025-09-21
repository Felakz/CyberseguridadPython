from collections import defaultdict

def _key(f):
    return f"{f['host']}:{f['port']}:{f.get('service','')}"

def diff_vs_baseline(current_findings, baseline_findings):
    base_map = {_key(f): f for f in baseline_findings}
    changes = []
    for f in current_findings:
        k = _key(f)
        status = "NEW" if k not in base_map else "CHANGED"
        if status == "CHANGED":
            # comparar versión/razones de manera simple
            bf = base_map[k]
            if bf.get("reasons") == f.get("reasons") and bf.get("severity") == f.get("severity"):
                status = "SAME"
        f2 = dict(f)
        f2["status"] = status
        if status != "SAME":
            changes.append(f2)
    return changes
