# coding: utf-8
# pylint: disable=missing-docstring
"""
This module contains tests.
"""
from __future__ import absolute_import

# Standard imports
import sys

# Internal imports
from aoikinspectargs import ArgumentType
from aoikinspectargs import InspectInfo
from aoikinspectargs import ParameterType
from aoikinspectargs import format_arguments
from aoikinspectargs import inspect_arguments


# Whether is Python 2
IS_PY2 = sys.version_info[0] == 2


def check_inspect_info(info):
    """
    Ensure inspect info is valid.

    :param info: InspectInfo instance.

    :return: None.
    """
    # Ensure type
    assert isinstance(info, InspectInfo)

    # Ensure item count
    assert len(info) == 9

    # Ensure keys are present
    assert InspectInfo.K_POSKWD_PARAM_NAMES in info
    assert InspectInfo.K_KWDONLY_PARAM_NAMES in info
    assert InspectInfo.K_VARPOS_PARAM_NAME in info
    assert InspectInfo.K_VARKWD_PARAM_NAME in info
    assert InspectInfo.K_FIXED_ARG_INFOS in info
    assert InspectInfo.K_VARPOS_ARG_INFOS in info
    assert InspectInfo.K_VARKWD_ARG_INFOS in info
    assert InspectInfo.K_DUPKWD_ARG_INFOS in info
    assert InspectInfo.K_MISSING_ARG_INFOS in info


def test_inspect_arguments_case_no_params_no_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func():
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None
    assert info.fixed_arg_infos == {}
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_no_params_pos_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func():
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[0],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None
    assert info.fixed_arg_infos == {}

    #
    assert len(info.varpos_arg_infos) == 1

    #
    arg_info = info.varpos_arg_infos[0]

    #
    assert arg_info.name is None
    assert arg_info.type == ArgumentType.VAR_POSITIONAL

    # This is because the function has no variable-positional parameter
    assert arg_info.param_type is None

    #
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_no_params_kwd_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func():
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs=dict(
            a=1,
        ),
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None
    assert info.fixed_arg_infos == {}
    assert info.varpos_arg_infos == []

    #
    assert len(info.varkwd_arg_infos) == 1

    #
    arg_info = info.varkwd_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.type == ArgumentType.VAR_KEYWORD

    # This is because the function has no variable-keyword parameter
    assert arg_info.param_type is None

    #
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_poskwd_param_miss_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(a):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == ['a']
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None
    assert info.fixed_arg_infos == {}
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}

    #
    assert list(info.missing_arg_infos.keys()) == ['a']

    #
    arg_info = info.missing_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.type == ArgumentType.MISSING
    assert arg_info.param_type == ParameterType.POSITIONAL_OR_KEYWORD


