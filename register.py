import cv2
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client


# =========================================================
# SUPABASE CONNECTION
# =========================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase URL or Publishable Key .env file me nahi mila."
    )

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("✅ Supabase connected successfully!")


# =========================================================
# HAAR CASCADE
# =========================================================

FACE_CASCADE = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)


# =========================================================
# SUPABASE STORAGE
# =========================================================

BUCKET_NAME = "face-images"


# =========================================================
# GET NEXT PHOTO NUMBER
# =========================================================

def get_next_photo_number(student_id):

    try:

        response = (
            supabase
            .table("student_faces")
            .select("face_path")
            .eq("student_id", student_id)
            .execute()
        )

        rows = response.data or []

        numbers = []

        for row in rows:

            face_path = row.get("face_path", "")

            # Example:
            # 101/1.jpg
            # 101/2.jpg
            # 101/3.jpg

            try:

                filename = Path(face_path).stem

                number = int(filename)

                numbers.append(number)

            except ValueError:

                continue

        if not numbers:
            return 1

        return max(numbers) + 1

    except Exception as error:

        print("❌ Could not find existing face photos.")
        print("Error:", error)

        return None


# =========================================================
# CREATE / UPDATE STUDENT
# =========================================================

def save_student(student_id, student_name):

    try:

        # Check whether student already exists
        response = (
            supabase
            .table("students")
            .select("student_id, student_name")
            .eq("student_id", student_id)
            .execute()
        )

        # ----------------------------------------------------
        # STUDENT ALREADY EXISTS
        # ----------------------------------------------------

        if response.data:

            existing_name = response.data[0]["student_name"]

            print(
                f"✅ Student {student_id} already exists."
            )

            print(
                f"Student Name: {existing_name}"
            )

            return True

        # ----------------------------------------------------
        # NEW STUDENT
        # ----------------------------------------------------

        student_data = {
            "student_id": student_id,
            "student_name": student_name
        }

        supabase \
            .table("students") \
            .insert(student_data) \
            .execute()

        print("✅ Student added to students table!")

        return True

    except Exception as error:

        print("❌ Student database save failed.")
        print("Error:", error)

        return False


# =========================================================
# SAVE FACE RECORD
# =========================================================

def save_face_record(student_id, face_path):

    try:

        face_data = {
            "student_id": student_id,
            "face_path": face_path
        }

        supabase \
            .table("student_faces") \
            .insert(face_data) \
            .execute()

        print("✅ Face record added to student_faces!")

        return True

    except Exception as error:

        print("❌ student_faces insert failed.")
        print("Error:", error)

        return False


# =========================================================
# REGISTER STUDENT
# =========================================================

