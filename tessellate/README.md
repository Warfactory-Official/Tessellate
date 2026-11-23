# Tessellate patch set: ColinVaughn/Tessellate
- Base: `c7132ea8b956e609889cca4638185bb469510469` (tag v1.2.13)
- Patches (apply in order): `0001-tessellate-worker-chunk-read-survives-ticket-drop.patch` 
- Apply: `bash tessellate/apply.sh <checkout at base>` = `git apply --3way` each, fail hard
- Build: `bash ./gradlew :neoforge:remapJar -x test --no-daemon` (JDK 21); `tessellate/finalize.py` appends "Patched for Tessellate async region ticking." to description, jar -> `<name>-tessellate.jar`; modId/version untouched
- Maven: `com.wf.tessellate:tessellate-neoforge-c2me:<modVersion>-SNAPSHOT` @ https://repo.warfactory.co/snapshots (secrets WARFACTORY_MAVEN_USER/TOKEN)
- CI: `.github/workflows/tessellate-patched.yml`
