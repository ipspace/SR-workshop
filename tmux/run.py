#!/usr/bin/env python3
#
import argparse
import time
import sys
import typing
import subprocess
import rich.console
from box import Box

def parse_args(args: list) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description='Run demo script')
  parser.add_argument(
    '-s','--script', dest='script',
    action='store',
    help='Demo script')
  parser.add_argument(
    '-r','--run', dest='demo',
    action='store',
    help='Run demo with the specified script')
  parser.add_argument(
    '--setup', dest='setup',
    action='store',default='setup.yml',
    help='Setup file')
  return parser.parse_args(args)

def bold(s: str) -> str:
  return f'[bold]{s}[/bold]'

def confirm(s: str, prompt: typing.Optional[str] = None) -> str:
  console = rich.console.Console()
  console.print(s,end="")
  try:
    return input(prompt or ' -> ').lower()
  except KeyboardInterrupt as ex:
    print('Bye')
    sys.exit(0)

def confirm_abort(s: str) -> typing.Never:
  confirm(bold(s))
  sys.exit(1)

def traceback(exc: Exception) -> list:
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

def run_demo(args: argparse.Namespace) -> None:
  setup = read_setup(args)

  cmd = ['tmux','new-session','-s',setup.session,setup.shell]
  cmd += [';','split-window','-v','-l','1','python3',__file__,'--script',args.demo]
  cmd += [';','select-pane','-L']

  subprocess.run(cmd)

def send_line(line: str, session: str, sleep: float = 0.03) -> None:
  tmux_cmd = ['tmux','send-keys','-t',f'{session}:0.0']
  if sleep:
    for chr in line:
      subprocess.run(tmux_cmd + [ chr ])
      time.sleep(sleep)
  else:
    subprocess.run(tmux_cmd + [ line ])
  subprocess.run(tmux_cmd + ['Enter'])

def run_action(action: Box, session: str = 'demo') -> None:
  if action.switch:
    subprocess.run(['tmux','select-pane','-U'])
  elif action.cmd:
    send_line(action.cmd,session)
    if action.more:
      confirm(bold('More...'),prompt=' ')
  if action.more:
    subprocess.run(['tmux','send-keys','-t',f'{session}:0.0','   ','q','C-u'])

def run_script(args: argparse.Namespace) -> None:
  setup = read_setup(args)
  script = read_yaml(args.script)
  if 'directory' not in script:
    confirm_abort('Target directory not specified in demo script')
  if 'steps' not in script:
    confirm_abort('The demo script has no steps')

  send_line(f'cd {setup.directory}/{script.directory}',session=setup.session,sleep=0)
  for step in list(script.steps):
    confirm(bold(step))
    action = script.steps[step]
    if isinstance(action,str):
      send_line(action,session=setup.session)
      continue
    elif not isinstance(action,Box):
      continue
    run_action(action,session=setup.session)

  confirm(bold('Done'))
  subprocess.run(['tmux','kill-server'])

def main() -> None:
  args = sys.argv[1:]
  if not args:
    parse_args(['--help'])
    return

  args = parse_args(sys.argv[1:])
  if args.demo:
    run_demo(args)
  elif args.script:
    run_script(args)
  else:
    print('Unknown option, aborting')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    subprocess.run(['tmux','resize-pane','-y','50%'])
    print(ex)
    print(str(ex))
    for line in traceback(ex):
      print(line)
    confirm('Exit')