def test_inspect_arguments_case_poskwd_param_pos_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(a):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[1],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == ['a']
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None
    assert list(info.fixed_arg_infos.keys()) == ['a']

    #
    arg_info = info.fixed_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.type == ArgumentType.POSITIONAL
    assert arg_info.value == 1
    assert arg_info.pos_index == 0
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.POSITIONAL_OR_KEYWORD

    #
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_poskwd_param_kwd_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(a):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs=dict(
            a=1,
        ),
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == ['a']
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None
    assert list(info.fixed_arg_infos.keys()) == ['a']

    #
    arg_info = info.fixed_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.type == ArgumentType.KEYWORD
    assert arg_info.value == 1
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.POSITIONAL_OR_KEYWORD

    #
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_poskwd_param_dft_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(a=1):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == ['a']
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None
    assert list(info.fixed_arg_infos.keys()) == ['a']

    #
    arg_info = info.fixed_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.type == ArgumentType.DEFAULT
    assert arg_info.value == 1
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.POSITIONAL_OR_KEYWORD

    #
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_varpos_param_no_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(*var_args):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name == 'var_args'
    assert info.varkwd_param_name is None
    assert info.fixed_arg_infos == {}
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_varpos_param_pos_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(*var_args):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[1, 2],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name == 'var_args'
    assert info.varkwd_param_name is None
    assert info.fixed_arg_infos == {}

    #
    assert len(info.varpos_arg_infos) == 2

    #
    arg_info = info.varpos_arg_infos[0]

    #
    assert arg_info.name is None
    assert arg_info.value == 1
    assert arg_info.type == ArgumentType.VAR_POSITIONAL
    assert arg_info.pos_index is None
    assert arg_info.varpos_index == 0
    assert arg_info.param_type == ParameterType.VAR_POSITIONAL

    #
    arg_info = info.varpos_arg_infos[1]

    #
    assert arg_info.name is None
    assert arg_info.value == 2
    assert arg_info.type == ArgumentType.VAR_POSITIONAL
    assert arg_info.pos_index is None
    assert arg_info.varpos_index == 1
    assert arg_info.param_type == ParameterType.VAR_POSITIONAL

    #
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_varkwd_param_no_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(**var_kwargs):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name == 'var_kwargs'
    assert info.fixed_arg_infos == {}
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_varkwd_param_kwd_args():
    """
    Test `inspect_arguments`.
    """
    # Create function
    def func(**var_kwargs):
        pass

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs=dict(
            a=1,
            b=2
        ),
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == []
    assert info.varpos_param_name is None
    assert info.varkwd_param_name == 'var_kwargs'
    assert info.fixed_arg_infos == {}
    assert info.varpos_arg_infos == []

    #
    assert set(info.varkwd_arg_infos.keys()) == set(['a', 'b'])

    #
    arg_info = info.varkwd_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.value == 1
    assert arg_info.type == ArgumentType.VAR_KEYWORD
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.VAR_KEYWORD

    #
    arg_info = info.varkwd_arg_infos['b']

    #
    assert arg_info.name == 'b'
    assert arg_info.value == 2
    assert arg_info.type == ArgumentType.VAR_KEYWORD
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.VAR_KEYWORD

    #
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_kwdonly_params_dft_args():
    """
    Test `inspect_arguments`.
    """
    # If is Python 2.
    # Python 2 has no keyword-only parameters.
    if IS_PY2:
        # Ignore
        return

    # Create function.
    # The keyword-only parameter syntax will cause syntax error in Python 2.
    # Use exec to avoid the syntax error.
    py3_only_code = r"""
def func(*, a=1, b=2):
    pass
"""

    # `exec`'s context dict
    context_dict = {}

    # Execute code in the context
    exec(py3_only_code, context_dict, context_dict)

    # Get function
    func = context_dict['func']

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs={},
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == ['a', 'b']
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None

    #
    assert list(info.fixed_arg_infos.keys()) == ['a', 'b']

    #
    arg_info = info.fixed_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.value == 1
    assert arg_info.type == ArgumentType.DEFAULT
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.KEYWORD_ONLY

    #
    arg_info = info.fixed_arg_infos['b']

    #
    assert arg_info.name == 'b'
    assert arg_info.value == 2
    assert arg_info.type == ArgumentType.DEFAULT
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.KEYWORD_ONLY

    #
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_inspect_arguments_case_kwdonly_params_kwd_args():
    """
    Test `inspect_arguments`.
    """
    # If is Python 2.
    # Python 2 has no keyword-only parameters.
    if IS_PY2:
        # Ignore
        return

    # Create function.
    # The keyword-only parameter syntax will cause syntax error in Python 2.
    # Use exec to avoid the syntax error.
    py3_only_code = r"""
def func(*, a=1, b=2):
    pass
"""

    # `exec`'s context dict
    context_dict = {}

    # Execute code in the context
    exec(py3_only_code, context_dict, context_dict)

    # Get function
    func = context_dict['func']

    # Inspect function arguments
    info = inspect_arguments(
        func=func,
        args=[],
        kwargs=dict(
            a=100,
            b=200,
        ),
    )

    # Check inspect info
    check_inspect_info(info)

    #
    assert info.poskwd_param_names == []
    assert info.kwdonly_param_names == ['a', 'b']
    assert info.varpos_param_name is None
    assert info.varkwd_param_name is None

    #
    assert list(info.fixed_arg_infos.keys()) == ['a', 'b']

    #
    arg_info = info.fixed_arg_infos['a']

    #
    assert arg_info.name == 'a'
    assert arg_info.value == 100
    assert arg_info.type == ArgumentType.KEYWORD_ONLY
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.KEYWORD_ONLY

    #
    arg_info = info.fixed_arg_infos['b']

    #
    assert arg_info.name == 'b'
    assert arg_info.value == 200
    assert arg_info.type == ArgumentType.KEYWORD_ONLY
    assert arg_info.pos_index is None
    assert arg_info.varpos_index is None
    assert arg_info.param_type == ParameterType.KEYWORD_ONLY

    #
    assert info.varpos_arg_infos == []
    assert info.varkwd_arg_infos == {}
    assert info.dupkwd_arg_infos == {}
    assert info.missing_arg_infos == {}


