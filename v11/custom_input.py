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
    key_map = {
        'escape': 0x01,
        'esc': 0x01,
        'f1': 0x3B,
        'f2': 0x3C,
        'f3': 0x3D,
        'f4': 0x3E,
        'f5': 0x3F,
        'f6': 0x40,
        'f7': 0x41,
        'f8': 0x42,
        'f9': 0x43,
        'f10': 0x44,
        'f11': 0x57,
        'f12': 0x58,
        'printscreen': 0xB7,
        'prntscrn': 0xB7,
        'prtsc': 0xB7,
        'prtscr': 0xB7,
        'scrolllock': 0x46,
        'pause': 0xC5,
        '`': 0x29,
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
        '-': 0x0C,
        '=': 0x0D,
        'backspace': 0x0E,
        'insert': 0xD2 + 1024,
        'home': 0xC7 + 1024,
        'pageup': 0xC9 + 1024,
        'pagedown': 0xD1 + 1024,
        # numpad
        'numlock': 0x45,
        'divide': 0xB5 + 1024,
        'multiply': 0x37,
        'subtract': 0x4A,
        'add': 0x4E,
        'decimal': 0x53,
        'numpadenter': 0x9C + 1024,
        'numpad1': 0x4F,
        'numpad2': 0x50,
        'numpad3': 0x51,
        'numpad4': 0x4B,
        'numpad5': 0x4C,
        'numpad6': 0x4D,
        'numpad7': 0x47,
        'numpad8': 0x48,
        'numpad9': 0x49,
        'numpad0': 0x52,
        # end numpad
        'tab': 0x0F,
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
        '[': 0x1A,
        ']': 0x1B,
        '\\': 0x2B,
        'del': 0xD3 + 1024,
        'delete': 0xD3 + 1024,
        'end': 0xCF + 1024,
        'capslock': 0x3A,
        'a': 0x1E,
        's': 0x1F,
        'd': 0x20,
        'f': 0x21,
        'g': 0x22,
        'h': 0x23,
        'j': 0x24,
        'k': 0x25,
        'l': 0x26,
        ';': 0x27,
        "'": 0x28,
        'enter': 0x1C,
        'return': 0x1C,
        'shift': 0x2A,
        'shiftleft': 0x2A,
        'z': 0x2C,
        'x': 0x2D,
        'c': 0x2E,
        'v': 0x2F,
        'b': 0x30,
        'n': 0x31,
        'm': 0x32,
        ',': 0x33,
        '.': 0x34,
        '/': 0x35,
        'shiftright': 0x36,
        'ctrl': 0x1D,
        'ctrlleft': 0x1D,
        'win': 0xDB + 1024,
        'winleft': 0xDB + 1024,
        'alt': 0x38,
        'altleft': 0x38,
        ' ': 0x39,
        'space': 0x39,
        'altright': 0xB8 + 1024,
        'winright': 0xDC + 1024,
        'apps': 0xDD + 1024,
        'ctrlright': 0x9D + 1024,
        'up': MapVirtualKey(0x26, MAPVK_VK_TO_VSC),
        'left': MapVirtualKey(0x25, MAPVK_VK_TO_VSC),
        'down': MapVirtualKey(0x28, MAPVK_VK_TO_VSC),
        'right': MapVirtualKey(0x27, MAPVK_VK_TO_VSC),
    }

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

    def press_key(hexKeyCode, key="T"):
        if key in ["up", "down", "left", "right"]:
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

    def release_key(hexKeyCode, key="T"):
        keybdFlags = 0x0008 | 0x0002
        if key in ["up", "down", "left", "right"]:
            keybdFlags |= 0x0001
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hexKeyCode, keybdFlags,
                            0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

        if key in ["up", "down", "left", "right"] and ctypes.windll.user32.GetKeyState(0x90):
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
