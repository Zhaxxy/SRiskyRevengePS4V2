import struct
from io import BytesIO
from typing import Any, NamedTuple

class CoordsLayerAndArea(NamedTuple):
    x_coord: int
    y_coord: int
    area_id: int
    current_layer: int

#temp fix
try: import ss as so
except ModuleNotFoundError: import SRiskyRevengePS4V2.ss as so
try: from bit_packing_tools import get_bits, set_bits
except ModuleNotFoundError: from SRiskyRevengePS4V2.bit_packing_tools import get_bits, set_bits


def jhash_mix(a, b, c):
    '''mix() -- mix 3 32-bit values reversibly.
For every delta with one or two bits set, and the deltas of all three
  high bits or all three low bits, whether the original value of a,b,c
  is almost all zero or is uniformly distributed,
* If mix() is run forward or backward, at least 32 bits in a,b,c
  have at least 1/4 probability of changing.
* If mix() is run forward, every bit of c will change between 1/3 and
  2/3 of the time.  (Well, 22/100 and 78/100 for some 2-bit deltas.)'''
    # Need to constrain U32 to only 32 bits using the & 0xffffffff 
    # since Python has no native notion of integers limited to 32 bit
    # http://docs.python.org/library/stdtypes.html#numeric-types-int-float-long-complex
    a &= 0xffffffff; b &= 0xffffffff; c &= 0xffffffff
    a -= b; a -= c; a ^= (c>>13); a &= 0xffffffff
    b -= c; b -= a; b ^= (a<<8); b &= 0xffffffff
    c -= a; c -= b; c ^= (b>>13); c &= 0xffffffff
    a -= b; a -= c; a ^= (c>>12); a &= 0xffffffff
    b -= c; b -= a; b ^= (a<<16); b &= 0xffffffff
    c -= a; c -= b; c ^= (b>>5); c &= 0xffffffff
    a -= b; a -= c; a ^= (c>>3); a &= 0xffffffff
    b -= c; b -= a; b ^= (a<<10); b &= 0xffffffff
    c -= a; c -= b; c ^= (b>>15); c &= 0xffffffff
    return a, b, c

def jhash(data, initval = 0):
    '''Implements a straight Jenkins lookup hash - http://burtleburtle.net/bob/hash/doobs.html

    Usage: 
        from jhash import jhash
        print jhash(b'My hovercraft is full of eels')

    Returns: unsigned 32 bit integer value

    Prereqs: None

    Tested with Python 2.6.
    Version 1.00 - der@dod.no - 23.08.2010

    Partly based on the Perl module Digest::JHash
    http://search.cpan.org/~shlomif/Digest-JHash-0.06/lib/Digest/JHash.pm

    Original copyright notice:
        By Bob Jenkins, 1996.  bob_jenkins@burtleburtle.net.  You may use this
        code any way you wish, private, educational, or commercial.  It's free.

        See http://burtleburtle.net/bob/hash/evahash.html
        Use for hash table lookup, or anything where one collision in 2^^32 is
        acceptable.  Do NOT use for cryptographic purposes.
    '''

    '''hash() -- hash a variable-length key into a 32-bit value
  data    : the key (the unaligned variable-length array of bytes)
  initval : can be any 4-byte value, defaults to 0
Returns a 32-bit value.  Every bit of the key affects every bit of
the return value.  Every 1-bit and 2-bit delta achieves avalanche.'''
    length = lenpos = len(data)

    # empty string returns 0
    if length == 0:
        return 0

    # Set up the internal state
    a = b = 0x9e3779b9 # the golden ratio; an arbitrary value
    c = initval        # the previous hash value
    p = 0              # string offset

    # ------------------------- handle most of the key in 12 byte chunks
    while lenpos >= 12:
        a += ((data[p+0]) + ((data[p+1])<<8) + ((data[p+2])<<16) + ((data[p+3])<<24))
        b += ((data[p+4]) + ((data[p+5])<<8) + ((data[p+6])<<16) + ((data[p+7])<<24))
        c += ((data[p+8]) + ((data[p+9])<<8) + ((data[p+10])<<16) + ((data[p+11])<<24))
        a, b, c = jhash_mix(a, b, c)
        p += 12
        lenpos -= 12

    # ------------------------- handle the last 11 bytes
    c += length
    if lenpos >= 11: c += (data[p+10])<<24
    if lenpos >= 10: c += (data[p+9])<<16
    if lenpos >= 9:  c += (data[p+8])<<8
    # the first byte of c is reserved for the length
    if lenpos >= 8:  b += (data[p+7])<<24
    if lenpos >= 7:  b += (data[p+6])<<16
    if lenpos >= 6:  b += (data[p+5])<<8
    if lenpos >= 5:  b += (data[p+4])
    if lenpos >= 4:  a += (data[p+3])<<24
    if lenpos >= 3:  a += (data[p+2])<<16
    if lenpos >= 2:  a += (data[p+1])<<8
    if lenpos >= 1:  a += (data[p+0])
    a, b, c = jhash_mix(a, b, c)

    # ------------------------- report the result
    return c