def test_format_arguments_case_no_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func():
        pass

    # Positional arguments
    args = []

    # Keyword arguments
    kwargs = {}

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == ''


def test_format_arguments_case_pos_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a):
        pass

    # Positional arguments
    args = [1]

    # Keyword arguments
    kwargs = {}

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'a=1'


def test_format_arguments_case_kwd_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a):
        pass

    # Positional arguments
    args = []

    # Keyword arguments
    kwargs = dict(
        a=1,
    )

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'a=1'


def test_format_arguments_case_varpos_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a, *args):
        pass

    # Positional arguments
    args = [1, 2, 3]

    # Keyword arguments
    kwargs = {}

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'a=1, *args=[2, 3]'


def test_format_arguments_case_varkwd_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a, **kwargs):
        pass

    # Positional arguments
    args = [1]

    # Keyword arguments
    kwargs = dict(
        b=2,
        c=3,
    )

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'a=1, **kwargs={b=2, c=3}'


def test_format_arguments_case_pos_varpos_varkwd_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a, *args, **kwargs):
        pass

    # Positional arguments
    args = [1, 2, 3]

    # Keyword arguments
    kwargs = dict(
        x=100,
        y=200,
        z=300
    )

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'a=1, *args=[2, 3], **kwargs={x=100, y=200, z=300}'


def test_format_arguments_case_pos_kwd_dft_varkwd_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a, b, c=3, *args, **kwargs):
        pass

    # Positional arguments
    args = [1]

    # Keyword arguments
    kwargs = dict(
        b=2,
        x=100,
        y=200,
        z=300
    )

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'a=1, b=2, c=3, *args=[], **kwargs={x=100, y=200, z=300}'


def test_format_arguments_case_miss_args():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a, b):
        pass

    # Positional arguments
    args = [1]

    # Keyword arguments
    kwargs = {}

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'a=1'


def test_format_arguments_case_repr_func_raises_error():
    """
    Test `format_arguments`.
    """
    # Create function
    def func(a):
        pass

    # Positional arguments
    args = [1]

    # Keyword arguments
    kwargs = {}

    # Create repr function that raises exception
    def repr_func(value):
        raise ValueError()

    # Format function arguments
    text = format_arguments(
        func=func,
        args=args,
        kwargs=kwargs,
        repr_func=repr_func,
    )

    # Check result text
    assert text == 'a=<?>'


def test_format_arguments_case_filter_func():
    """
    Test `format_arguments`.
    """
    # Create class
    class CustomClass(object):

        # Create function with the first parameter name being `self`
        def func(self, a):
            pass

    # Positional arguments
    args = [0, 1]

    # Keyword arguments
    kwargs = {}

    # Format function arguments
    text = format_arguments(
        func=CustomClass.func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
    )

    # Check result text
    assert text == 'self=0, a=1'

    # Create inspect info filter function that removes `self` argument info
    def filter_func(info):
        """
        Inspect info filter function that removes `self` argument info.

        :param info: InspectInfo instance.

        :return: None.
        """
        # Get fixed argument infos dict
        fixed_arg_infos = info[InspectInfo.K_FIXED_ARG_INFOS]

        # If fixed argument infos dict is not empty
        if fixed_arg_infos:
            # Get the first fixed argument name
            first_arg_name = next(iter(fixed_arg_infos))

            # If the first fixed argument name is `self`
            if first_arg_name == 'self':
                # Remove `self` argument info
                del fixed_arg_infos['self']

    # Format function arguments
    text = format_arguments(
        func=CustomClass.func,
        args=args,
        kwargs=kwargs,
        repr_func=repr,
        filter_func=filter_func,
    )

    # Check result text
    assert text == 'a=1'
