import functools
import inspect
import sys
import warnings
from types import FunctionType

import wrapt
from deprecated import deprecated as _deprecated

# noinspection PyProtectedMember
from deprecated.classic import _routine_stacklevel, _class_stacklevel
# noinspection PyPackageRequirements
from interface import Interface as _Interface, implements as _implements
# noinspection PyPackageRequirements
from interface import interface

# Function / class decorators.
from overload import overload

deprecated = _deprecated
implements = _implements

# Class Decorators
Interface = _Interface


class InvalidImplementation(TypeError):
    """
    Raised when a class intending to implement an interface fails to do so.
    """

    __module__ = "builtins"


class InvalidSubInterface(TypeError):
    """
    Raised when on attempt to define a subclass of an interface that's not
    compatible with the parent definition.
    """

    __module__ = "builtins"


interface.InvalidImplementation = InvalidImplementation
interface.InvalidSubInterface = InvalidSubInterface


# ExperimentalWarning
class ExperimentalWarning(Warning):
    """ Base class for warnings about experimental functionality. """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class ClassicAdapter(wrapt.AdapterFactory):
    """
    Classic adapter -- *for advanced usage only*

    This adapter is used to get the deprecation message according to the wrapped object type:
    class, function, standard method, static method, or class method.

    This is the base class of the :class:`~experimental.sphinx.SphinxAdapter` class
    which is used to update the wrapped object docstring.

    You can also inherit this class to change the deprecation message.

    In the following example, we change the message into "The ... is experimental.":

    .. code-block:: python

       import inspect

       from experimental.classic import ClassicAdapter
       from experimental.classic import experimental


       class MyClassicAdapter(ClassicAdapter):
           def get_deprecated_msg(self, wrapped, instance):
               if instance is None:
                   if inspect.isclass(wrapped):
                       fmt = "The class {name} is experimental."
                   else:
                       fmt = "The function {name} is experimental."
               else:
                   if inspect.isclass(instance):
                       fmt = "The class method {name} is experimental."
                   else:
                       fmt = "The method {name} is experimental."
               if self.reason:
                   fmt += " ({reason})"
               if self.version:
                   fmt += " -- Deprecated since version {version}."
               return fmt.format(name=wrapped.__name__,
                                 reason=self.reason or "",
                                 version=self.version or "")

    Then, you can use your ``MyClassicAdapter`` class like this in your source code:

    .. code-block:: python

       @experimental(reason="use another function", adapter_cls=MyClassicAdapter)
       def some_old_function(x, y):
           return x + y
    """

    def __init__(self, action=None, category=ExperimentalWarning):
        """
        Construct a wrapper adapter.

        :type  action: str
        :param action:
            A warning filter used to activate or not the deprecation warning.
            Can be one of "error", "ignore", "always", "default", "module", or "once".
            If ``None`` or empty, the the global filtering mechanism is used.
            See: `The Warnings Filter`_ in the Python documentation.

        :type  category: type
        :param category:
            The warning category to use for the deprecation warning.
            By default, the category class is :class:`~DeprecationWarning`,
            you can inherit this class to define your own deprecation warning category.
        """
        self.action = action
        self.category = category
        super(ClassicAdapter, self).__init__()

    @staticmethod
    def get_experimental_msg(wrapped, instance):
        """
        Get the deprecation warning message for the user.

        :param wrapped: Wrapped class or function.

        :param instance: The object to which the wrapped function was bound when it was called.

        :return: The warning message.
        """

        if instance is None:
            if inspect.isclass(wrapped):
                fmt = "Call to experimental class {name}."
            else:
                if inspect.isfunction(wrapped):
                    fmt = "Call to experimental function {name}."
                else:
                    fmt = "Call to experimental function (or staticmethod) {name}."
        else:
            if inspect.isclass(instance):
                fmt = "Call to experimental class method {name}."
            else:
                fmt = "Call to experimental method {name}."
        return fmt.format(name=wrapped.__name__)

    def __call__(self, wrapped):
        """
        Decorate your class or function.

        :param wrapped: Wrapped class or function.

        :return: the decorated class or function.

        .. versionchanged:: 1.2.4
           Don't pass arguments to :meth:`object.__new__` (other than *cls*).

        .. versionchanged:: 1.2.8
           The warning filter is not set if the *action* parameter is ``None`` or empty.
        """
        if inspect.isclass(wrapped):
            old_new1 = wrapped.__new__

            def wrapped_cls(cls, *args, **kwargs):
                msg = self.get_experimental_msg(wrapped, None)
                if self.action:
                    with warnings.catch_warnings():
                        warnings.simplefilter(self.action, self.category)
                        warnings.warn(msg, category=self.category, stacklevel=_class_stacklevel)
                else:
                    warnings.warn(msg, category=self.category, stacklevel=_class_stacklevel)
                if old_new1 is object.__new__:
                    return old_new1(cls)
                # actually, we don't know the real signature of *old_new1*
                return old_new1(cls, *args, **kwargs)

            wrapped.__new__ = staticmethod(wrapped_cls)

        return wrapped


