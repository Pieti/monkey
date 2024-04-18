from monkey.mobj import (NULL, Array, Builtin, Error, Integer, MonkeyObject,
                         String)


def _len(*args: MonkeyObject) -> MonkeyObject:
    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")
    if isinstance(args[0], Array):
        return Integer(len(args[0].elements))
    if isinstance(args[0], String):
        return Integer(len(args[0].value))
    return Error(f"argument to `len` not supported, got {args[0].monkey_type}")


def _first(*args: MonkeyObject) -> MonkeyObject:
    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")
    if not isinstance(args[0], Array):
        return Error(f"argument to `first` must be ARRAY, got {args[0].monkey_type}")
    if len(args[0].elements) > 0:
        return args[0].elements[0]
    return NULL


def _last(*args: MonkeyObject) -> MonkeyObject:
    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")
    if not isinstance(args[0], Array):
        return Error(f"argument to `last` must be ARRAY, got {args[0].monkey_type}")
    if len(args[0].elements) > 0:
        return args[0].elements[-1]
    return NULL


def _rest(*args: MonkeyObject) -> MonkeyObject:
    if len(args) != 1:
        return Error(f"wrong number of arguments. got={len(args)}, want=1")
    if not isinstance(args[0], Array):
        return Error(f"argument to `rest` must be ARRAY, got {args[0].monkey_type}")
    if len(args[0].elements) > 0:
        return Array(args[0].elements[1:])
    return NULL


def _push(*args: MonkeyObject) -> MonkeyObject:
    if len(args) != 2:
        return Error(f"wrong number of arguments. got={len(args)}, want=2")
    if not isinstance(args[0], Array):
        return Error(f"argument to `push` must be ARRAY, got {args[0].monkey_type}")
    new_elements = args[0].elements.copy()
    new_elements.append(args[1])
    return Array(new_elements)


def _puts(*args: MonkeyObject) -> MonkeyObject:
    for arg in args:
        print(str(arg))
    return NULL


BUILTINS: dict[str, Builtin] = {
    "len": Builtin(_len),
    "first": Builtin(_first),
    "last": Builtin(_last),
    "rest": Builtin(_rest),
    "push": Builtin(_push),
    "puts": Builtin(_puts),
}
