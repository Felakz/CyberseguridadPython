import time
import yaml
from pathlib import Path
import nmap

def _load_targets():
    cfg = yaml.safe_load(Path("config/targets.yaml").read_text(encoding="utf-8"))
    return cfg.get("targets", [])

def expand_targets():
    """Devuelve lista de cadenas a escanear (CIDR o IPs)."""
    targets = _load_targets()
    out = []
    for t in targets:
        if "cidr" in t:
            out.append(t["cidr"])
        elif "host" in t:
            out.append(t["host"])
    return out

def run_scan():
    nm = nmap.PortScanner()
    results = []
    scan_targets = expand_targets()
    if not scan_targets:
        return {"ts": int(time.time()), "findings": results}

    target_str = " ".join(scan_targets)
    # -sV: detectar versión; -O: SO (puede requerir permisos); -T4: más rápido
    nm.scan(hosts=target_str, arguments="-sV -T4")
    ts = int(time.time())

    for host in nm.all_hosts():
        if "tcp" not in nm[host]:
            continue
        for port, pdata in nm[host]["tcp"].items():
            if pdata.get("state") != "open":
                continue
            service = pdata.get("name", "")
            product = pdata.get("product", "")
            version = pdata.get("version", "")
            results.append({
                "host": host,
                "port": port,
                "service": service,
                "product": product,
                "version": version,
                "env": "lab"
            })
    return {"ts": ts, "findings": results}