def experimental(*args, **kwargs):
    """
    This is a decorator which can be used to mark functions
    as experimental. It will result in a warning being emitted
    when the function is used.

    **Classic usage:**

    To use this, decorate your experimental function with **@experimental** decorator:

    .. code-block:: python

       from experimental import experimental


       @experimental
       def some_old_function(x, y):
           return x + y

    You can also decorate a class or a method:

    .. code-block:: python

       from experimental import experimental


       class SomeClass(object):
           @experimental
           def some_old_method(self, x, y):
               return x + y


       @experimental
       class SomeOldClass(object):
           pass

    You can give a *reason* message to help the developer to choose another function/class,
    and a *version* number to specify the starting version number of the deprecation.

    .. code-block:: python

       from experimental import experimental


       @experimental(reason="use another function", version='1.2.0')
       def some_old_function(x, y):
           return x + y

    The *category* keyword argument allow you to specify the deprecation warning class of your choice.
    By default, :exc:`DeprecationWarning` is ued but you can choose :exc:`FutureWarning`,
    :exc:`PendingDeprecationWarning` or a custom subclass.

    .. code-block:: python

       from experimental import experimental


       @experimental(category=PendingDeprecationWarning)
       def some_old_function(x, y):
           return x + y

    The *action* keyword argument allow you to locally change the warning filtering.
    *action* can be one of "error", "ignore", "always", "default", "module", or "once".
    If ``None``, empty or missing, the the global filtering mechanism is used.
    See: `The Warnings Filter`_ in the Python documentation.

    .. code-block:: python

       from experimental import experimental


       @experimental(action="error")
       def some_old_function(x, y):
           return x + y

    """
    if args and not callable(args[0]):
        raise TypeError(repr(type(args[0])))

    if args:
        action = kwargs.get('action')
        category = kwargs.get('category', ExperimentalWarning)
        adapter_cls = kwargs.pop('adapter_cls', ClassicAdapter)
        adapter = adapter_cls(**kwargs)

        wrapped = args[0]
        if inspect.isclass(wrapped):
            wrapped = adapter(wrapped)
            return wrapped

        elif inspect.isroutine(wrapped):

            @wrapt.decorator(adapter=adapter)
            def wrapper_function(wrapped_, instance_, args_, kwargs_):
                msg = adapter.get_experimental_msg(wrapped_, instance_)
                if action:
                    with warnings.catch_warnings():
                        warnings.simplefilter(action, category)
                        warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                else:
                    warnings.warn(msg, category=category, stacklevel=_routine_stacklevel)
                return wrapped_(*args_, **kwargs_)

            return wrapper_function(wrapped)

        else:
            raise TypeError(repr(type(wrapped)))

    return functools.partial(experimental, **kwargs)


def on_define(*args, **kwargs):
    # noinspection PyShadowingNames
    def decorator(func):
        func(*args, **kwargs)

    return decorator