class BytesIORS(BytesIO):
    def rs(self,seek_number,read_number,*,seek_to_previous = False):
        return_seek = self.tell()
        
        self.seek(seek_number)
        returing = self.read(read_number)
        
        if seek_to_previous:
            self.seek(return_seek)
        else:
            self.seek(0)
        
        return returing 
    def ws(self,seek_number,write_bytes,*,seek_to_previous = False):
            return_seek = self.tell()

            self.seek(seek_number)
            self.write(write_bytes)

            if seek_to_previous:
                 self.seek(return_seek)
            else:
                 self.seek(0)
        

class _InventoryItem:
    _has_been_initialised = False
    def __setattr__(self, name: str, value: Any) -> None:
        if not hasattr(self,name) and self._has_been_initialised:
            raise AttributeError(f"Attribute '{name}' does not exist")
        else:
            super().__setattr__(name, value)
    
    def __init__(self,self2,boolean_flags: tuple,count_flags: tuple=False):
        
        self._savedata = self2._savedata
        self._read_packed_int = self2._read_packed_int
        self._write_packed_int = self2._write_packed_int

        self.boolean_flags = boolean_flags
        self.count_flags = count_flags

        self._has_been_initialised = True


    @property
    def exists(self) -> bool:
        trues = [self._read_packed_int(boolean_flag) for boolean_flag in self.boolean_flags]
        assert all(element == trues[0] for element in trues)
        return trues[0]
    @exists.setter
    def exists(self, value: bool):
        for boolean_flag in self.boolean_flags:
            self._write_packed_int(boolean_flag,value)
    
    
    @property
    def count(self) -> int:
        if not self.count_flags: raise AttributeError('No attruibte for count')

        some_ints = [self._read_packed_int(count_flag) for count_flag in self.count_flags]
        assert all(element == some_ints[0] for element in some_ints)
        return some_ints[0]
    @count.setter
    def count(self, value: int):
        if not self.count_flags: raise AttributeError('No attruibte for count')
        
        for count_flag in self.count_flags:
            self._write_packed_int(count_flag,value)

