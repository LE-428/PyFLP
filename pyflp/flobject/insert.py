import enum
from typing import (
    List,
    Optional,
    Union
)

from flobject.flobject import *
from flobject.insertslot import InsertSlot, InsertSlotEventID
from utils import *
from bytesioex import BytesIOEx

@enum.unique
class InsertEventID(enum.IntEnum):
    Parameters = DATA + 27
    Color = DWORD + 21
    Name = TEXT + 12
    Icon = WORD + 31
    Routing = DATA + 26
    Output = DWORD + 19
    Input = DWORD + 26

class InsertFlags(enum.IntFlag):
    None_ = 0x00
    ReversePolarity = 0x01
    SwapLeftRight = 0x02
    U1 = 0x04
    Enabled = 0x08
    AllowThreadedProcessing = 0x10
    U2 = 0x20
    DockMiddle = 0x40
    DockRight = 0x80
    ShowSeperator = 0x0400

class Insert(FLObject):
    _count = 0
    max_count = 1	# Will be a given a value by ProjectParser

    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)
    
    @name.setter
    def name(self, value: str):
        self.setprop('name', value)
    
    @property
    def routing(self) -> Optional[bytes]:
        return getattr(self, '_routing', None)
    
    @routing.setter
    def routing(self, value: bytes):
        self.setprop('routing', value)
    
    @property
    def icon(self) -> Optional[int]:
        return getattr(self, '_icon', None)
    
    @icon.setter
    def icon(self, value: int):
        self.setprop('icon', value)
    
    @property
    def input(self) -> Optional[int]:
        return getattr(self, '_input', None)
    
    @input.setter
    def input(self, value: int):
        self.setprop('input', value)
    
    @property
    def output(self) -> Optional[int]:
        return getattr(self, '_output', None)
    
    @output.setter
    def output(self, value: int):
        self.setprop('output', value)
    
    @property
    def color(self) -> Optional[int]:
        return getattr(self, '_color', None)
    
    @color.setter
    def color(self, value: int):
        self.setprop('color', value)
    
    @property
    def flags(self) -> Union[InsertFlags, int, None]:
        return getattr(self, '_flags', None)
    
    @flags.setter
    def flags(self, value: Union[InsertFlags, int]):
        self._parameters_data.seek(0)
        self._parameters_data.write(value.to_bytes(4, 'little'))
        self._events['parameters'].dump(self._parameters_data.read())
    
    @property
    def slots(self) -> List[InsertSlot]:
        return getattr(self, '_slots', [])

    @slots.setter
    def slots(self, value: List[InsertSlot]):
        self._slots = value

    def parse(self, event: Event) -> None:
        if event.id == InsertSlotEventID.Index:
            self._cur_slot.parse(event)
            self._slots.append(self._cur_slot)
            if len(self._slots) < InsertSlot.max_count:
                self._cur_slot = InsertSlot()
        elif event.id in (
            InsertSlotEventID.Color,
            InsertSlotEventID.Icon,
            InsertSlotEventID.PluginNew,
            InsertSlotEventID.Data
        ):
            self._cur_slot.parse(event)
        else:
            return super().parse(event)
    
    def _parse_word_event(self, event: WordEvent):
        if event.id == InsertEventID.Icon:
            self._events['icon'] = event
            self._icon = event.to_uint16()
    
    def _parse_dword_event(self, event: DWordEvent):
        if event.id == InsertEventID.Input:
            self._events['input'] = event
            self._input = event.to_int32()
        elif event.id == InsertEventID.Color:
            self._events['color'] = event
            self._color = event.to_uint32()
        elif event.id == InsertEventID.Output:
            self._events['output'] = event
            self._output = event.to_int32()
    
    def _parse_text_event(self, event: TextEvent):
        if event.id == InsertEventID.Name:
            self._events['name'] = event
            self._name = event.to_str()
        elif event.id == InsertSlotEventID.DefaultName:
            # Slot is not empty
            self._cur_slot = InsertSlot()
            self._cur_slot.parse(event)
    
    def _parse_data_event(self, event: DataEvent):
        if event.id == InsertEventID.Parameters:
            self._events['parameters'] = event
            self._parameters_data = BytesIOEx(event.data)
            self._flags = InsertFlags(self._parameters_data.read_uint32())
            # 8 more bytes
        elif event.id == InsertEventID.Routing:
            self._events['routing'] = event
            self._routing = event.data

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        self._events['routing'].dump(self._routing)
        self._parameters_data.seek(0)
        self._events['parameters'].dump(self._parameters_data.read())
        return super().save()
    
    def __init__(self):
        super().__init__()
        InsertSlot._count = 0
        self._slots: List[InsertSlot] = []
        self._cur_slot = InsertSlot()
        Insert._count += 1
        assert Insert._count <= Insert.max_count, f"Insert count: {self._count}"
        self._log.info(f"__init__(), count: {self._count}")
        self.idx = Insert._count - 2