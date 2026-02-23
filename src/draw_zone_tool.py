import cv2
import numpy as np

VIDEO_PATH = "data/videos/clip1.mp4"

points = []

def mouse_callback(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Point added: ({x}, {y})")

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to read video.")
        return

    cv2.namedWindow("Draw Zone")
    cv2.setMouseCallback("Draw Zone", mouse_callback)

    while True:
        temp = frame.copy()
        for p in points:
            cv2.circle(temp, p, 5, (0, 255, 0), -1)

        if len(points) > 1:
            cv2.polylines(temp, [np.array(points)], False, (0, 255, 255), 2)

        cv2.imshow("Draw Zone", temp)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    print("Final Points:", points)

if __name__ == "__main__":
    main()