class _UseItemsInventory:
    _has_been_initialised = False
    def __setattr__(self, name: str, value: Any) -> None:
        if not hasattr(self,name) and self._has_been_initialised:
            raise AttributeError(f"Attribute '{name}' does not exist")
        else:
            super().__setattr__(name, value)

    def __str__(self) -> str:
        use_items_inventory = []
        if self._read_packed_int(so.HAS_FIREBALL):
            use_items_inventory.append('fireball')
        if self._read_packed_int(so.HAS_SPITFIRE):
            use_items_inventory.append('spitfire')
        if self._read_packed_int(so.HAS_FLAMETHROWER):
            use_items_inventory.append('flamethrower')
        if self._read_packed_int(so.HAS_PIKE_BALL):
            use_items_inventory.append('pike_ball')
        if self._read_packed_int(so.HAS_SUPER_PIKE_BALL):
            use_items_inventory.append('super_pike_ball')
        if self._read_packed_int(so.HAS_MEGA_PIKE_BALL):
            use_items_inventory.append('mega_pike_ball')
        if self._read_packed_int(so.HAS_STORM_PUFF):
            use_items_inventory.append('storm_puff')
        if self._read_packed_int(so.HAS_CRUSH_PUFF):
            use_items_inventory.append('crush_puff')
        if self._read_packed_int(so.HAS_MEGA_PUFF):
            use_items_inventory.append('mega_puff')
        
        assert self._read_packed_int(so.HAS_HEALTH_VIAL1) == self._read_packed_int(so.HAS_HEALTH_VIAL2)
        assert self._read_packed_int(so.HAS_MAGIC_POTION1) == self._read_packed_int(so.HAS_MAGIC_POTION2)

        if self._read_packed_int(so.HAS_HEALTH_VIAL1):
            use_items_inventory.append({'health_vials':self._read_packed_int(so.HEALTH_VIALS)})

        if self._read_packed_int(so.HAS_MAGIC_POTION1):
            use_items_inventory.append({'magic_potions':self._read_packed_int(so.MAGIC_POTIONS)})

        if self._read_packed_int(so.HAS_MAP):
            use_items_inventory.append('map')        
        return str(use_items_inventory)

    def __init__(self,self2):
        self._savedata = self2._savedata
        self._read_packed_int = self2._read_packed_int
        self._write_packed_int = self2._write_packed_int

        assert self._read_packed_int(so.HAS_HEALTH_VIAL1) == self._read_packed_int(so.HAS_HEALTH_VIAL2)
        assert self._read_packed_int(so.HAS_MAGIC_POTION1) == self._read_packed_int(so.HAS_MAGIC_POTION2)

        self.health_vials = _InventoryItem(self2,(so.HAS_HEALTH_VIAL1,so.HAS_HEALTH_VIAL2),(so.HEALTH_VIALS,))
        self.magic_potions = _InventoryItem(self2,(so.HAS_MAGIC_POTION1,so.HAS_MAGIC_POTION2),(so.MAGIC_POTIONS,))

        self.fireball = _InventoryItem(self2,(so.HAS_FIREBALL,))
        self.spitfire = _InventoryItem(self2,(so.HAS_SPITFIRE,))
        self.flamethrower = _InventoryItem(self2, (so.HAS_FLAMETHROWER,))
        self.pike_ball = _InventoryItem(self2, (so.HAS_PIKE_BALL,))
        self.super_pike_ball = _InventoryItem(self2, (so.HAS_SUPER_PIKE_BALL,))
        self.mega_pike_ball = _InventoryItem(self2, (so.HAS_MEGA_PIKE_BALL,))
        self.storm_puff = _InventoryItem(self2, (so.HAS_STORM_PUFF,))
        self.crush_puff = _InventoryItem(self2, (so.HAS_CRUSH_PUFF,))
        self.mega_puff = _InventoryItem(self2, (so.HAS_MEGA_PUFF,))
        self.the_map = _InventoryItem(self2, (so.HAS_MAP,))
        
        self._has_been_initialised = True
        
