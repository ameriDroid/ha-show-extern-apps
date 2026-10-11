#!/usr/bin/env python3
"""Sign out/<package>-unsigned.apk with the ameriDroid extern-apps key: tools/sign.py [Repo ...]
The key comes from the environment: EXTERN_KEYSTORE_B64 (base64 of the PKCS#12 file, a GitHub Actions secret) or EXTERN_KEYSTORE_FILE
(a path, for local builds), plus EXTERN_KEYSTORE_PASSWORD or EXTERN_KEYSTORE_PASSWORD_FILE. Without a key (pull requests from forks get no
secrets) nothing is signed and the exit status is 0, so the workflow still builds."""
import base64, glob, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = json.loads((ROOT / "apps.json").read_text())


def main():
    ks = os.environ.get("EXTERN_KEYSTORE_FILE")
    tmp = None
    if not ks and os.environ.get("EXTERN_KEYSTORE_B64"):
        tmp = tempfile.NamedTemporaryFile(suffix=".p12", delete=False)
        tmp.write(base64.b64decode(os.environ["EXTERN_KEYSTORE_B64"])); tmp.close(); ks = tmp.name
    pw = os.environ.get("EXTERN_KEYSTORE_PASSWORD")
    if not pw and os.environ.get("EXTERN_KEYSTORE_PASSWORD_FILE"):
        pw = Path(os.environ["EXTERN_KEYSTORE_PASSWORD_FILE"]).read_text().strip()
    if not ks or not pw:
        print("no signing key available: leaving the APKs unsigned"); return
    apksigner = sorted(glob.glob(f"{os.environ['ANDROID_HOME']}/build-tools/*/apksigner"))[-1]
    want = sys.argv[1:] or [a["repo"] for a in APPS]
    (ROOT / "out" / "signed").mkdir(parents=True, exist_ok=True)
    try:
        for a in APPS:
            if a["repo"] not in want: continue
            src = ROOT / "out" / f"{a['package']}-unsigned.apk"
            if not src.exists():
                sys.exit(f"{src.name} is missing: build {a['repo']} first")
            dst = ROOT / "out" / "signed" / f"{a['package']}.apk"
            subprocess.run([apksigner, "sign", "--ks", ks, "--ks-pass", "env:EXTERN_KS_PASS", "--out", str(dst), str(src)], check=True,
                           env={**os.environ, "EXTERN_KS_PASS": pw})        # env, not argv: failures print the command
            subprocess.run([apksigner, "verify", str(dst)], check=True)
            print(f"signed {a['package']}")
    finally:
        if tmp: os.unlink(tmp.name)


if __name__ == "__main__":
    main()
