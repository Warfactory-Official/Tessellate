#!/usr/bin/env bash
# publish.sh OUTDIR GROUP ARTIFACT: PUT jar+pom to Warfactory snapshots (Gradle maven layout, version = mod version + -SNAPSHOT)
set -euo pipefail
OUT=$1 GROUP=$2 ART=$3
. "$OUT/coords.env"
if [ -z "${WARFACTORY_MAVEN_USER:-}" ] || [ -z "${WARFACTORY_MAVEN_TOKEN:-}" ]; then
  echo "::notice::WARFACTORY_MAVEN_USER/WARFACTORY_MAVEN_TOKEN unset: publish skipped, jar only uploaded as workflow artifact"
  exit 0
fi
V="${MOD_VERSION}-SNAPSHOT"
BASE="https://repo.warfactory.co/snapshots/${GROUP//.//}/$ART/$V"
cat > "$OUT/$ART-$V.pom" <<POM
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>
<groupId>$GROUP</groupId><artifactId>$ART</artifactId><version>$V</version><packaging>jar</packaging></project>
POM
put() { curl -fsS --retry 3 -u "$WARFACTORY_MAVEN_USER:$WARFACTORY_MAVEN_TOKEN" -X PUT --upload-file "$1" "$2" >/dev/null; }
put "$OUT/$OUT_JAR" "$BASE/$ART-$V.jar"
put "$OUT/$ART-$V.pom" "$BASE/$ART-$V.pom"
echo "published $GROUP:$ART:$V"
