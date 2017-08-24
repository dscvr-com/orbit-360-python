import binascii
import struct
import time
import sys
from bluepy.btle import UUID, Peripheral

# Command characteristic UUID for Orbit360
command_uuid = UUID("69400002-b5a3-f393-e0a9-e50e24dcca99")

# This is the address of the Orbit360 to connect. You can find it using any
# bluetooth scan tool. 
p = Peripheral("C7:EA:96:09:7B:79", "random")

print("Peripheral connected")

def buildCmdXY(stepsX, stepsY, speedX, speedY):
    # Command code 3 is for moving x and y at the same time. 
    commandCode = 3

    # Convert steps for x/y into hexadecimal.
    # This tells the motor how many steps to move, 4 bytes each.
    hexStepsX = ''.join(format(x, '02x') for x in (stepsX & (2**32-1)).to_bytes(4, byteorder='big'))
    hexStepsY = ''.join(format(x, '02x') for x in (stepsy & (2**32-1)).to_bytes(4, byteorder='big'))
    # Convert speed for x/y into hexadecimal (only positive values)
    # Speed is in steps per second, 2 bytes each. 
    hexSpeedX = '{:04x}'.format(speedX)
    hexSpeedY = '{:04x}'.format(speedY)

    # Create payload and header
    # Payload is command specific, the final byte here is reserved. 
    payload = "{}{}{}{}00".format(hexStepsX, hexStepsY, hexSpeedX, hexSpeedY)
    # Header is three bytes and has the format: 0xFE, length of payload, command code. 
    header = "FE{}{}".format(format(len(payload), '02x'), format(commandCode, '02x'))

    cmd = payload + header
    
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
    chs = p.getCharacteristics(uuid=command_uuid)
    # Simple loop which allows controlling the motor via WASD
    while(True): 
        for ch in chs: 
            print(ch.uuid)
            dir = sys.stdin.read(1)
         
            if dir == 'a':
                ch.write(buildCmd(100, 0, 1000, 1000))
            if dir == 'd':
                ch.write(buildCmd(-100, 0, 1000, 1000))
            if dir == 'w':
                ch.write(buildCmd(0, 100, 1000, 1000))
            if dir == 's':
                ch.write(buildCmd(-100, 0, 1000, 1000))
            
            time.sleep(1)
finally:
    p.disconnect()
