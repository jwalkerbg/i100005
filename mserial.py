import serial
import time
import keyboard



# # Open the COM port
# com_port = "COM13"  # Replace with your port
# baud_rate = 115200  # Use the baud rate expected by your device

# # Initialize the serial connection
# try:
#     ser = serial.Serial(com_port, baud_rate, timeout=1)
#     print(f"Opened {com_port} successfully!")
# except serial.SerialException as e:
#     print(f"Error opening {com_port}: {e}")
#     exit(1)

# # Send data to the BLE server
# data_to_send = "Hello BLE Server!"
# try:
#     ser.write(data_to_send.encode())  # Convert string to bytes and send
#     print(f"Sent: {data_to_send}")
# except serial.SerialException as e:
#     print(f"Error writing to {com_port}: {e}")

# # Optional: Wait for a response
# time.sleep(1)  # Wait for a possible response
# if ser.in_waiting > 0:
#     response = ser.read(ser.in_waiting) # .decode()  # Read and decode response
#     print(f"Received: {response}")

# # Close the COM port
# ser.close()

# print("Running... (Press 'q' or 'Q' to exit)")

# while True:
#     print("some work....")
#     # Main loop logic
#     time.sleep(1)

#     event = keyboard.    .get_event()  # Non-blocking call to get the next event

#     if event and event.event_type == keyboard.KEY_DOWN:
#         if event.name in ['q', 'Q']:
#             print("You pressed 'q' or 'Q'. Exiting...")
#             break
#         else:
#             print(f"You pressed: {event.name}")  # Optional: Show other key presses

# Define some functions
def func1():
    return "Function 1"

def func2():
    return "Function 2"

def func3():
    return "Function 3"

# Create a list of functions
functions = [func1, func2, func3]

# Loop through the list and call each function
for i, func in enumerate(functions):
    print(f"Result from {i+1}: {func()}")


for func in functions:
    print(f"---> {func()}")

print("after loop")