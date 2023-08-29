import serial
import time
import random

# Replace 'COM4' with the appropriate serial port
ser = serial.Serial('COM4', 9600)

def send_pixel_data(pixel_index, r, g, b):
    ser.write(r.to_bytes(1, byteorder='big'))
    ser.write(g.to_bytes(1, byteorder='big'))
    ser.write(b.to_bytes(1, byteorder='big'))
    ser.write(pixel_index.to_bytes(1, byteorder='big'))

    response = ser.read().decode('utf-8')
    return response

def generate_random_pixel_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b

num_pixels = 46  # Number of pixels in the LED strip

for pixel_index in range(num_pixels):
    r, g, b = generate_random_pixel_color()
    response = send_pixel_data(pixel_index, r, g, b)
    if response == 'A':
        print(f"Pixel {pixel_index} updated successfully.")

ser.close()
