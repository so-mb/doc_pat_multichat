import socket
import threading
import sys
import json
from chatui import init_windows, read_command, print_message, end_windows

# Constants
HEADER_LENGTH = 2

# Handle command line arguments
if len(sys.argv) != 4:
    print("Usage: python chat_client.py <nickname> <server_address> <port>")
    sys.exit(1)

nickname = sys.argv[1]
server_address = sys.argv[2]
port = int(sys.argv[3])

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_address, port))

# Send initial "hello" packet
hello_packet = json.dumps({"type": "hello", "nick": nickname})
client_socket.send(len(hello_packet).to_bytes(HEADER_LENGTH, byteorder='big') + hello_packet.encode('utf-8'))

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            data_length = int.from_bytes(client_socket.recv(HEADER_LENGTH), byteorder='big')
            data = client_socket.recv(data_length).decode('utf-8')
            message = json.loads(data)

            if message['type'] == 'chat':
                print_message(f"{message['nick']}: {message['message']}")
            elif message['type'] == 'join':
                print_message(f"*** {message['nick']} has joined the chat")
            elif message['type'] == 'leave':
                print_message(f"*** {message['nick']} has left the chat")
        except:
            print_message("*** Connection to server lost")
            break

# Function to send messages to the server
def send_message():
    print_message(f"*** You are chatting as << {nickname} >>", f"{nickname}> ")
    while True:
        message = read_command(f"Me> ")
        if message.strip() == "":
            continue
        if message.startswith('/q'):
            print("*** Quitting chat")
            break

        chat_packet = json.dumps({"type": "chat", "message": message})
        client_socket.send(len(chat_packet).to_bytes(HEADER_LENGTH, byteorder='big') + chat_packet.encode('utf-8'))
        # Show the message in the sender's terminal as "Me"
        print_message(f"Me: {message}")

    client_socket.close()
    end_windows()
    sys.exit(0)

# Initialize TUI
init_windows()

# Start the receiving thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Start the sending thread
send_message()
