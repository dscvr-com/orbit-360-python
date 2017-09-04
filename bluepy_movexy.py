import binascii
import struct
import time
import sys
from bluepy.btle import UUID, Peripheral

# Command characteristic UUID for Orbit360
command_uuid = UUID("69400002-b5a3-f393-e0a9-e50e24dcca99")

# This is the address of the Orbit360 to connect. You can find it using any
# bluetooth scan tool. 
p = Peripheral("E3:77:47:F0:4B:18", "random")

print("Peripheral connected")

def toBytes(number):
    return('%%0%dx' % (4 << 1) % number).decode('hex')[-4:]

def buildCmdXY(stepsX, stepsY, speedX, speedY):
    # Command code 3 is for moving x and y at the same time. 
    commandCode = 3

    # Convert steps for x/y into hexadecimal.
    # This tells the motor how many steps to move, 4 bytes each.
    hexStepsX = ''.join(format(x, '02x') for x in (stepsX & (2**32-1)).to_bytes(4, byteorder='big'))
    hexStepsY = ''.join(format(x, '02x') for x in (stepsY & (2**32-1)).to_bytes(4, byteorder='big'))

    # Convert speed for x/y into hexadecimal (only positive values)
    # Speed is in steps per second, 2 bytes each. 
    hexSpeedX = format(speedX, '04x')
    hexSpeedY = format(speedY, '04x')

    # Create payload and header
    # Payload is command specific, the final byte here is reserved. 
    payload = "{}{}{}{}00".format(hexStepsX, hexSpeedX, hexStepsY, hexSpeedY)
    # Header is three bytes and has the format: 0xFE, length of payload, command code. 
    header = "FE{}{}".format('{:02x}'.format(len(payload) // 2), '{:02x}'.format(commandCode))

    cmd = header + payload
   
    # Convert to binary and calc CRC checksum
    data = binascii.a2b_hex(cmd)
    crc = 0

    for b in data:
        crc += b

    # Append CRC checksum to data
    crc = crc & 0xFF
    data = data + binascii.a2b_hex('{:02x}'.format(crc))

    return data
 
try:
    ch = p.getCharacteristics(uuid=command_uuid)[0]
    # Simple loop which allows controlling the motor via WASD
    while(True): 
        dir = sys.stdin.read(1)
     
        if dir == 'a':
            ch.write(buildCmdXY(1000, 0, 1000, 1000))
        if dir == 'd':
            ch.write(buildCmdXY(-1000, 0, 1000, 1000))
        if dir == 'w':
            ch.write(buildCmdXY(0, 500, 1000, 1000))
        if dir == 's':
            ch.write(buildCmdXY(0, -500, 1000, 1000))
finally:
    p.disconnect()
