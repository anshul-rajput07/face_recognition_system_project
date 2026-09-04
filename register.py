import cv2
from pathlib import Path


FACE_CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# Where student photos will be stored
DATA_DIR = Path("data/faces")


def create_student_folder(student_id: str) -> Path:
    folder = DATA_DIR / student_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def register_student() -> None:
    student_id = input("Enter Student ID: ").strip()
    name = input("Enter Student Name: ").strip()

    if not student_id or not name:
        print("Student ID and name are required.")
        return

    student_folder = create_student_folder(student_id)

    detector = cv2.CascadeClassifier(FACE_CASCADE)

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Could not open camera.")
        return

    print("\nCamera opened.")
    print("Look at the camera.")
    print("Press SPACE to capture.")
    print("Press Q to quit.\n")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read camera frame.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100),
            )

            for x, y, w, h in faces:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    "Press SPACE to capture",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            cv2.imshow("Student Registration", frame)

            key = cv2.waitKey(1) & 0xFF

            # SPACE
            if key == 32:

                if len(faces) == 0:
                    print("No face detected. Try again.")
                    continue

                if len(faces) > 1:
                    print("More than one face detected. Please keep only one person in view.")
                    continue

                x, y, w, h = faces[0]

                face_image = frame[y:y + h, x:x + w]

                image_path = student_folder / "face.jpg"

                cv2.imwrite(str(image_path), face_image)

                print(f"\nRegistration successful!")
                print(f"Name: {name}")
                print(f"Student ID: {student_id}")
                print(f"Photo saved at: {image_path}")

                break

            # Q
            if key == ord("q"):
                print("Registration cancelled.")
                break


    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    register_student()