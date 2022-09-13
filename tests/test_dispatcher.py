import gc

import pytest

from async_signals import Signal, receiver


@pytest.fixture
def signal() -> Signal:
    return Signal()


@pytest.fixture
def signal2() -> Signal:
    return Signal()


@pytest.fixture
def debug_signal() -> Signal:
    return Signal(debug=True)


@pytest.fixture
def cached_signal() -> Signal:
    return Signal(use_caching=True)


def test_signal_connect_disconnect(signal: Signal):
    def receiver_function(**kwargs):
        pass

    assert len(signal.receivers) == 0

    signal.connect(receiver_function)
    assert signal.has_listeners()
    assert len(signal.receivers) == 1

    signal.disconnect(receiver_function)
    assert not signal.has_listeners()
    assert len(signal.receivers) == 0


def test_signal_connect_weakref_removal(signal: Signal):
    def receiver_function(**kwargs):
        pass

    assert len(signal.receivers) == 0

    signal.connect(receiver_function)
    assert signal.has_listeners()
    assert len(signal.receivers) == 1

    del receiver_function
    gc.collect()
    assert not signal.has_listeners()
    assert len(signal.receivers) == 0


def test_signal_connect_with_weakref_is_false(signal: Signal):
    def receiver_function(**kwargs):
        pass

    assert len(signal.receivers) == 0

    signal.connect(receiver_function, weak=False)
    assert signal.has_listeners()
    assert len(signal.receivers) == 1

    del receiver_function
    gc.collect()
    assert signal.has_listeners()
    assert len(signal.receivers) == 1


def test_signal_connect_disconnect_for_methods(signal: Signal):
    class Receiver():
        def handler(self, **kwargs): pass

    receiver_obj = Receiver()

    assert len(signal.receivers) == 0

    signal.connect(receiver_obj.handler)
    assert signal.has_listeners()
    assert len(signal.receivers) == 1

    signal.disconnect(receiver_obj.handler)
    assert not signal.has_listeners()
    assert len(signal.receivers) == 0


def test_signal_connect_disconnect_with_dispatch_uid(signal: Signal):
    def receiver_function(**kwargs):
        pass

    dispatch_uid = "some_id"

    assert len(signal.receivers) == 0

    signal.connect(receiver_function, dispatch_uid=dispatch_uid)
    assert signal.has_listeners()
    assert len(signal.receivers) == 1

    signal.disconnect(receiver_function, dispatch_uid=dispatch_uid)
    assert not signal.has_listeners()
    assert len(signal.receivers) == 0


def test_signal_connect_disconnect_with_caching(cached_signal: Signal):
    def receiver_function(**kwargs):
        pass

    assert len(cached_signal.receivers) == 0

    cached_signal.connect(receiver_function)
    assert cached_signal.has_listeners()
    assert len(cached_signal.receivers) == 1

    cached_signal.disconnect(receiver_function)
    assert not cached_signal.has_listeners()
    assert len(cached_signal.receivers) == 0


def test_signal_connect_disconnect_with_caching_and_sender_name(cached_signal: Signal):
    def receiver_function(**kwargs):
        pass

    assert len(cached_signal.receivers) == 0

    cached_signal.connect(receiver_function)
    assert cached_signal.has_listeners(test_signal_connect_disconnect_with_caching_and_sender_name)
    assert len(cached_signal.receivers) == 1

    cached_signal.disconnect(receiver_function)
    assert not cached_signal.has_listeners(test_signal_connect_disconnect_with_caching_and_sender_name)
    assert len(cached_signal.receivers) == 0


def test_signal_with_debug_ensures_callable(debug_signal: Signal):
    with pytest.raises(TypeError):
        debug_signal.connect("invalid")  # type: ignore


def test_signal_with_debug_ensures_kwargs(debug_signal: Signal):
    def invalid_receiver_function():
        pass

    with pytest.raises(ValueError):
        debug_signal.connect(invalid_receiver_function)


