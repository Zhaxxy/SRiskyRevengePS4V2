def get_bits(packed_bits: int, packed_bits_length: int, bits_offset: int, bits_length: int) -> int:
    if not(packed_bits >= 0 and packed_bits_length >= 0 and bits_offset >= 0 and bits_length >= 0): raise ValueError('No neagtive values allowed')
    
    if not(bits_offset + bits_length <= packed_bits_length): raise ValueError('Invalid bit offset or length')

    shift_amount = packed_bits_length - bits_offset - bits_length
    
    mask = 2**bits_length-1
    mask <<= shift_amount
    
    return (packed_bits & mask) >> shift_amount


def set_bits(packed_bits: int, packed_bits_length: int, bits_offset: int, bits_length: int, value: int) -> int:
    print(value)
    if not(packed_bits >= 0 and packed_bits_length >= 0 and bits_offset >= 0 and bits_length >= 0 and value >= 0): raise ValueError('No neagtive values allowed')
    
    
    bits_offset_plus_bits_length = bits_offset + bits_length
    
    if not(bits_offset_plus_bits_length <= packed_bits_length): raise ValueError('Invalid bit offset or length')
    
    max_value = 2**bits_length-1
    if not(value <= max_value): raise OverflowError(f'Value {value} is too big, max is {max_value}')

    # get first bits
    first_bits = get_bits(packed_bits,packed_bits_length,0,bits_offset)
    
    # get last bits
    last_bits_length = packed_bits_length - bits_offset_plus_bits_length
    last_bits = get_bits(packed_bits,packed_bits_length,bits_offset_plus_bits_length,last_bits_length)

    # concacntae them togegther
    return (((first_bits << bits_length) | value) << last_bits_length) | last_bits


def main():
    a = 0x6d_ff
    al = 16
    b = 6
    c = 10
    
    v = get_bits(a,al,b,c) 
    assert v == 511
    assert set_bits(a,al,b,c,511) == a 
    
    m = set_bits(a,al,b,c,0x9)
    
    
    
    assert get_bits(m,al,b,c) == 9
    
    print(v)
    print(hex(m))


if __name__ == '__main__':
    main()