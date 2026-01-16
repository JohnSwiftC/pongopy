import usb.core
import usb.util
import sys
import struct

dev = usb.core.find(idVendor=0x05AC, idProduct=0x4141)
if not dev:
    print("PongoOS not found")
    sys.exit(1)

try:
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
except:
    pass

dev.set_configuration()
usb.util.claim_interface(dev, 0)


def pongo_read():
    output = b""
    while True:
        status = dev.ctrl_transfer(0xA1, 2, 0, 0, 1)
        try:
            data = dev.ctrl_transfer(0xA1, 1, 0, 0, 0x1000)
            if data:
                output += bytes(data)
                print(bytes(data).decode(), end="", flush=True)
        except:
            pass
        if status[0] == 0:
            break
    return output


def pongo_send(cmd):
    if isinstance(cmd, str):
        cmd = cmd.encode()
    if not cmd.endswith(b"\n"):
        cmd += b"\n"
    dev.ctrl_transfer(0x21, 4, 1, 0, None)
    dev.ctrl_transfer(0x21, 3, 0, 0, cmd)


def pongo_upload(filename):
    with open(filename, "rb") as f:
        data = f.read()
    size = len(data)
    # Send size
    dev.ctrl_transfer(0x21, 1, 0, 0, struct.pack("<I", size))
    # Send data via bulk
    dev.write(0x02, data, timeout=60000)
    print(f"Uploaded {size} bytes")


pongo_read()

while True:
    try:
        cmd = input()
        if cmd.startswith("/send "):
            filename = cmd[6:].strip()
            pongo_upload(filename)
        else:
            pongo_send(cmd)
        pongo_read()
    except EOFError:
        break
    except KeyboardInterrupt:
        break
