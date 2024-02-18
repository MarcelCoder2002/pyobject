from inspect import FrameInfo, getframeinfo, isclass
from sys import _getframe


def stack(n: int = 0) -> list[FrameInfo]:
    i = 1 if n != 0 else n
    frame = _getframe(i)
    framelist = []
    while frame and i <= n:
        traceback_info = getframeinfo(frame, 1)
        frameinfo = (frame,) + traceback_info
        framelist.append(FrameInfo(*frameinfo, positions=traceback_info.positions))
        frame = frame.f_back
        if n != 0:
            i += 1
    return framelist


def getBase(__object, __type):
    if isclass(__type):
        base_type = __type
    else:
        base_type = type(__type)
    bases = ()
    if (isclass(__object)):
        if __object is base_type:
            return base_type
        bases = __object.__bases__
    else:
        owner = type(__object)
        if owner is base_type:
            return base_type
        bases = owner.__bases__
    if bases == (object,):
        if __type is not object:
            return None
        return object
    else:
        for base in bases:
            if issubclass(base, base_type):
                return base
            else:
                r = getBase(base, base_type)
    return r


def getBaseByQualname(__object, qualname: str):
    bases = ()
    if (isclass(__object)):
        if __object.__qualname__ == qualname:
            return __object
        bases = __object.__bases__
    else:
        owner = type(__object)
        if owner.__qualname__ is qualname:
            return owner
        bases = owner.__bases__
    if bases == (object,):
        if qualname != object.__qualname__:
            return None
        return object
    else:
        for base in bases:
            if base.__qualname__ == qualname:
                return base
            else:
                r = getBaseByQualname(base, qualname)
    return r


def getBaseByName(__object, name: str, __class=None):
    bases = ()
    if (isclass(__object)):
        if __object.__name__ == name:
            return __object
        bases = __object.__bases__
    else:
        owner = type(__object)
        if owner.__name__ is name:
            return owner
        bases = owner.__bases__
    if bases == (object,):
        if name != 'object':
            return None
        return object
    else:
        for base in bases:
            if base.__name__ == name:
                if __class is not None:
                    if not isclass(__class):
                        __class = type(__class)
                    if issubclass(base, __class):
                        return base
                else:
                    return base
                r = None
            else:
                r = getBaseByName(base, name, __class)
    return r


if __name__ == '__main__':
    pass