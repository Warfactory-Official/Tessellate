#!/usr/bin/env python3
"""finalize.py JAR MODID OUTDIR: append description sentence to MODID's [[mods]] block, write OUTDIR/<stem>-tessellate.jar + OUTDIR/coords.env. modId/version untouched."""
import re, sys, zipfile, os

SENTENCE = os.environ.get("TESS_SENTENCE", "Patched for Tessellate async region ticking.")
SUFFIX = os.environ.get("TESS_SUFFIX", "tessellate")
TOMLS = ("META-INF/neoforge.mods.toml", "META-INF/mods.toml")


def patch_toml(text, modid):
    blocks = list(re.finditer(r"^\[\[mods\]\][^\n]*$", text, re.M))
    for b in blocks:
        nxt = re.search(r"^\[", text[b.end():], re.M)
        end = b.end() + (nxt.start() if nxt else len(text) - b.end())
        blk = text[b.start():end]
        if not re.search(r"^\s*modId\s*=\s*[\"']%s[\"']" % re.escape(modid), blk, re.M):
            continue
        m = re.search(r"^(\s*description\s*=\s*)('''|\"\"\"|\"|')(.*?)\2", blk, re.M | re.S)
        if m:
            body = m.group(3)
            nb = body.rstrip("\n") + (" " if "\n" not in body else "\n") + SENTENCE + ("\n" if body.endswith("\n") else "")
            new = blk[:m.start(3)] + nb + blk[m.end(3):]
        else:
            new = blk.rstrip("\n") + '\ndescription = "%s"\n\n' % SENTENCE
        ver = re.search(r"^\s*version\s*=\s*[\"']([^\"']*)[\"']", blk, re.M)
        return text[:b.start()] + new + text[end:], (ver.group(1) if ver else None)
    raise SystemExit("modId %s not in toml" % modid)


def main(jar, modid, outdir):
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.basename(jar)[:-4]
    out = os.path.join(outdir, stem + "-" + SUFFIX + ".jar")
    zin = zipfile.ZipFile(jar)
    version = None
    patched = False
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in TOMLS:
                try:
                    t, v = patch_toml(data.decode("utf-8"), modid)
                except SystemExit:
                    t, v = None, None
                if t is not None:
                    patched = True
                    data = t.encode("utf-8")
                    version = version or v
            zout.writestr(item, data)
    if os.environ.get("TESS_MOD_VERSION"):
        version = os.environ["TESS_MOD_VERSION"]
    if not patched:
        raise SystemExit("no mods.toml patched")
    if version is None or version.startswith("${"):
        mf = zin.read("META-INF/MANIFEST.MF").decode()
        m = re.search(r"^Implementation-Version:\s*(\S+)", mf, re.M)
        version = m.group(1) if m else None
    if not version:
        raise SystemExit("no version for %s" % modid)
    with open(os.path.join(outdir, "coords.env"), "w") as f:
        f.write("MOD_VERSION=%s\nOUT_JAR=%s\n" % (version, os.path.basename(out)))
    print(out, version)


main(*sys.argv[1:4])
