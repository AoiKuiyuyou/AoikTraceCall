# coding: utf-8
from __future__ import absolute_import

# Internal imports
from aoiktracecall.state import count_get
from aoiktracecall.state import get_simple_thread_id
from aoiktracecall.state import level_add
from aoiktracecall.state import level_get


try:
    from pyfiglet import figlet_format
except ImportError:
    figlet_format = None


def indent_text(text, indent):
    new_part_s = []
    for line in text.split('\n'):
        new_part_s.append(indent)
        new_part_s.append(line)
        new_part_s.append('\n')
    new_part_s.pop()
    res = ''.join(new_part_s)
    return res


def print_text(
    text,
    indent_unit='        ',
    indent_by_level=True,
    level_step_before=0,
    level_step_after=0,
    level_diff=0,
    count=True,
    figlet=False,
    auto_step=False,
):
    #
    if auto_step:
        level_step_before = 1

        level_step_after = -1

    #
    if level_step_before:
        level_add(level_step_before)

    #
    thread_id = get_simple_thread_id()

    #
    head_mark = ''
    if text.startswith('+'):
        head_mark = '+'
    elif text.startswith('-'):
        head_mark = '-'
    else:
        head_mark = '!'

    #
    if count is None or count is False:
        count_text = ''
    elif count is True:
        count_text = '{} {} '.format(head_mark, count_get())
    else:
        count_text = '{} {} '.format(head_mark, count)

    text = '{head_mark} T{thread_id} {count_text}{text} {head_mark}'.format(
        head_mark=head_mark,
        thread_id=thread_id,
        count_text=count_text,
        text=text)

    if figlet:
        if figlet_format is not None:
            text = figlet_format(text, width=1000)

    if indent_unit is not None:
        if indent_by_level:
            indent = indent_unit * (level_get() + level_diff)
        else:
            indent = indent_unit

        text = indent_text(text, indent)

    print(text)

    #
    if level_step_after:
        level_add(level_step_after)