class _KeyItemsInventory:
    _has_been_initialised = False
    def __setattr__(self, name: str, value: Any) -> None:
        if not hasattr(self,name) and self._has_been_initialised:
            raise AttributeError(f"Attribute '{name}' does not exist")
        else:
            super().__setattr__(name, value)

    def __str__(self):
        key_items_list = []

        if self._read_packed_int(so.HAS_PROHIBITION_SIGN):
            key_items_list.append('red_circle')
        if self._read_packed_int(so.HAS_HEARTS_HOLDER):
            amnt = abs(self._read_packed_int(so.HEARTS) - 3) #im pretty sure this is correct
            key_items_list.append({'hearts_holder':amnt})
        if self._read_packed_int(so.HAS_GOLDEN_SQUID_BABY):
            key_items_list.append({'golden_warp_squid_baby':self._read_packed_int(so.GOLDEN_SQUID_BABY_COUNT)})
        if self._read_packed_int(so.HAS_MONKEY_DANCE):
            key_items_list.append('monkey_dance')
        if self._read_packed_int(so.HAS_ELPHANT_DANCE):
            key_items_list.append('elephant_dance')
        if self._read_packed_int(so.HAS_MERMAID_DANCE):
            key_items_list.append('mermaid_dance')
        if self._read_packed_int(so.HAS_ATTRACT_MAGIC):
            key_items_list.append('attract_magic')
        if self._read_packed_int(so.HAS_MAGIC_FILL):
            key_items_list.append('magic_fill')
        if self._read_packed_int(so.HAS_SILKY_CREAM):
            key_items_list.append('silky_creme')
        if self._read_packed_int(so.HAS_SUPER_SILKY_CREAM):
            key_items_list.append('super_silky_creme')
        if self._read_packed_int(so.HAS_PUPPY):
            key_items_list.append('puppy')
        if self._read_packed_int(so.HAS_TASTY_MEAL):
            key_items_list.append('tasty_meal')
        if self._read_packed_int(so.HAS_SKYS_EGG):
            key_items_list.append('skys_egg')
        if self._read_packed_int(so.HAS_SCUTTLE_DEED):
            key_items_list.append('deed')
        if self._read_packed_int(so.HAS_AMMO_TOWN_PASSPORT):
            key_items_list.append('Ammo_Town_Passport_and_Activity_Book')
        if self._read_packed_int(so.HAS_COFFEE_BEANS):
            key_items_list.append('coffee_beans')
        if self._read_packed_int(so.HAS_BROKEN_COFFEE_MACHINE):
            key_items_list.append('coffee_machine')
        if self._read_packed_int(so.HAS_ZOMBIE_LATTE):
            key_items_list.append('lattee')
        if self._read_packed_int(so.HAS_FOREST_KEY):
            key_items_list.append('forest_key')
        if self._read_packed_int(so.HAS_PLASTIC_EXPLOSIVES):
            key_items_list.append('plastic_explosives')
        if self._read_packed_int(so.HAS_MONKEY_BULLET):
            key_items_list.append('monkey_bullet')
        if self._read_packed_int(so.HAS_ELPHANT_STOMP):
            key_items_list.append('elephant_stomp')
        if self._read_packed_int(so.HAS_MERMAID_BUBBLE):
            key_items_list.append('mermaid_bubble')
        if self._read_packed_int(so.HAS_TOP_HALF_SKULL):
            key_items_list.append('top_half_of_skull')
        if self._read_packed_int(so.HAS_BOTTOM_HALF_SKULL):
            key_items_list.append('bottom_half_of_skull')
        if self._read_packed_int(so.HAS_MAGIC_SEAL):
            key_items_list.append({'magic_seal':self._read_packed_int(so.MAGIC_SEALS_COUNT)})#
        if self._read_packed_int(so.HAS_MAGIC_JAM):
            key_items_list.append({'magic_jam':self._read_packed_int(so.MAGIC_JAMS_COUNT)})#
        
        return str(key_items_list)

    def __init__(self,self2):
        self._savedata = self2._savedata
        self._read_packed_int = self2._read_packed_int
        self._write_packed_int = self2._write_packed_int
        
        self.magic_seal = _InventoryItem(self2, (so.HAS_MAGIC_SEAL,), (so.MAGIC_SEALS_COUNT,))
        self.golden_warp_squid_baby =  _InventoryItem(self2, (so.HAS_GOLDEN_SQUID_BABY,), (so.GOLDEN_SQUID_BABY_COUNT,))
        self.magic_jam = _InventoryItem(self2, (so.HAS_MAGIC_JAM,), (so.MAGIC_JAMS_COUNT,))
        
        self.red_circle = _InventoryItem(self2, (so.HAS_PROHIBITION_SIGN,))
        self.hearts_holder = _InventoryItem(self2, (so.HAS_HEARTS_HOLDER,))
        self.golden_warp_squid_baby = _InventoryItem(self2, (so.HAS_GOLDEN_SQUID_BABY,))
        self.monkey_dance = _InventoryItem(self2, (so.HAS_MONKEY_DANCE,))
        self.elephant_dance = _InventoryItem(self2, (so.HAS_ELPHANT_DANCE,))
        self.mermaid_dance = _InventoryItem(self2, (so.HAS_MERMAID_DANCE,))
        self.attract_magic = _InventoryItem(self2, (so.HAS_ATTRACT_MAGIC,))
        self.magic_fill = _InventoryItem(self2, (so.HAS_MAGIC_FILL,))
        self.silky_creme = _InventoryItem(self2, (so.HAS_SILKY_CREAM,))
        self.super_silky_creme = _InventoryItem(self2, (so.HAS_SUPER_SILKY_CREAM,))
        self.puppy = _InventoryItem(self2, (so.HAS_PUPPY,))
        self.tasty_meal = _InventoryItem(self2, (so.HAS_TASTY_MEAL,))
        self.skys_egg = _InventoryItem(self2, (so.HAS_SKYS_EGG,))
        self.deed = _InventoryItem(self2, (so.HAS_SCUTTLE_DEED,))
        self.Ammo_Town_Passport_and_Activity_Book = _InventoryItem(self2, (so.HAS_AMMO_TOWN_PASSPORT,))
        self.coffee_beans = _InventoryItem(self2, (so.HAS_COFFEE_BEANS,))
        self.coffee_machine = _InventoryItem(self2, (so.HAS_BROKEN_COFFEE_MACHINE,))
        self.lattee = _InventoryItem(self2, (so.HAS_ZOMBIE_LATTE,))
        self.forest_key = _InventoryItem(self2, (so.HAS_FOREST_KEY,))
        self.plastic_explosives = _InventoryItem(self2, (so.HAS_PLASTIC_EXPLOSIVES,))
        self.monkey_bullet = _InventoryItem(self2, (so.HAS_MONKEY_BULLET,))
        self.elephant_stomp = _InventoryItem(self2, (so.HAS_ELPHANT_STOMP,))
        self.mermaid_bubble = _InventoryItem(self2, (so.HAS_MERMAID_BUBBLE,))
        self.top_half_of_skull = _InventoryItem(self2, (so.HAS_TOP_HALF_SKULL,))
        self.bottom_half_of_skull = _InventoryItem(self2, (so.HAS_BOTTOM_HALF_SKULL,))

        self._has_been_initialised = True


