#!/usr/bin/env python3
"""Write out/manifest.json for the signed APKs in out/signed/: package, install directory, upstream commit, sha256 and size.
The image builder (ha-show-img) downloads this file with the APKs from a GitHub Release."""
import hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = {}
for a in json.loads((ROOT / "apps.json").read_text()):
    apk = ROOT / "out" / "signed" / f"{a['package']}.apk"
    if not apk.exists():
        continue
    commit = subprocess.run(["git", "-C", str(ROOT / "apps" / a["repo"]), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    data = apk.read_bytes()
    out[a["package"]] = {"dir": a["dir"], "file": apk.name, "source": f"LineageOS/android_packages_apps_{a['repo']}@lineage-21.0",
                         "commit": commit, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
(ROOT / "out" / "manifest.json").write_text(json.dumps(out, indent=2) + "\n")
print(f"manifest: {len(out)} apps")
