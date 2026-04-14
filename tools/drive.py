#!/usr/bin/env python3
#
import argparse
import time
import typing
import subprocess
from box import Box

from common import bold, confirm, confirm_abort, read_setup, read_yaml

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