class _File():
    _has_been_initialised = False
    def __setattr__(self, name: str, value: Any) -> None:
        if not hasattr(self,name) and self._has_been_initialised:
            raise AttributeError(f"Attribute '{name}' does not exist")
        else:
            super().__setattr__(name, value)

    def _read_int_data(self, the_structure: so.StructuredData) -> int:
    
        new_offset = (so.MAINSAVEOFFSET + the_structure.struct_offset) + (the_structure.struct_length * (self._savenumber-1)) + the_structure.data_offset

        if the_structure.data_length == 1:
            return the_structure[-1](ord(self._savedata.rs(new_offset,the_structure.data_length)))

        bytes_data = self._savedata.rs(new_offset,the_structure.data_length)
        
        
        
        return the_structure[-1](struct.unpack(so.FORMAT_STRS[the_structure.data_length],bytes_data)[0])

    def _write_int_data(self, the_structure: so.StructuredData, value: int) -> int:
        new_offset = (so.MAINSAVEOFFSET + the_structure.struct_offset) + (the_structure.struct_length * (self._savenumber-1)) + the_structure.data_offset
        new_bytes = struct.pack(so.FORMAT_STRS[the_structure.data_length],value)

        self._savedata.ws(new_offset, new_bytes)


    def _read_packed_int(self, packed_data: so.PackedData) -> int:
        new_offset = (so.MAINSAVEOFFSET + packed_data.packed_bits_offset) + (packed_data.packed_bits_length * (self._savenumber-1))
        int_array = struct.unpack(so.FORMAT_STRS[packed_data.packed_bits_length],self._savedata.rs(new_offset,packed_data.packed_bits_length))[0]

        return packed_data[-1](get_bits(int_array,packed_data.packed_bits_length*8,packed_data.bits_offset,packed_data.bits_length))

    def _write_packed_int(self,packed_data: so.PackedData, value: int):
        new_offset = (so.MAINSAVEOFFSET + packed_data.packed_bits_offset) + (packed_data.packed_bits_length * (self._savenumber-1))
        int_array = struct.unpack(so.FORMAT_STRS[packed_data.packed_bits_length],self._savedata.rs(new_offset,packed_data.packed_bits_length))[0]

        new_int_array = set_bits(int_array,packed_data.packed_bits_length*8,packed_data.bits_offset,packed_data.bits_length,value)
        new_bytes = struct.pack(so.FORMAT_STRS[packed_data.packed_bits_length],new_int_array)

        self._savedata.ws(new_offset, new_bytes)

    def __init__(self,self2,savenumber: int):
        self._savenumber = savenumber
        self._savedata = self2._savedata

        self.key_items_inventory = _KeyItemsInventory(self)
        self.use_items_inventory = _UseItemsInventory(self)

        self._has_been_initialised = True

    @property
    def gems(self) -> int:
        return self._read_packed_int(so.GEMS)
    @gems.setter
    def gems(self,value: int):
        self._write_packed_int(so.GEMS,value)

    @property
    def hearts(self) -> int:
        return self._read_packed_int(so.HEARTS)
    @hearts.setter
    def hearts(self,value: int):
        self._write_packed_int(so.HEARTS,value)

    @property
    def is_used(self) -> bool:
        return self._read_packed_int(so.IS_USED)
    @is_used.setter
    def is_used(self,value: bool):
        self._write_packed_int(so.IS_USED,value)

    @property
    def always_running(self) -> int:
        return self._read_packed_int(so.ALWAYS_RUNNING)
    @always_running.setter
    def always_running(self,value: int):
        self._write_packed_int(so.ALWAYS_RUNNING,value)

        
    @property
    def save_file_time_frames(self) -> int:
        return self._read_int_data(so.SAVE_FILE_TIME)
    @save_file_time_frames.setter
    def save_file_time_frames(self, value: int):
        self._write_int_data(so.SAVE_FILE_TIME,value)

    
    @property
    def current_health(self) -> int:
        return self._read_int_data(so.CURRENT_HEALTH)
    @current_health.setter
    def current_health(self, value: int):
        self._write_int_data(so.CURRENT_HEALTH,value)


    @property
    def current_magic(self) -> int:
        return self._read_int_data(so.CURRENT_MAGIC)
    @current_magic.setter
    def current_magic(self, value: int):
        self._write_int_data(so.CURRENT_MAGIC,value)


    @property
    def current_y_coord(self) -> int:
        return self._read_int_data(so.CURRENT_Y_COORD)
    @current_y_coord.setter
    def current_y_coord(self, value: int):
        self._write_int_data(so.CURRENT_Y_COORD,value)
    
    @property
    def current_x_coord(self) -> int:
        return self._read_int_data(so.CURRENT_X_COORD)
    @current_x_coord.setter
    def current_x_coord(self, value: int):
        self._write_int_data(so.CURRENT_X_COORD,value)

    @property
    def area_id(self) -> int:
        return self._read_int_data(so.LOADED_AREA_ID)
    @area_id.setter
    def area_id(self, value: int):
        self._write_int_data(so.LOADED_AREA_ID,value)

    @property
    def layer(self) -> int:
        return self._read_int_data(so.CURRENT_LAYER)
    @layer.setter
    def layer(self, value: int):
        self._write_int_data(so.CURRENT_LAYER,value)


    @property
    def in_magic_mode(self) -> bool:
        return self._read_int_data(so.MAGIC_MODE)
    @in_magic_mode.setter
    def in_magic_mode(self, value: bool):
        self._write_int_data(so.MAGIC_MODE,value)


    @property
    def warp_squid_lilac_fields_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_LILAC_FIELDS)
    @warp_squid_lilac_fields_awake.setter
    def warp_squid_lilac_fields_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_LILAC_FIELDS,value)

    @property
    def warp_squid_tangle_forest_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_TANGLE_FORST)
    @warp_squid_tangle_forest_awake.setter
    def warp_squid_tangle_forest_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_TANGLE_FORST, value)

    @property
    def warp_squid_seaside_retreat_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_SEASIDE_RETREAT)
    @warp_squid_seaside_retreat_awake.setter
    def warp_squid_seaside_retreat_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_SEASIDE_RETREAT, value)

    @property
    def warp_squid_mermaid_cliffs_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_MERMAID_CLIFFS)
    @warp_squid_mermaid_cliffs_awake.setter
    def warp_squid_mermaid_cliffs_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_MERMAID_CLIFFS, value)

    @property
    def warp_squid_pumpkin_patch_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_PUMPKIN_PATCH)
    @warp_squid_pumpkin_patch_awake.setter
    def warp_squid_pumpkin_patch_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_PUMPKIN_PATCH, value)

    @property
    def warp_squid_baron_desert_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_BARON_DESERT)
    @warp_squid_baron_desert_awake.setter
    def warp_squid_baron_desert_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_BARON_DESERT, value)

    @property
    def warp_squid_sunken_caverns_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_SUNKEN_CAVERNS)
    @warp_squid_sunken_caverns_awake.setter
    def warp_squid_sunken_caverns_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_SUNKEN_CAVERNS, value)

    @property
    def warp_squid_riskys_lair_awake(self) -> bool:
        return self._read_int_data(so.WARP_SQUID_RISKYS_LAIR)
    @warp_squid_riskys_lair_awake.setter
    def warp_squid_riskys_lair_awake(self, value: bool):
        self._write_int_data(so.WARP_SQUID_RISKYS_LAIR, value)
    
    
    def file_select_show(self) -> str:
        if not self.is_used or not self.save_file_time_frames:
            return 'NEW'
        else:
            return format_ingame_time(self.save_file_time_frames)
    
    def load_area_from_player_state(self, player_state: CoordsLayerAndArea):
        self.current_x_coord = player_state.x_coord
        self.current_y_coord = player_state.y_coord
        
        self.area_id = player_state.area_id
        self.layer = player_state.current_layer
 
    def mark_save_as_used(self):
        self.is_used = True
        if self.save_file_time_frames == 0: self.save_file_time_frames = 1
        
