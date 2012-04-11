#!/usr/bin/env python2
# coding: utf-8

import os, os.path as path
from contextlib import closing
from itertools import chain
import argparse
import conf

conf.packages_file = path.normpath(path.join(path.dirname(__file__), path.expanduser(conf.packages_file)))
conf.backup_file = path.normpath(path.join(path.dirname(__file__), path.expanduser(conf.backup_file)))

def install(packages):
  print("installing %s packages" % len(packages))
  print(packages)
  cmd = conf.install_command % " ".join(packages)
  return os.system(cmd) == 0

def remove(packages):
  print("removing %s packages" % len(packages))
  print(packages)
  cmd = conf.remove_command % " ".join(packages)
  return os.system(cmd) == 0

def parse(filepath):
  with closing(open(filepath, 'r')) as f:
    lines = f.readlines()

  # remove end-of-line comments and useless blanks
  lines = [l.split(conf.comment_char, 1)[0].strip() for l in lines]

  # split lines with several package names
  lines = chain(*(l.split() for l in lines))

  # return all non-empty lines
  packages = set(l for l in lines if len(l) > 0)
  return packages

def backup(packages):
  with closing(open(conf.backup_file, 'w')) as f:
    f.write("## This file is automatically edited.\n"\
            "## You may want to edit %s\n\n" % conf.packages_file)
    f.write('\n'.join(packages))

def sync():
  currents = parse(conf.packages_file)
  olds = parse(conf.backup_file)

  to_remove = list(olds.difference(currents))
  to_remove.sort()
  to_install = list(currents.difference(olds))
  to_install.sort()

  remove_ok = True
  install_ok = True

  if len(to_remove) > 0:
    remove_ok = remove(to_remove)
  if len(to_install) > 0 and remove_ok:
    install_ok = install(to_install)
  if remove_ok and install_ok:
    backup(currents)
  else:
    if not remove_ok:
      print("ERROR: an error occured while removing.")
    if not install_ok:
      print("ERROR: an error occured while installing.")
    print("You can check your package file's consistency manually by having a look at %s" % conf.packages_file)

def edit():
  os.system(conf.edit_command % conf.packages_file)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Help managing packages')
  parser.add_argument('command', metavar='command', choices=['sync', 'edit'], help="Either `sync` or `edit`")
  args = parser.parse_args()
  if args.command == 'sync':
    sync()
  elif args.command == 'edit':
    edit()
