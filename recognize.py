import cv2
import time
import face_recognition
import numpy as np
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

# Laptop built-in camera
CAMERA_INDEX = 0

# Folder containing registered faces
FACES_DIR = Path("data/faces")

# Recognition threshold
# Lower = stricter
THRESHOLD = 0.50

# Process every 5th frame for better speed
PROCESS_EVERY_N_FRAMES = 5

# Automatically turn the camera off after this many seconds.
# Change to 10 or 15 as needed.
CAMERA_TIMEOUT_SECONDS = 10


# ============================================================
# STUDENT INFORMATION
# ============================================================

STUDENTS = {
    "101": "Anshul Rajput",
    "102": "Nirzara Chauhan",
    "103": "Abhishek Varshney",
    "104": "Namrata Gupta",
    "105" : "Jatin baby"
}


# ============================================================
# LOAD REGISTERED FACES
# ============================================================

def load_registered_faces():
    """
    Load all face images from:

    data/faces/101/
    data/faces/102/
    data/faces/103/
    data/faces/104/

    Each folder name is treated as the Student ID.
    """

    known_encodings = []
    known_ids = []

    if not FACES_DIR.exists():
        print("ERROR: Face data folder does not exist.")
        print(f"Expected: {FACES_DIR}")
        return known_encodings, known_ids

    print("\nLoading registered faces...\n")

    for student_folder in sorted(FACES_DIR.iterdir()):

        if not student_folder.is_dir():
            continue

        student_id = student_folder.name

        # Ignore folders that aren't in our student list
        if student_id not in STUDENTS:
            print(
                f"Skipping unknown student folder: "
                f"{student_id}"
            )
            continue

        student_name = STUDENTS[student_id]

        for image_path in sorted(student_folder.iterdir()):

            if image_path.suffix.lower() not in [
                ".jpg",
                ".jpeg",
                ".png",
            ]:
                continue

            try:

                image = face_recognition.load_image_file(
                    image_path
                )

                # Find face
                face_locations = face_recognition.face_locations(
                    image,
                    model="hog"
                )

                if len(face_locations) == 0:
                    print(
                        f"  ❌ No face: {image_path.name}"
                    )
                    continue

                if len(face_locations) > 1:
                    print(
                        f"  ❌ Multiple faces: "
                        f"{image_path.name}"
                    )
                    continue

                # Generate face encoding
                encodings = face_recognition.face_encodings(
                    image,
                    face_locations
                )

                if not encodings:
                    print(
                        f"  ❌ Encoding failed: "
                        f"{image_path.name}"
                    )
                    continue

                known_encodings.append(
                    encodings[0]
                )

                known_ids.append(
                    student_id
                )

                print(
                    f"  ✅ {student_name} "
                    f"(ID {student_id}) "
                    f"← {image_path.name}"
                )

            except Exception as error:

                print(
                    f"  ❌ Error reading "
                    f"{image_path.name}: {error}"
                )

    return known_encodings, known_ids


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("       SMARTATTEND - TEAM SHADOW")
    print("       FACE RECOGNITION SYSTEM")
    print("=" * 60)

    # --------------------------------------------------------
    # Load known faces
    # --------------------------------------------------------

    known_encodings, known_ids = (
        load_registered_faces()
    )

    if not known_encodings:

        print("\nNo registered faces found.")
        print(
            "Put face images inside "
            "data/faces/<student_id>/"
        )

        return

    print(
        f"\nLoaded {len(known_encodings)} "
        f"registered face encodings."
    )

    print("\nStudents available:")

    for student_id, student_name in STUDENTS.items():

        print(
            f"  {student_id} → {student_name}"
        )

    # --------------------------------------------------------
    # Open laptop camera
    # --------------------------------------------------------

    print(
        f"\nOpening laptop camera "
        f"(index {CAMERA_INDEX})..."
    )

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print("\n❌ Could not open laptop camera.")
        print(
            "Try CAMERA_INDEX = 1 if your laptop "
            "camera is not index 0."
        )

        return

    # --------------------------------------------------------
    # Camera resolution
    # --------------------------------------------------------

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    print("✅ Camera started.")
    print(f"Camera will automatically turn off after {CAMERA_TIMEOUT_SECONDS} seconds.")
    print("Press Q to quit.\n")

    # Start the automatic shutdown timer.
    start_time = time.monotonic()

    frame_count = 0

    # Store latest recognition results
    last_results = []

    try:

        while True:

            # ------------------------------------------------
            # Automatic camera shutdown
            # ------------------------------------------------

            elapsed = time.monotonic() - start_time

            if elapsed >= CAMERA_TIMEOUT_SECONDS:
                print(f"\n{CAMERA_TIMEOUT_SECONDS} seconds completed.")
                print("Automatically turning camera off...")
                break

            success, frame = camera.read()

            if not success:

                print("Could not read camera frame.")
                break

            frame_count += 1

            # ------------------------------------------------
            # Only process every Nth frame
            # ------------------------------------------------

            if (
                frame_count % PROCESS_EVERY_N_FRAMES
                == 0
            ):

                # Make frame smaller for faster recognition
                small_frame = cv2.resize(
                    frame,
                    None,
                    fx=0.20,
                    fy=0.20
                )

                # BGR → RGB
                rgb_frame = cv2.cvtColor(
                    small_frame,
                    cv2.COLOR_BGR2RGB
                )

                # ------------------------------------------------
                # Detect faces
                # ------------------------------------------------

                face_locations = (
                    face_recognition.face_locations(
                        rgb_frame,
                        model="hog"
                    )
                )

                # ------------------------------------------------
                # Generate encodings
                # ------------------------------------------------

                face_encodings = (
                    face_recognition.face_encodings(
                        rgb_frame,
                        face_locations
                    )
                )

                current_results = []

                # ------------------------------------------------
                # Recognize every face
                # ------------------------------------------------

                for (
                    face_location,
                    face_encoding
                ) in zip(
                    face_locations,
                    face_encodings
                ):

                    distances = (
                        face_recognition.face_distance(
                            known_encodings,
                            face_encoding
                        )
                    )

                    if len(distances) == 0:
                        continue

                    best_index = int(
                        np.argmin(distances)
                    )

                    best_distance = float(
                        distances[best_index]
                    )

                    # --------------------------------------------
                    # MATCH
                    # --------------------------------------------

                    if best_distance <= THRESHOLD:

                        student_id = known_ids[
                            best_index
                        ]

                        student_name = STUDENTS.get(
                            student_id,
                            "Unknown"
                        )

                        label = (
                            f"{student_name} "
                            f"| ID: {student_id}"
                        )

                        color = (
                            0,
                            255,
                            0
                        )

                        

                    # --------------------------------------------
                    # UNKNOWN
                    # --------------------------------------------

                    else:

                        student_id = None

                        label = "Unknown"

                        color = (
                            0,
                            0,
                            255
                        )

                        print(
                            f"Unknown face "
                            f"| Distance: "
                            f"{best_distance:.3f}"
                        )

                    current_results.append(
                        (
                            face_location,
                            label,
                            color,
                            best_distance
                        )
                    )

                last_results = current_results


                

            # ------------------------------------------------
            # Draw previous/current results
            # ------------------------------------------------

            for (
                face_location,
                label,
                color,
                distance
            ) in last_results:

                top, right, bottom, left = (
                    face_location
                )

                # Convert 1/5-size coordinates
                # back to original frame
                top *= 5
                right *= 5
                bottom *= 5
                left *= 5

                # ------------------------------------------------
                # Face box
                # ------------------------------------------------

                cv2.rectangle(
                    frame,
                    (left, top),
                    (right, bottom),
                    color,
                    2
                )

                # ------------------------------------------------
                # Label
                # ------------------------------------------------

                cv2.rectangle(
                    frame,
                    (
                        left,
                        max(0, bottom - 35)
                    ),
                    (
                        right,
                        bottom
                    ),
                    color,
                    cv2.FILLED
                )

                cv2.putText(
                    frame,
                    label,
                    (
                        left + 5,
                        bottom - 10
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2
                )

            # ------------------------------------------------
            # Title
            # ------------------------------------------------

            cv2.putText(
                frame,
                "SmartAttend - Team Shadow",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            # Show remaining camera time.
            remaining = max(0, int(CAMERA_TIMEOUT_SECONDS - elapsed))

            cv2.putText(
                frame,
                f"Camera OFF in: {remaining}s",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            # ------------------------------------------------
            # Display
            # ------------------------------------------------

            cv2.imshow(
                "SmartAttend - Face Recognition",
                frame
            )

            # ------------------------------------------------
            # Quit with Q
            # ------------------------------------------------

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        camera.release()
        cv2.destroyAllWindows()

        print("\nCamera closed.")
        print("Program ended.")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()