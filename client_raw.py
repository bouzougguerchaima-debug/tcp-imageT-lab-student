
import socket
import struct
import time
import cv2
import numpy as np

SERVER_IP = '127.0.0.1'
PORT = 8080

IMAGE_PATH = 'test_image.jpg'
WIDTH = 640
HEIGHT = 480
mode = 'pixel_by_pixel'


def generate_test_image(filename, width, height):
    # 1. Create a blank dark-gray canvas
    image = np.full((height, width, 3), 40, dtype=np.uint8)

    # 2. Add a diagonal color gradient
    for y in range(height):
        for x in range(width):
            image[y, x, 0] = int((x / width) * 255)
            image[y, x, 1] = int((y / height) * 255)

    # 3. Draw geometric shapes
    center_coordinates = (width // 2, height // 2)
    cv2.circle(image, center_coordinates, 80, (0, 0, 255), -1)

    cv2.rectangle(image, (50, 50), (200, 150), (0, 255, 255), 3)

    cv2.line(image, (50, height - 50),
             (width - 50, height - 50), (0, 255, 0), 4)

    # 4. Add text
    font = cv2.FONT_HERSHEY_SIMPLEX

    cv2.putText(image, 'TCP IMAGE TEST',
                (width // 2 - 140, 60), font, 1.0,
                (255, 255, 255), 2)

    cv2.putText(image, f'{width}x{height} px',
                (width // 2 - 60, height // 2 + 120),
                font, 0.7, (255, 255, 255), 1)

    # 5. Save image
    cv2.imwrite(filename, image)

    print(f"Test image generated: {filename}")


def send_pixel_by_pixel(sock, header, img):
    """Send header and every pixel separately."""

    height, width, channels = img.shape

    sock.sendall(header)
    calls = 1

    for y in range(height):
        for x in range(width):
            sock.sendall(img[y, x].tobytes())
            calls += 1

    return calls


def run_client():

    # TODO 1: Prepare the generated test image
    generate_test_image(IMAGE_PATH, WIDTH, HEIGHT)

    img = cv2.imread(IMAGE_PATH)

    if img is None:
        print(f"Error: {IMAGE_PATH} not found.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Disable Nagle's algorithm
    client_socket.setsockopt(
        socket.IPPROTO_TCP,
        socket.TCP_NODELAY,
        1
    )

    try:
        client_socket.connect((SERVER_IP, PORT))

        print(f"Connected to server at {SERVER_IP}:{PORT} (mode: {mode})")

        # TODO 2: Get image dimensions
        height, width, channels = img.shape

        payload = img.tobytes()
        payload_length = len(payload)

        # TODO 3: Construct fixed-size header
        header = struct.pack('!HHI',
                             height,
                             width,
                             payload_length)

        # TODO 4: Transmit header and raw pixel data
        start_time = time.time()

        calls = send_pixel_by_pixel(client_socket, header, img)

        elapsed = time.time() - start_time

        throughput = (
            (payload_length + len(header)) /
            elapsed / (1024 * 1024)
        )

        print(
            f"Sent raw image {width}x{height}x{channels} "
            f"({payload_length} bytes) in {elapsed:.4f} seconds "
            f"using {calls} send call(s) "
            f"({throughput:.2f} MB/s)."
        )

    finally:
        client_socket.close()


if __name__ == '__main__':
    run_client()

