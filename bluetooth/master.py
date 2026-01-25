import serial

PORT = "COM5"   # set to the machine's SPP "Incoming" port
BAUD = 115200

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    print(f"SPP server listening on {PORT} …")
    n = 0
    while True:
        # send a line every 2s, like your broadcaster
        msg = f"Hello laptops! msg={n}\n".encode()
        ser.write(msg)
        print("TX:", msg.decode().strip())

        # also read anything from the peer (optional)
        line = ser.readline()
        if line:
            print("RX:", line.decode(errors="ignore").rstrip())

        n += 1
        import time; time.sleep(2)
