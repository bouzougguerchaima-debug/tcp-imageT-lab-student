
import socket
import struct
import time
import cv2
import numpy as np

PORT = 8080
HEADER_SIZE = 8  # 2 bytes height + 2 bytes width + 4 bytes payload length


def recv_exact(sock, n):
    """Read exactly n bytes from a TCP stream."""
    data = b''

    while len(data) < n:
        packet = sock.recv(n - len(data))

        if not packet:
            return None

        data += packet

    return data


def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)

    print(f"Server listening on port {PORT}...")
    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    try:
        if not conn.recv(1, socket.MSG_PEEK):
            print("Client closed the connection without sending data.")
            return

        start_time = time.time()

        # TODO 5: Read the header
        header = recv_exact(conn, HEADER_SIZE)

        if header is None:
            print("Error: incomplete header.")
            return

        # TODO 6: Unpack the header
        height, width, payload_length = struct.unpack('!HHI', header)

        print(f"Header received: {width}x{height}, payload = {payload_length} bytes")

        pixels = height * width

        if pixels == 0 or payload_length % pixels != 0:
            print("Error: payload length does not match the image dimensions.")
            return

        # TODO 7: Read the payload
        payload = recv_exact(conn, payload_length)

        if payload is None:
            print("Error: incomplete image payload.")
            return

        # TODO 8: Reconstruct the image
        channels = payload_length // pixels

        image_array = np.frombuffer(payload, dtype=np.uint8)
        image = image_array.reshape((height, width, channels))

        # TODO 9: Calculate network performance metrics
        end_time = time.time()

        transfer_time = end_time - start_time

        latency_ms = transfer_time * 1000
        packet_loss = 0.0
        throughput_kbps = (HEADER_SIZE + payload_length) / 1024 / transfer_time

        print(f"Raw Transfer Complete | Size: {HEADER_SIZE + payload_length} bytes")
        print(f"Metrics | Latency: {latency_ms:.3f} ms | Packet loss: {packet_loss:.2f} % | "
              f"Throughput: {throughput_kbps:.2f} KB/s")

        cv2.imshow("Received Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    finally:
        conn.close()
        server_socket.close()


if __name__ == '__main__':
    run_server()

