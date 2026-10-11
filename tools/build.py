#!/usr/bin/env python3
"""Build one app (or all) from apps/<Repo> with Gradle: tools/build.py [Repo ...]
Applies the small build fixes listed in apps.json (the standalone Gradle builds of some Lineage apps need them), runs
`./gradlew assembleRelease` and copies the unsigned APK to out/<package>-unsigned.apk. Needs JDK 17 and ANDROID_HOME (platforms 34 and 35,
build-tools 34)."""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = json.loads((ROOT / "apps.json").read_text())


def build(app):
    d = ROOT / "apps" / app["repo"]
    if not (d / "gradlew").exists():
        sys.exit(f"{d} is empty: git submodule update --init --recursive")
    (d / "local.properties").write_text(f"sdk.dir={os.environ['ANDROID_HOME']}\n")
    for rel, content in app.get("files", {}).items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True); (d / rel).write_text(content)
    for rel, old, new in app.get("replace", []):
        f = d / rel; f.write_text(f.read_text().replace(old, new))
    subprocess.run(["./gradlew", "assembleRelease", "--no-daemon", "-q"], cwd=d, check=True)
    out = ROOT / "out"; out.mkdir(exist_ok=True)
    shutil.copy(d / app["apk"], out / f"{app['package']}-unsigned.apk")
    print(f"built {app['package']}")


if __name__ == "__main__":
    want = sys.argv[1:] or [a["repo"] for a in APPS]
    for a in APPS:
        if a["repo"] in want:
            build(a)
