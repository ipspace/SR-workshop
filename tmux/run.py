#!/usr/bin/env python3
#
import argparse
import time
import io
import sys
import typing
import subprocess
import rich.console
import rich.table
from box import Box

def parse_args(args: list) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description='Run demo script')
  mode_group = parser.add_mutually_exclusive_group()
  mode_group.add_argument(
    '-s','--script', dest='script',
    action='store',
    help='Demo script')
  mode_group.add_argument(
    '-r','--run', dest='demo',
    action='store',
    help='Run demo with the specified script')
  mode_group.add_argument(
    '-m','--menu', dest='menu',
    action='store',
    help='Start autopilot with the specified top-level menu')
  parser.add_argument(
    '--setup', dest='setup',
    action='store',default='setup.yml',
    help='Setup file')
  return parser.parse_args(args)

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
  cmd += ['python3',__file__,'--script',args.demo]

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

def wait_for_pane(wait: typing.Any, setup: Box) -> None:
  wait_string = wait if isinstance(wait,str) else setup.wait
  if not wait_string:
    return

  print('Waiting...',end="",flush=True)
  start_time = time.time()
  print_time = start_time
  try:
    while True:
      result = subprocess.run(
                  ['tmux','capture-pane','-p','-S','9999','-t',f'{setup.session}:0.0'],
                  capture_output=True,check=True)
      if wait_string in result.stdout.decode("utf-8"):
        print("Completed")
        return
      now = time.time()
      if now > print_time + 5:
        print()
        print(f'Waiting ({int(now - start_time)} seconds) ...',end="",flush=True)
        print_time = now
      time.sleep(0.25)

  except subprocess.CalledProcessError as ex:
    print(f'tmux capture-pane failed: {str(ex)}')
    return
  except KeyboardInterrupt:
    print('Giving up')
    return

def run_action(action: Box, setup: Box) -> None:
  if action.switch:
    subprocess.run(['tmux','select-pane','-U'])
  elif action.cmd:
    send_line(action.cmd,setup.session)
    if action.more:
      confirm(bold('More...'),prompt=' ',single_key=True)
    elif action.wait:
      wait_for_pane(action.wait,setup)
  if action.more:
    subprocess.run(['tmux','send-keys','-t',f'{setup.session}:0.0','   ','q','C-u'])

def run_script(args: argparse.Namespace) -> None:
  setup = read_setup(args)
  script = read_yaml(args.script)
  if 'directory' not in script:
    confirm_abort('Target directory not specified in demo script')
  if 'steps' not in script:
    confirm_abort('The demo script has no steps')

  send_line(f'cd {setup.directory}/{script.directory}',session=setup.session,sleep=0)
  for step in list(script.steps):
    confirm(bold(step),single_key=True)
    action = script.steps[step]
    if isinstance(action,str):
      send_line(action,session=setup.session)
      continue
    elif not isinstance(action,Box):
      continue
    run_action(action,setup=setup)

  confirm(bold('Done'),single_key=True)
  subprocess.run(['tmux','kill-session','-t',setup.session])

def get_menu_title(title: str, desc: str) -> str:
  return f"\\[{title[:1]}]: {desc}"

def display_menu(menu: Box, last_selected: typing.Optional[str] = None) -> dict:
  console = rich.console.Console()
  table = rich.table.Table(
            title=menu.get('title','The Demo')+"\n\n")
  max_row = 0
  selected: typing.Optional[str] = None
  lookup: dict = {}

  for col in menu.columns:
    table.add_column(col.title)
    max_row = max(max_row,len(col.demos))
    for demo in col.demos:
      key = demo[:1]
      if last_selected == key:
        last_selected = None
      elif last_selected is None:
        selected = key
        last_selected = key
      lookup[demo[:1]] = demo

  lookup['selected'] = selected

  table.add_row()
  for ridx in range(0,max_row):
    row_data = []
    for col in menu.columns:
      demo_titles = list(col.demos)
      if len(demo_titles) > ridx:
        d_key = demo_titles[ridx]
        row_value = get_menu_title(d_key,col.demos[d_key])
        if d_key[:1] == selected:
          row_value = bold(row_value)
        row_data.append(row_value)
      else:
        row_data.append("")

    table.add_row(*row_data)

  table.add_row()
  console.clear()
  console.print(table)
  return lookup

def show_menu(args) -> None:
  menu = read_yaml(args.menu)
  select: typing.Optional[str] = None
  while True:
    lookup = display_menu(menu,select)
    print()
    select = confirm(bold('Select demo'))
    if not select:
      select = lookup.get('selected','')
    if select not in lookup:
      confirm(bold('Invalid option'))
      select = None
      continue

    exec_cmd = ['python3',__file__,'--setup',args.setup,'-r',lookup[select]+'.yml']
    subprocess.run(exec_cmd)

def main() -> None:
  cli_args = sys.argv[1:]
  if not cli_args:
    parse_args(['--help'])
    return

  args = parse_args(cli_args)
  if args.menu:
    show_menu(args)
  elif args.demo:
    run_demo(args)
  elif args.script:
    run_script(args)
  else:
    print('Unknown option, aborting')
    sys.exit(2)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    subprocess.run(['tmux','resize-pane','-y','50%'])
    print(ex)
    print(str(ex))
    for line in fetch_traceback(ex):
      print(line)
    confirm('Exit')