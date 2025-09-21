from pathlib import Path
import yaml

SEV_LOW, SEV_MED, SEV_HIGH = "LOW", "MEDIUM", "HIGH"

def _load_rules():
    data = yaml.safe_load(Path("config/rules.yaml").read_text(encoding="utf-8"))
    return {
        "deny_ports": set(data.get("deny_ports", [])),
        "min_versions": data.get("min_versions", {}),
        "tls": data.get("tls", {}),
    }

def version_is_outdated(product: str, version: str, min_required: str) -> bool:
    # comparación simple por string; suficiente para demo
    if not version or not min_required:
        return False
    return str(version).strip() < str(min_required).strip()

def evaluate(findings):
    """
    Marca hallazgos según reglas simples.
    """
    rules = _load_rules()
    evals = []
    for f in findings:
        reasons = []
        severity = None

        # puertos prohibidos
        if f["port"] in rules["deny_ports"]:
            severity = SEV_HIGH
            reasons.append(f"Puerto prohibido {f['port']}")

        # versiones mínimas (ej: ssh/OpenSSH)
        if f["service"] == "ssh":
            min_ssh = rules["min_versions"].get("ssh")
            if min_ssh and version_is_outdated("ssh", f.get("product","") + "_" + f.get("version",""), min_ssh):
                severity = severity or SEV_MED
                reasons.append(f"SSH por debajo de {min_ssh}")

        # TLS viejo (heurística: si el producto/versión contiene 'SSL' o 'TLS1.0/1.1')
        if f["service"] in ("https","ssl","http"):
            forbid = set(rules["tls"].get("forbid_protocols", []))
            txt = (f.get("product","") + " " + f.get("version","")).upper()
            if any(proto.upper() in txt for proto in forbid):
                severity = severity or SEV_MED
                reasons.append("Protocolos TLS inseguros detectados")

        if reasons:
            f = dict(f)  # copia
            f["severity"] = severity
            f["reasons"] = reasons
            evals.append(f)
    return evals