@pytest.mark.anyio
async def test_signal_send_without_receivers(signal: Signal, mocker):
    result = await signal.send(sender=test_signal_send_without_receivers, x="a", y="b")

    assert len(result) == 0


@pytest.mark.anyio
async def test_signal_send_without_receivers_and_caching(signal: Signal, mocker):
    signal.use_caching = True

    result = await signal.send(sender=test_signal_send_without_receivers, x="a", y="b")

    assert len(result) == 0


@pytest.mark.anyio
async def test_signal_send_sync(signal: Signal, mocker):
    receiver_function = mocker.Mock()

    signal.connect(receiver_function)

    result = await signal.send(sender=test_signal_send_sync, x="a", y="b")

    assert len(result) == 1
    receiver_function.assert_called_once_with(
        sender=test_signal_send_sync,
        signal=signal,
        x="a",
        y="b",
    )


@pytest.mark.anyio
async def test_signal_send_async(signal: Signal, mocker):
    receiver_function = mocker.AsyncMock()

    signal.connect(receiver_function)

    result = await signal.send(sender=test_signal_send_async, x="a", y="b")

    assert len(result) == 1
    receiver_function.assert_called_once_with(
        sender=test_signal_send_async,
        signal=signal,
        x="a",
        y="b",
    )


@pytest.mark.anyio
async def test_signal_send_will_raise_exception(signal: Signal, mocker):
    receiver_function = mocker.AsyncMock(
        side_effect=Exception("Boom!"),
    )

    signal.connect(receiver_function)

    with pytest.raises(Exception):
        await signal.send(sender=test_signal_send_will_raise_exception, x="a", y="b")


@pytest.mark.anyio
async def test_signal_send_robust_without_receivers(signal: Signal, mocker):
    result = await signal.send_robust(sender=test_signal_send_without_receivers, x="a", y="b")

    assert len(result) == 0


@pytest.mark.anyio
async def test_signal_send_robust_works_normally(signal: Signal, mocker):
    receiver_function = mocker.AsyncMock()

    signal.connect(receiver_function)

    result = await signal.send_robust(sender=test_signal_send_async, x="a", y="b")

    assert len(result) == 1
    receiver_function.assert_called_once_with(
        sender=test_signal_send_async,
        signal=signal,
        x="a",
        y="b",
    )


@pytest.mark.anyio
async def test_signal_send_robust_will_catch_exception(signal: Signal, mocker):
    receiver_function = mocker.AsyncMock(
        side_effect=Exception("Boom!"),
        __qualname__="receiver_function",
    )

    signal.connect(receiver_function)

    await signal.send_robust(sender=test_signal_send_robust_will_catch_exception, x="a", y="b")


def test_receiver(signal: Signal):
    @receiver(signal)
    def receiver_function(**kwargs):
        pass

    assert len(signal.receivers) == 1


def test_receiver_for_signal_list(signal: Signal, signal2: Signal):
    @receiver([signal, signal2])
    def receiver_function(**kwargs):
        pass

    assert len(signal.receivers) == 1
    assert len(signal2.receivers) == 1


@pytest.mark.anyio
async def test_receivers_only_called_when_sender_matches(signal: Signal, mocker):
    receiver_function1 = mocker.AsyncMock()
    receiver_function2 = mocker.AsyncMock()

    signal.connect(receiver_function1, sender="sender1")
    signal.connect(receiver_function2, sender="sender2")

    await signal.send("sender1")

    receiver_function1.assert_called_once()
    receiver_function2.assert_not_called()
    receiver_function1.reset_mock()
    receiver_function2.reset_mock()

    await signal.send("sender2")

    receiver_function1.assert_not_called()
    receiver_function2.assert_called_once()
    receiver_function1.reset_mock()
    receiver_function2.reset_mock()

    await signal.send("sender3")

    receiver_function1.assert_not_called()
    receiver_function2.assert_not_called()
