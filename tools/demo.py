#!/usr/bin/env python3
#
import argparse
import subprocess

from common import read_setup

def run_demo(args: argparse.Namespace) -> None:
  setup = read_setup(args)

  cmd = ['tmux','new-session','-s',setup.session]
  if setup.shell:
    cmd += [ setup.shell ]
  cmd += [';','set','history-limit','500']
  cmd += [';','setw','-g','mouse','on']
  if setup.status_left:
    status_left = setup.status_left + "  "
    cmd += [';','set','status-left',status_left]
    cmd += [';','set','status-left-length',str(len(status_left))]
  cmd += [';','split-window','-v','-l',str(setup.get('bottom_lines','1'))]
  cmd += ['python3',args.me,'--script',args.demo]

  subprocess.run(cmd)
