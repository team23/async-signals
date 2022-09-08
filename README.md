# async-signals

Easy library to implement the observer pattern in async code.

**Note:** This library is a copy of the signals library from 
[Django](https://docs.djangoproject.com/en/4.1/topics/signals/). I always felt
like using the observer pattern in Django is pretty well crafted and liked
the way Django did implement this. But when switching to
[FastAPI](https://fastapi.tiangolo.com/) I missed this feature. So I decided
to copy the signals library from Django and implement it for FastAPI and other
async frameworks.  
A big thanks to the nice people why built Django! And for using a BSD license
to make this possible.

## Changes from the original Django signals library

* `Signal.send(...)` and `Signal.send_robust(...)` are now async functions 🚀
* I added type annotations to all functions and classes, mypy is happy now 🧐
* I created tests for the signals library - without using any Django models 😎

## Usage

```python
from async_signals import Signal

# Create a signal
my_signal = Signal()

# Connect a function to the signal (can be async or sync, needs to receive **kwargs)
async def my_handler(sender, **kwargs):
    print("Signal received!")

my_signal.connect(my_handler)

# Send the signal
await my_signal.send("sender")
```

`signal.send(...)` will return a list of all called receivers and their return
values.

## About weak signals

The signal class will automatically remove signals when the receiver is
garbage collected. This is done by using weak references. This means that
you can use signals in long running applications without having to worry
about memory leaks.

If you want to disable this behaviour you can set the `weak` parameter to
`False` when connecting the receiver.

```python
my_signal.connect(my_handler, weak=False)

# or

my_signal.connect(my_handler, weak=True)  # the default
```

## About async signals

The signal class will automatically await async receivers. If your receiver
is sync it will be executed normally.

## About the sender

The sender is the object that sends the signal. It can be anything. It is
passed to the receiver as the first argument. This is useful if you want to
have multiple signals in your application and you want to know which signal
was sent. Normally the sender is the object that triggers the signal.

You may also pass the sender when connecting a receiver. This is useful if
you want to connect a receiver to a specific sender. If you do this the
receiver will only be called when the sender is the same as the one you
passed when connecting the receiver.

**Note:** I normally tend to use Pydantic models as the sender in FastAPI. But
feel free to use whatever you want.

```python
my_signal.connect(my_handler, sender="sender")

# This will not call the receiver
await my_signal.send("other_sender")
```

## Using the receiver decorator

You can also use the `receiver` decorator to connect a receiver to a signal.

```python
@receiver(my_signal)
async def my_handler(sender, **kwargs):
    print("Signal received!")
```

Or if you want to limit the receiver to a specific sender.

```python
@receiver(my_signal, sender="sender")
async def my_handler(sender, **kwargs):
    print("Signal received!")
```

## Handle exceptions

By default the signal class will raise exceptions raised by receivers. If
you want the signal to catch the exceptions and continue to call the other
receivers you can use `send_robust(..)` instead of `send()`. The return value
will be a list of tuples containing the receiver and the return or the
exception raised by the receiver. You will need to check the type of the
return value to see if it is an exception or not.

```python
await my_signal.send_robust("sender")
```

# Contributing

If you want to contribute to this project, feel free to just fork the project,
create a dev branch in your fork and then create a pull request (PR). If you
are unsure about whether your changes really suit the project please create an
issue first, to talk about this.
