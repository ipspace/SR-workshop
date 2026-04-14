#!/usr/bin/env python3
#
import typing
import subprocess
import os
import rich.console
import rich.table
from pathlib import Path
from box import Box

from common import read_yaml, confirm, bold

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

  menu_dir = str(Path(args.menu).parent)
  os.chdir(menu_dir)

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

    exec_cmd = ['python3',args.me,'--setup',args.setup,'-r',lookup[select]+'.yml',]
    subprocess.run(exec_cmd)
