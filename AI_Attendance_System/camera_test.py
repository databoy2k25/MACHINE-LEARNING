import cv2


def main():

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Could not access the webcam.")
        return

    print("Webcam started successfully.")
    print("Press Q to quit.")

    while True:

        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read frame from webcam.")
            break

        cv2.imshow(
            "AI Attendance System - Webcam Test",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

    print("Webcam released successfully.")


if __name__ == "__main__":
    main()