import struct
import time

if __name__ == "__main__":
    with open('/dev/cpu_dma_latency', 'wb') as f:
        f.write(struct.pack('H', 1))
        while True:
            time.sleep(1)
