import serial, time

PORT = "COM3"   # set to this laptop's SPP "Outgoing" port to the other machine
BAUD = 115200

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    print(f"SPP client connected on {PORT} …")
    while True:
        line = ser.readline()
        if line:
            print("RX:", line.decode(errors="ignore").rstrip())
        # (optional) reply back
        # ser.write(b"ack\n")
        time.sleep(0.05)