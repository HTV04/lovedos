#!/usr/bin/env python3
import os, sys, shutil, re, textwrap

COMPILER    = "~/djgpp/bin/i586-pc-msdosdjgpp-gcc"
SRC_DIR     = "src"
BIN_DIR     = "bin"
BIN_NAME    = "love.exe"
EMBED_DIR   = "src/embed"
TEMPSRC_DIR = ".tempsrc"

CFLAGS    = [ "-O2", "-Wall", "-s", "-Wno-misleading-indentation" ]
DLIBS     = [ "m" ]
DEFINES   = [ "DMT_ABORT_NULL", "LUA_COMPAT_ALL" ]
INCLUDES  = [ "src", TEMPSRC_DIR ]


def fmt(fmt, var):
  for k in var:
    fmt = fmt.replace("{%s}" % str(k), var[k])
  return fmt


def listdir(path):
  return [os.path.join(dp, f) for dp, dn, fn in os.walk(path) for f in fn]


def make_c_include(name, data):
    name = re.sub("[^a-z0-9]", "_", name.lower())
    res = "static const char " + name + "[] = {"
    for c in data:
        res += str(c) + ", "
    res = res.rstrip(", ") + "};"
    return name, textwrap.fill(res, width=79)


def main():
  os.chdir(sys.path[0])

  if not os.path.exists(BIN_DIR):
    os.makedirs(BIN_DIR)

  if not os.path.exists(TEMPSRC_DIR):
    os.makedirs(TEMPSRC_DIR)

  embedded_files = listdir(EMBED_DIR)

  for filename in embedded_files:
    name = os.path.basename(filename)
    name, text = make_c_include(name, open(filename, "rb").read())
    open("%s/%s.h" % (TEMPSRC_DIR, name), "w").write(text)

  cfiles = [x for x in listdir(SRC_DIR) if x.endswith((".c", ".C"))]

  cmd = fmt(
    "{compiler} {flags} {defines} {includes} -o {outfile} {srcfiles} {libs} {argv}",
    {
      "compiler"  : COMPILER,
      "flags"     : " ".join(CFLAGS),
      "defines"   : " ".join(["-D " + x for x in DEFINES]),
      "includes"  : " ".join(["-I " + x for x in INCLUDES]),
      "outfile"   : BIN_DIR + "/" + BIN_NAME,
      "srcfiles"  : " ".join(cfiles),
      "libs"      : " ".join(["-l" + x for x in DLIBS]),
      "argv"      : " ".join(sys.argv[1:])
    })

  print("compiling...")
  res = os.system(cmd)

  print("deleting temporary files...")
  if os.path.exists(TEMPSRC_DIR):
    shutil.rmtree(TEMPSRC_DIR)

  print("done" + (" with errors" if res else ""))



if __name__ == "__main__":
  main()
