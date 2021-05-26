import ctypes

SendInput = ctypes.windll.user32.SendInput
MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_UNICODE = 0x0004
MAPVK_VK_TO_CHAR = 2
MAPVK_VK_TO_VSC = 0
MAPVK_VSC_TO_VK = 1
MAPVK_VSC_TO_VK_EX = 3
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


class CustomInput():
    def grab_key_dict():
        KEYBOARD_MAPPING = {
            '1': 0x02,
            '2': 0x03,
            '3': 0x04,
            '4': 0x05,
            '5': 0x06,
            '6': 0x07,
            '7': 0x08,
            '8': 0x09,
            '9': 0x0A,
            '0': 0x0B,
            'q': 0x10,
            'w': 0x11,
            'e': 0x12,
            'r': 0x13,
            't': 0x14,
            'y': 0x15,
            'u': 0x16,
            'i': 0x17,
            'o': 0x18,
            'p': 0x19,
            'a': 0x1E,
            's': 0x1F,
            'd': 0x20,
            'f': 0x21,
            'g': 0x22,
            'h': 0x23,
            'j': 0x24,
            'k': 0x25,
            'l': 0x26,
            'z': 0x2C,
            'x': 0x2D,
            'c': 0x2E,
            'v': 0x2F,
            'b': 0x30,
            'n': 0x31,
            'm': 0x32,
            'up': MapVirtualKey(0x26, MAPVK_VK_TO_VSC),
            'left': MapVirtualKey(0x25, MAPVK_VK_TO_VSC),
            'down': MapVirtualKey(0x28, MAPVK_VK_TO_VSC),
            'right': MapVirtualKey(0x27, MAPVK_VK_TO_VSC),
        }
        return KEYBOARD_MAPPING

    def press_key(hexKeyCode):
        if hexKeyCode in [75, 76, 77, 78]:
            # Do the primary key
            hexKeyCode2 = 0xE0
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode2, 0x0008,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            # then the arrow itself
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0001,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))
            SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

        else:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_key(hexKeyCode):
        keybdFlags = 0x0008 | 0x0002
        if hexKeyCode in [75, 76, 77, 78]:
            keybdFlags |= 0x0001
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hexKeyCode, keybdFlags,
                            0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

        if hexKeyCode in [75, 76, 77, 78] and ctypes.windll.user32.GetKeyState(0x90):
            hexKeyCode = 0xE0
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))

    def left_click(x, y):
        pass

    def window_left_click(x, y, window):
        pass
