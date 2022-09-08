from async_signals.utils import _get_callable_parameters, _get_func_parameters, func_accepts_kwargs


def the_valid_function(arg1, arg2, **kwargs):
    pass


def the_invalid_function(arg1, arg2):
    pass


class TheTestClass:
    def the_valid_method(self, arg1, arg2, **kwargs):
        pass

    def the_invalid_method(self, arg1, arg2):
        pass


the_test_instance = TheTestClass()


def test_get_func_parameters():
    params = _get_func_parameters(the_valid_function, remove_first=False)
    assert len(params) == 3

    params = _get_func_parameters(the_invalid_function, remove_first=False)
    assert len(params) == 2

    params = _get_func_parameters(TheTestClass.the_valid_method, remove_first=False)
    assert len(params) == 4

    params = _get_func_parameters(TheTestClass.the_invalid_method, remove_first=False)
    assert len(params) == 3

    params = _get_func_parameters(TheTestClass.the_valid_method, remove_first=True)
    assert len(params) == 3

    params = _get_func_parameters(TheTestClass.the_invalid_method, remove_first=True)
    assert len(params) == 2


def test_get_callable_parameters():
    params = _get_callable_parameters(the_valid_function)
    assert len(params) == 3

    params = _get_callable_parameters(the_invalid_function)
    assert len(params) == 2

    params = _get_callable_parameters(the_test_instance.the_valid_method)
    assert len(params) == 3

    params = _get_callable_parameters(the_test_instance.the_invalid_method)
    assert len(params) == 2


def test_func_accepts_kwargs():
    assert func_accepts_kwargs(the_valid_function)
    assert not func_accepts_kwargs(the_invalid_function)
    assert func_accepts_kwargs(the_test_instance.the_valid_method)
    assert not func_accepts_kwargs(the_test_instance.the_invalid_method)