def log(*message, sep=" ", file=sys.stderr, flush=True):
    def decorator(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(message) > 0:
                print(f"Logged call of {name}(): {sep.join(message)}", file=file, flush=flush)
            else:
                print(f"Logged call of {name}()", file=file, flush=flush)

            func(*args, **kwargs)

        return wrapper

    return decorator


def suppress_warnings(*categories):
    # if len(categories) == 0:
    #     raise ValueError("No categories.")

    def decorator(func):
        func: FunctionType

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with warnings.catch_warnings(record=True) as warn:
                warnings.simplefilter("always")

                out = func(*args, **kwargs)

                warns = warn

            for w in warns:
                w: warnings.WarningMessage
                # print(w)
                if w.category not in categories:
                    w.lineno = func.__code__.co_firstlineno

                    frame = inspect.currentframe().f_back
                    w.lineno = frame.f_lineno
                    w.filename = frame.f_globals["__file__"]

                    # print(w.filename)
                    # print(w.lineno)

                    with open(w.filename) as file:
                        w.line = file.read().splitlines()[w.lineno - 1]

                    warnings.showwarning(w.message, w.category, w.filename, w.lineno, w.file, w.line)
                # print("deprecated" in str(w.message))
            return out

        return wrapper

    return decorator


# class interface(object):
#     def __init__(self, args=None, varargs=None, keywords=None, defaults=0):
#         pass
#
#
# class method(object):
#     def __init__(self, args=None, varargs=None, keywords=None, defaults=0):
#         self.args = args or []
#         self.varargs = varargs
#         self.keywords = keywords
#         self.defaults = defaults
#
#
# class implements(object):
#     def __init__(self, interface):
#         self.interface = interface
#
#     def __call__(self, clazz):
#         methods = [each for each in dir(self.interface) if inspect.ismethod(each)]
#         for each in methods:
#             self._assert_implements(clazz, each)
#         return clazz
#
#     def _assert_implements(self, clazz, method_name):
#         method_contract = object.__getattribute__(self.interface, method_name)
#         method_impl = inspect.getfullargspec(object.__getattribute__(clazz, method_name))
#         assert method_name in dir(clazz)
#         assert method_contract.args == method_impl.args
#         assert method_contract.varargs == method_impl.varargs
#         assert method_contract.keywords == method_impl.varkw
#         if method_impl.defaults is not None:
#             assert method_contract.defaults == len(method_impl.defaults)
#         else:
#             assert method_contract.defaults == 0


def readonly(*attrs):
    """
    Class decorator to mark selected attributes of a class as read-only. All
    attributes in ``attrs`` cannot be modified. If ``*`` is present in
    ``attrs`` then no attribute can be modified.

    Parameters
    ----------
    attrs : list of str
        Names of the attributes that should be constants. '*' value will
        make all attributes constant
    """

    def _rebuilt_class(cls):
        class ReadOnlyPropertyClass(cls):
            @overload
            def __setattr__(self, name, value):
                if "*" in attrs:
                    raise AttributeError(
                        "All attributes of this class are read-only")
                if name in attrs:
                    err = "Cannot modify `{}` as it is marked as read-only"
                    err = err.format(name)
                    raise AttributeError(err)
                return super().__setattr__(name, value)

            @classmethod
            @overload
            def __setattr__(cls, name, value):
                if "*" in attrs:
                    raise AttributeError(
                        "All attributes of this class are read-only")
                if name in attrs:
                    err = "Cannot modify `{}` as it is marked as read-only"
                    err = err.format(name)
                    raise AttributeError(err)
                return super().__setattr__(name, value)

        return ReadOnlyPropertyClass

    return _rebuilt_class


if __name__ == '__main__':
    # @suppress_warnings(DeprecationWarning)
    @deprecated
    def some_old_function(x, y):
        warnings.warn("Call to deprecated function.", DeprecationWarning)
        warnings.warn("Syntax warning.", SyntaxWarning, 3)
        warnings.warn("Import failed.", ImportWarning, 3)
        warnings.warn("Call to experimental function.", ExperimentalWarning, 3)
        return x + y


    @suppress_warnings(DeprecationWarning)
    def test3():
        # noinspection PyDeprecation
        print(some_old_function(3, 5))


    def test_readonly():
        @readonly("readonly_attr")
        class TestReadonly(object):
            readonly_attr = "LOL"

            def __init__(self):
                self.readonly_attr = "LOL2"

        TestReadonly.readonly_attr = "Test"
        print(TestReadonly.readonly_attr)
        TestReadonly()


    test_readonly()

    test3()
