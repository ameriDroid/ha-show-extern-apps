# ha-show-extern-apps

The third-party apps that ship preinstalled on the ameriDroid HA Show image, built from source. Everything here is public.

The apps are the LineageOS ones for Android 14 (`lineage-21.0`), as git submodules under `apps/`:

| App | Source | Package |
|---|---|---|
| Clock | android_packages_apps_DeskClock | `com.android.deskclock` |
| Calculator | android_packages_apps_ExactCalculator | `com.android.calculator2` |
| Voice recorder | android_packages_apps_Recorder | `org.lineageos.recorder` |
| Gallery | android_packages_apps_Glimpse | `org.lineageos.glimpse` |
| Calendar | android_packages_apps_Etar | `ws.xsoh.etar` |
| Browser | android_packages_apps_Jelly | `org.lineageos.jelly` |
| Music | android_packages_apps_Eleven | `org.lineageos.eleven` |

Pinned commits are the submodule pointers. To take newer upstream changes: `git submodule update --remote apps/<Name>`, check the build, commit.
`apps.json` lists the package id, the install directory and the few build fixes the standalone Gradle builds need (Etar).

## Building

```sh
git clone --recursive https://github.com/ameriDroid/ha-show-extern-apps
export ANDROID_HOME=...   # SDK with platforms 34 + 35 and build-tools 34, JDK 17
python3 tools/build.py            # all apps, or: tools/build.py Etar
python3 tools/sign.py             # needs the signing key, see below
python3 tools/manifest.py
```

## GitHub Actions

`.github/workflows/build.yml` builds every app on each push and pull request. A tag `vYYYY.MM.DD` also signs the APKs and publishes a
GitHub Release with the APKs and `out/manifest.json` (package, install directory, upstream commit, sha256), which the image builder
downloads.

Signing uses two **repository secrets**:

| Secret | Value |
|---|---|
| `EXTERN_KEYSTORE_B64` | the PKCS#12 keystore, base64 (`base64 -i hashow-extern.p12`) |
| `EXTERN_KEYSTORE_PASSWORD` | its password |

Pull requests from forks get no secrets: they build, and the APKs stay unsigned. Create an environment named `release` (Settings, Environments)
and add required reviewers if you want a person to approve every publish.

The key is a dedicated one, separate from the keys that sign the private manager and setup apps, because anything that can run the workflow can
use it. Do not reuse it for anything else.

## Licence

This repository holds build scripts only. Each app keeps its own upstream licence (see the submodules).
