import ctypes
import ctypes.util
import queue
import threading
from enum import Enum, auto

# Load Objective-C runtime
objc = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")

objc_getClass = objc.objc_getClass
objc_getClass.restype = ctypes.c_void_p
objc_getClass.argtypes = [ctypes.c_char_p]

sel_registerName = objc.sel_registerName
sel_registerName.restype = ctypes.c_void_p
sel_registerName.argtypes = [ctypes.c_char_p]

objc_msgSend = objc.objc_msgSend
objc_msgSend.restype = ctypes.c_void_p
objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]


class Status(Enum):
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    SKIPPED = auto()


class Modality(Enum):
    FULL_STOP = auto()  # Stop on any non-SUCCESS (warn or error)
    STOP = auto()  # Stop on ERROR only (default)
    ELIDE = auto()  # Continue on all errors, store status
    IGNORE = auto()  # Discard all statuses, just run


class Command:
    def __init__(self, target_class, selector_name, *args):
        self.target_class = target_class
        self.selector_name = selector_name
        self.args = args

    def execute(self):
        try:
            cls = objc_getClass(self.target_class.encode("utf-8"))
            if not cls:
                return Status.ERROR
            sel = sel_registerName(self.selector_name.encode("utf-8"))
            if not sel:
                return Status.ERROR
            result = objc_msgSend(cls, sel, *self.args)
            if result is None or result == 0:
                return Status.WARNING  # treat null pointer as mild failure
            return Status.SUCCESS
        except Exception:
            return Status.ERROR


class CommandBuffer:
    def __init__(self, modality=Modality.STOP):
        self.commands = []
        self.statuses = []
        self.modality = modality
        self.skip_count = 0

    def enqueue(self, command):
        self.commands.append(command)
        self.statuses.append(None)

    def commit(self):
        for idx, cmd in enumerate(self.commands):
            status = cmd.execute()
            self.statuses[idx] = status

            # Handle modality-based flow control
            if self.modality == Modality.FULL_STOP and status != Status.SUCCESS:
                self._mark_skipped_from(idx + 1)
                break
            elif self.modality == Modality.STOP and status == Status.ERROR:
                self._mark_skipped_from(idx + 1)
                break
            elif self.modality == Modality.IGNORE:
                pass
            elif self.modality == Modality.ELIDE:
                pass

    def _mark_skipped_from(self, start_idx):
        for idx in range(start_idx, len(self.commands)):
            self.statuses[idx] = Status.SKIPPED
            self.skip_count += 1

    @property
    def percentage_successful(self):
        total = len(
            [s for s in self.statuses if s not in (None, Status.SKIPPED)]
        )
        if total == 0:
            return 0.0
        successful = len([s for s in self.statuses if s == Status.SUCCESS])
        return (successful / total) * 100

    @property
    def warning_count(self):
        return self.statuses.count(Status.WARNING)

    @property
    def error_count(self):
        return self.statuses.count(Status.ERROR)

    @property
    def completion_count(self):
        return len(
            [
                s
                for s in self.statuses
                if s in (Status.SUCCESS, Status.WARNING, Status.ERROR)
            ]
        )

    @property
    def skip_count_total(self):
        return self.skip_count


# Example Usage:
cb = CommandBuffer(modality=Modality.ELIDE)

cb.enqueue(Command("NSString", "alloc"))
cb.enqueue(Command("NonexistentClass", "alloc"))  # Will fail
cb.enqueue(Command("NSString", "description"))  # May warn or succeed

cb.commit()

print("Statuses:", cb.statuses)
print(f"Success Rate: {cb.percentage_successful:.2f}%")
print(f"Warnings: {cb.warning_count}")
print(f"Errors: {cb.error_count}")
print(f"Completions: {cb.completion_count}")
print(f"Skips: {cb.skip_count_total}")
