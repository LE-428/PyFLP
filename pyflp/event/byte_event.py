import enum
from typing import Union

from pyflp.event.event import Event
from pyflp.utils import WORD

class ByteEvent(Event):
    """Represents a byte-sized event
 
    Raises:
        ValueError & TypeError
    """
    
    @property
    def size(self) -> int:
        return 2
    
    def __repr__(self) -> str:
        return f"ByteEvent ID: {self.id} Data: {self.to_uint8()} (Index: {self.index})"

    def dump(self, new_data: Union[bytes, int, bool]):
        if isinstance(new_data, bytes):
            if len(new_data) != 1:
                raise ValueError(f"Expected a bytes object of 1 byte length; got {new_data}")
            self.data = new_data
        elif isinstance(new_data, int):
            if new_data != abs(new_data):
                if new_data not in range(-128, 128):
                    raise ValueError(f"Expected a value of -128 to 127; got {new_data}")
            else:
                if new_data > 255:
                    raise ValueError(f"Expected a value of 0 to 255; got {new_data}")
            self.data = new_data.to_bytes(1, 'little')
        elif isinstance(new_data, bool):
            data = 1 if new_data else 0
            self.data = data.to_bytes(1, 'little')
        else:
            raise TypeError(f"Expected a bytes, bool or an int object; got {type(new_data)}")
    
    def to_uint8(self) -> int:
        return int.from_bytes(self.data, 'little')
    
    def to_int8(self) -> int:
        return int.from_bytes(self.data, 'little', signed=True)
    
    def to_bool(self) -> bool:
        return self.to_int8() != 0
    
    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        if not id < WORD:
            raise ValueError(f"Exepcted 0-63; got {id}")
        super().__init__(id, data)