def format_ingame_time(time_as_int: int) -> str:
    """
    format the number of frames into the format the game uses (on the File Select! menu)
    """
    seconds = time_as_int // 60
    hours, extra_seconds = divmod(seconds,3600)
    minutes = extra_seconds // 60
    return f'{hours:02d}:{minutes:02d}'

def time2ingame_time(formated_ingame_time: str,must_be_in_use=True) -> int:
    """
    the reverse of format_ingame_time
    must_be_in_use is a flag that ensures that it always returns at least 1, this is because ingame if the number is 0 the save is marked as unused, EVEN THOUGH THEY HAVE A FUCKING FLAG FOR THAT ANYWAYS
    """
    hours, minutes = formated_ingame_time.split(':')
    total_minutes = (int(hours) * 60) + int(minutes)
    return max((total_minutes * 60)*60,1) if must_be_in_use else (total_minutes * 60)*60

class InvalidRiskyRevengeSavePS4(Exception): pass
class InvalidRiskyRevengeHashPS4(InvalidRiskyRevengeSavePS4): pass

class SRiskyRevengePS4V2Loader:
    _has_been_initialised = False
    def __setattr__(self, name: str, value: Any) -> None:
        if not hasattr(self,name) and self._has_been_initialised:
            raise AttributeError(f"Attribute '{name}' does not exist")
        else:
            super().__setattr__(name, value)

    def __init__(self, savedata_sav_bytes: bytes,/,*,hash_check: bool = False):
        if len(savedata_sav_bytes) != 2048:
            raise InvalidRiskyRevengeSavePS4('Savedata is not exactly 2048 bytes, so its not a save')
        
        self._savedata = BytesIORS(savedata_sav_bytes)
        self.hash_check = hash_check
        
        if self.hash_check:
            data = self._savedata.rs(so.MAINSAVEOFFSET,so.MAINSAVELENGTH)
            original_hash = self._savedata.rs(so.MAINSAVEOFFSET-4,4)
            if struct.pack(so.FORMAT_STRS[4],jhash(data)) != original_hash:
                raise InvalidRiskyRevengeHashPS4('Hash mismatch')
        
        self.File_A = _File(self,1)
        self.File_B = _File(self,2)
        self.File_C = _File(self,3)

        self._has_been_initialised = True

    def export_save(self):
        if self.hash_check:
            data = self._savedata.rs(so.MAINSAVEOFFSET,so.MAINSAVELENGTH)
            new_hash = struct.pack(so.FORMAT_STRS[4],jhash(data))
            
            assert len(new_hash) == 4, 'wat'
            self._savedata.ws(so.MAINSAVEOFFSET-4,new_hash)
        
        return self._savedata.getvalue()
    
    def __repr__(self):
        return f'{type(self).__name__}({self._savedata.getvalue()}, hash_check = {self.hash_check})'


TP_2_FIRST_BOSS = CoordsLayerAndArea(2367487, 2949119, 213, 0)
TP_2_CHEF_HOUSE = CoordsLayerAndArea(1138688, 2031615, 208, 0)
TP_2_FINAL_CHECKPOINT = CoordsLayerAndArea(21381120, 18415615, 188, 2)
TP_2_RISKY_SHIP_PRE_FINAL_BOSS = CoordsLayerAndArea(1867776, 3145727, 190, 0)
TP_2_FINAL_BOSS = CoordsLayerAndArea(2277376, 2031615, 191, 0)

TP_2_FINAL_BOSS_BEATEN = CoordsLayerAndArea(1474560, 3145727, 192, 0)
TP_2_FINAL_CUTSCENE = CoordsLayerAndArea(3342336, 18677759, 215, 1)


def main():
    save = SRiskyRevengePS4V2Loader(open('savedata.sav','rb').read())
    save.File_A.use_items_inventory.mega_pike_balll = 4




    open('zzzzzzzz/savedata.sav','wb').write(save.export_save())
    
if __name__ == '__main__':
    main()