def register_student() -> None:

    # -----------------------------------------------------
    # STUDENT INFORMATION
    # -----------------------------------------------------

    student_id = input(
        "\nEnter Student ID: "
    ).strip()

    name = input(
        "Enter Student Name: "
    ).strip()

    if not student_id or not name:

        print(
            "❌ Student ID and name are required."
        )

        return

    # -----------------------------------------------------
    # CHECK STUDENT ID
    # -----------------------------------------------------

    if not student_id.isdigit():

        print(
            "❌ Student ID must contain numbers only."
        )

        return

    # -----------------------------------------------------
    # SAVE STUDENT
    # -----------------------------------------------------

    print("\n🗄️ Checking students table...")

    if not save_student(student_id, name):

        return

    # -----------------------------------------------------
    # GET NEXT PHOTO NUMBER
    # -----------------------------------------------------

    next_photo_number = get_next_photo_number(student_id)

    if next_photo_number is None:

        return

    print(
        f"\n📸 Next photo number: {next_photo_number}"
    )

    # -----------------------------------------------------
    # LOAD FACE DETECTOR
    # -----------------------------------------------------

    detector = cv2.CascadeClassifier(
        FACE_CASCADE
    )

    if detector.empty():

        print(
            "❌ Could not load face detector."
        )

        return

    # -----------------------------------------------------
    # OPEN CAMERA
    # -----------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print(
            "❌ Could not open camera."
        )

        return

    # -----------------------------------------------------
    # CAMERA SETTINGS
    # -----------------------------------------------------

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("\n========================================")
    print("       STUDENT FACE REGISTRATION")
    print("========================================")
    print(f"Student ID   : {student_id}")
    print(f"Student Name : {name}")
    print("----------------------------------------")
    print("SPACE = Capture photo")
    print("Q     = Finish registration")
    print("----------------------------------------")
    print("You can capture MULTIPLE photos.")
    print("========================================\n")

    captured_count = 0

    try:

        while True:

            # -------------------------------------------------
            # READ CAMERA
            # -------------------------------------------------

            success, frame = camera.read()

            if not success:

                print(
                    "❌ Could not read camera frame."
                )

                break

            # -------------------------------------------------
            # GRAYSCALE
            # -------------------------------------------------

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # -------------------------------------------------
            # FACE DETECTION
            # -------------------------------------------------

            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )

            # -------------------------------------------------
            # DRAW FACE RECTANGLES
            # -------------------------------------------------

            for x, y, w, h in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            # -------------------------------------------------
            # CAMERA TEXT
            # -------------------------------------------------

            cv2.putText(
                frame,
                f"ID: {student_id} | {name}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Photos captured: {captured_count}",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "SPACE = Capture | Q = Finish",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # -------------------------------------------------
            # SHOW CAMERA
            # -------------------------------------------------

            cv2.imshow(
                "Student Registration",
                frame
            )

            # -------------------------------------------------
            # KEYBOARD
            # -------------------------------------------------

            key = cv2.waitKey(10) & 0xFF

            # =================================================
            # SPACE → CAPTURE
            # =================================================

            if key == 32:

                print("\n📸 SPACE pressed!")

                # -------------------------------------------------
                # NO FACE
                # -------------------------------------------------

                if len(faces) == 0:

                    print(
                        "❌ No face detected."
                    )

                    print(
                        "Please look at the camera and try again."
                    )

                    continue

                # -------------------------------------------------
                # MULTIPLE FACES
                # -------------------------------------------------

                if len(faces) > 1:

                    print(
                        "❌ More than one face detected."
                    )

                    print(
                        "Keep only one person "
                        "in front of the camera."
                    )

                    continue

                # -------------------------------------------------
                # GET FACE
                # -------------------------------------------------

                x, y, w, h = faces[0]

                # -------------------------------------------------
                # CROP FACE
                # -------------------------------------------------

                face_image = frame[
                    y:y + h,
                    x:x + w
                ]

                # =================================================
                # CONVERT IMAGE TO JPEG IN MEMORY
                # =================================================

                success, encoded_image = cv2.imencode(
                    ".jpg",
                    face_image
                )

                if not success:

                    print(
                        "❌ Could not encode face image."
                    )

                    continue

                image_bytes = encoded_image.tobytes()

                # =================================================
                # CREATE PHOTO PATH
                # =================================================

                photo_number = next_photo_number + captured_count

                filename = f"{photo_number}.jpg"

                storage_path = (
                    f"{student_id}/{filename}"
                )

                print(
                    f"\n📤 Uploading: {storage_path}"
                )

                # =================================================
                # UPLOAD TO SUPABASE STORAGE
                # =================================================

                try:

                    supabase.storage \
                        .from_(BUCKET_NAME) \
                        .upload(
                            storage_path,
                            image_bytes,
                            {
                                "content-type": "image/jpeg",
                                "upsert": "false"
                            }
                        )

                    print(
                        "✅ Face image uploaded!"
                    )

                except Exception as error:

                    print(
                        "❌ Photo upload failed."
                    )

                    print(
                        "Error:",
                        error
                    )

                    continue

                # =================================================
                # SAVE PATH IN student_faces
                # =================================================

                if save_face_record(
                    student_id,
                    storage_path
                ):

                    captured_count += 1

                    print("\n================================")
                    print("✅ PHOTO REGISTERED")
                    print("================================")
                    print(
                        f"Student ID : {student_id}"
                    )
                    print(
                        f"Photo      : {filename}"
                    )
                    print(
                        f"Path       : {storage_path}"
                    )
                    print("================================")

                else:

                    print(
                        "⚠️ Photo uploaded but database "
                        "record failed."
                    )

            # =================================================
            # Q → FINISH
            # =================================================

            elif key == ord("q"):

                print(
                    "\n🛑 Registration finished."
                )

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

    # =========================================================
    # FINAL RESULT
    # =========================================================

    print("\n========================================")
    print("       🎉 REGISTRATION COMPLETE!")
    print("========================================")
    print(
        f"Student ID   : {student_id}"
    )
    print(
        f"Student Name : {name}"
    )
    print(
        f"Photos Added : {captured_count}"
    )
    print("========================================")

    if captured_count > 0:

        print(
            "\n✅ Student information → students"
        )

        print(
            "✅ All face photos → student_faces"
        )

        print(
            "✅ Actual images → face-images bucket"
        )

    else:

        print(
            "\n⚠️ No photos were captured."
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    register_student()