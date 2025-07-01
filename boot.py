# boot.py -- run on boot-up
# This file is executed before main.py

import machine
import gc
import time

# Print boot message
print("Booting ESP32-2432S028R (Cheap Yellow Display)...")
print("MicroPython version:", gc.mem_free())

# Set CPU frequency to 240MHz for better performance
machine.freq(240000000)
print("CPU Frequency:", machine.freq() / 1000000, "MHz")

# Initialize garbage collector
gc.collect()
print("Memory free:", gc.mem_free(), "bytes")

# Small delay to allow for stable boot
time.sleep(1)

print("Boot complete. Starting main.py...")
