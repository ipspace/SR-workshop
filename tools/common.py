#!/usr/bin/env python3
#
import argparse
import io
import sys
import typing
import subprocess
import rich.console
from box import Box

def bold(s: str) -> str:
  return f'[bold]{s}[/bold]'

def confirm(s: str, prompt: typing.Optional[str] = None, single_key: bool = False) -> str:
  console = rich.console.Console()
  console.print(s,end="")
  try:
    if single_key:
      print(prompt or ' -> ',end='',flush=True)
      subprocess.run(['stty','cbreak'])
      result = None
      try:
        with io.open(sys.stdin.fileno(), 'rb', closefd=False) as stdin:
          result = stdin.read(1)
      except Exception:
        result = None

      subprocess.run(['stty','sane'])
      print()
      if result is None or result == b'\x04':
        print('Looks like we lost you')
        sys.exit(0)
      return result.decode(sys.stdin.encoding or 'utf-8', errors='ignore')
    else:
      return input(prompt or ' -> ').lower()
  except EOFError:
    print('Bye')
    sys.exit(0)
  except KeyboardInterrupt:
    print('How rude :( Bye')
    subprocess.run(['stty','sane'])               # Just in case we got here from single-key reads
    sys.exit(0)

def confirm_abort(s: str) -> typing.Never:
  confirm(bold(s))
  sys.exit(1)

def fetch_traceback(exc: Exception) -> list:
  loc_list = []
  tb = exc.__traceback__
  while tb:
    f = tb.tb_frame
    loc_txt = f'Line {tb.tb_lineno} @ {f.f_code.co_filename}'
    if loc_txt not in loc_list:
      loc_list.append(loc_txt)
    tb = tb.tb_next

  loc_list.reverse()
  return loc_list

def read_yaml(fname: str) -> Box:
  try:
    return Box.from_yaml(filename=fname,default_box=True,default_box_none_transform=False,box_dots=True)
  except Exception as ex:
    print(f'Cannot read YAML file {fname}: {str(ex)}')
    sys.exit(1)

def read_setup(args: argparse.Namespace) -> Box:
  setup = read_yaml(args.setup)
  if 'session' not in setup:
    setup.session = 'demo'
  if 'shell' not in setup:
    setup.shell = ''

  if 'directory' not in setup:
    confirm_abort('Demo directory not specified in setup')

  return setup
