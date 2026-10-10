import cv2
import time
import face_recognition
import numpy as np

from zoneinfo import ZoneInfo
from datetime import datetime

import os
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# SUPABASE CONNECTION
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:

    raise ValueError(
        "Supabase URL or Publishable Key are not in .env file."
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


print("Supabase connected successfully!")


# ============================================================
# SETTINGS
# ============================================================

CAMERA_INDEX = 0

THRESHOLD = 0.50

MIN_MATCH_MARGIN = 0.03

PROCESS_EVERY_N_FRAMES = 5

CAMERA_TIMEOUT_SECONDS = 20

BUCKET_NAME = "face-images"


# ============================================================
# GET INDIA ATTENDANCE DATE
# ============================================================

def get_attendance_date():

    india_timezone = ZoneInfo(
        "Asia/Kolkata"
    )

    now_ist = datetime.now(
        india_timezone
    )

    return now_ist.date().isoformat()


# ============================================================
# INITIALIZE ATTENDANCE
#
# WHEN RECOGNITION STARTS:
# ALL STUDENTS ARE MARKED AS ABSENT
# ============================================================

def initialize_attendance(students):

    try:

        attendance_date = get_attendance_date()


        print()

        print("=" * 70)

        print(
            "INITIALIZING ATTENDANCE"
        )

        print(
            f"Date: {attendance_date}"
        )

        print("=" * 70)


        # ====================================================
        # CHECK IF ATTENDANCE ALREADY EXISTS FOR TODAY
        # ====================================================

        existing_response = (

            supabase
            .table("attendance")
            .select("*")
            .eq(
                "attendance_date",
                attendance_date
            )
            .execute()

        )


        existing_records = (

            existing_response.data or []

        )


        # ====================================================
        # IF RECORDS ALREADY EXIST
        #
        # ADD MISSING STUDENTS AS ABSENT
        # ====================================================

        existing_student_ids = set(

            str(
                record.get(
                    "student_id"
                )
            )

            for record in existing_records

        )


        missing_students = []


        for student_id, student_name in students.items():

            if str(student_id) not in existing_student_ids:

                missing_students.append(

                    {

                        "student_id": str(student_id),

                        "student_name": student_name,

                        "status": "Absent",

                        "attendance_date": attendance_date

                    }

                )


        # ====================================================
        # ADD MISSING STUDENTS
        # ====================================================

        if missing_students:

            (

                supabase
                .table("attendance")
                .insert(
                    missing_students
                )
                .execute()

            )


            print()

            print(
                f"Added {len(missing_students)} "
                "missing students as Absent."
            )


        # ====================================================
        # IF ALL RECORDS ALREADY EXIST
        # ====================================================

        else:

            print()

            print(
                "Attendance records already initialized."
            )

            print(
                f"Total existing records: "
                f"{len(existing_records)}"
            )


        print()

        print(
            "✓ ATTENDANCE INITIALIZED SUCCESSFULLY"
        )

        print(
            f"Total Students: {len(students)}"
        )

        print(
            "Initial Status: Absent"
        )

        print()

        return True


    except Exception as error:

        print()

        print(
            "FAILED TO INITIALIZE ATTENDANCE"
        )

        print(
            f"Error: {error}"
        )

        print()

        return False


# ============================================================
# MARK RECOGNIZED STUDENT AS PRESENT
# ============================================================

def mark_attendance(student_id, student_name):

    try:

        attendance_date = get_attendance_date()


        # ====================================================
        # CHECK STUDENT ATTENDANCE RECORD
        # ====================================================

        existing_response = (

            supabase
            .table("attendance")
            .select("*")
            .eq(
                "student_id",
                str(student_id)
            )
            .eq(
                "attendance_date",
                attendance_date
            )
            .execute()

        )


        existing_records = (

            existing_response.data or []

        )


        # ====================================================
        # RECORD EXISTS
        # ====================================================

        if existing_records:


            existing_record = (

                existing_records[0]

            )


            current_status = str(

                existing_record.get(
                    "status",
                    ""
                )

            ).lower()


            # =================================================
            # ALREADY PRESENT
            # =================================================

            if current_status == "present":

                print(

                    f"Already Present: "
                    f"{student_name} "
                    f"(ID: {student_id})"

                )

                return False


            # =================================================
            # UPDATE ABSENT → PRESENT
            # =================================================

            (

                supabase
                .table("attendance")
                .update(

                    {

                        "status": "Present"

                    }

                )
                .eq(

                    "student_id",

                    str(student_id)

                )
                .eq(

                    "attendance_date",

                    attendance_date

                )
                .execute()

            )


            print()

            print(
                "✓ ATTENDANCE UPDATED SUCCESSFULLY"
            )

            print(
                f"Student: {student_name}"
            )

            print(
                f"ID: {student_id}"
            )

            print(
                "Status: Absent → Present"
            )

            print(
                f"Date: {attendance_date}"
            )

            print()

            return True


        # ====================================================
        # RECORD DOES NOT EXIST
        # CREATE PRESENT RECORD
        # ====================================================

        else:


            attendance_record = {

                "student_id": str(student_id),

                "student_name": student_name,

                "status": "Present",

                "attendance_date": attendance_date

            }


            (

                supabase
                .table("attendance")
                .insert(
                    attendance_record
                )
                .execute()

            )


            print()

            print(
                "✓ ATTENDANCE SAVED SUCCESSFULLY"
            )

            print(
                f"Student: {student_name}"
            )

            print(
                f"ID: {student_id}"
            )

            print(
                "Status: Present"
            )

            print()

            return True


    except Exception as error:

        print()

        print(
            "FAILED TO UPDATE ATTENDANCE"
        )

        print(
            f"Student: {student_name}"
        )

        print(
            f"Error: {error}"
        )

        print()

        return False


# ============================================================
# LOAD STUDENTS + ALL FACE PHOTOS
# ============================================================

def load_registered_faces():

    students = {}

    student_encodings = {}


    print()

    print(
        "Loading students from Supabase..."
    )

    print()


    # ========================================================
    # LOAD STUDENTS TABLE
    # ========================================================

    try:

        response = (

            supabase
            .table("students")
            .select(
                "student_id, student_name"
            )
            .execute()

        )


        student_records = (

            response.data or []

        )


    except Exception as error:

        print(
            "Could not load students table."
        )

        print(
            "Error:",
            error
        )

        return students, student_encodings


    # ========================================================
    # NO STUDENTS
    # ========================================================

    if not student_records:

        print(
            "No students found in students table."
        )

        return students, student_encodings


    # ========================================================
    # STORE STUDENTS
    # ========================================================

    for student in student_records:


        student_id = str(

            student["student_id"]

        )


        student_name = (

            student["student_name"]

        )


        students[student_id] = student_name


        student_encodings[

            student_id

        ] = []


    print(

        f"Loaded {len(students)} students."

    )


    # ========================================================
    # LOAD STUDENT FACES TABLE
    # ========================================================

    try:

        response = (

            supabase
            .table("student_faces")
            .select(

                "id, student_id, face_path"

            )
            .execute()

        )


        face_records = (

            response.data or []

        )


    except Exception as error:

        print(
            "Could not load student_faces table."
        )

        print(
            "Error:",
            error
        )

        return students, student_encodings


    # ========================================================
    # NO FACE RECORDS
    # ========================================================

    if not face_records:

        print(
            "No face records found in student_faces table."
        )

        return students, student_encodings


    print(

        f"Found {len(face_records)} "
        f"registered face photos."

    )


    print()


    # ========================================================
    # DOWNLOAD AND ENCODE REGISTERED PHOTOS
    # ========================================================

    for face_record in face_records:


        student_id = str(

            face_record["student_id"]

        )


        face_path = (

            face_record["face_path"]

        )


        # ====================================================
        # CHECK STUDENT EXISTS
        # ====================================================

        if student_id not in students:

            print(

                f"Skipping {face_path}: "

                f"student ID {student_id} "

                "does not exist."

            )

            continue


        student_name = (

            students[student_id]

        )


        print(

            f"Loading: {student_name} "

            f"(ID {student_id})"

        )


        try:


            # =================================================
            # DOWNLOAD IMAGE FROM SUPABASE STORAGE
            # =================================================

            image_bytes = (

                supabase
                .storage
                .from_(BUCKET_NAME)
                .download(face_path)

            )


            if not image_bytes:

                print(

                    f"Empty image: {face_path}"

                )

                continue


            # =================================================
            # BYTES TO NUMPY ARRAY
            # =================================================

            image_array = (

                np.frombuffer(

                    image_bytes,

                    dtype=np.uint8

                )

            )


            # =================================================
            # DECODE IMAGE
            # =================================================

            image = (

                cv2.imdecode(

                    image_array,

                    cv2.IMREAD_COLOR

                )

            )


            if image is None:

                print(

                    f"Could not decode: "

                    f"{face_path}"

                )

                continue


            # =================================================
            # BGR TO RGB
            # =================================================

            image = (

                cv2.cvtColor(

                    image,

                    cv2.COLOR_BGR2RGB

                )

            )


            # =================================================
            # DETECT FACE
            # =================================================

            face_locations = (

                face_recognition.face_locations(

                    image,

                    model="hog"

                )

            )


            # =================================================
            # NO FACE
            # =================================================

            if len(face_locations) == 0:

                print(

                    f"No face found: "

                    f"{face_path}"

                )

                continue


            # =================================================
            # MULTIPLE FACES
            # =================================================

            if len(face_locations) > 1:

                print(

                    f"Multiple faces found: "

                    f"{face_path}"

                )

                continue


            # =================================================
            # CREATE FACE ENCODING
            # =================================================

            encodings = (

                face_recognition.face_encodings(

                    image,

                    face_locations

                )

            )


            if not encodings:

                print(

                    f"Encoding failed: "

                    f"{face_path}"

                )

                continue


            # =================================================
            # SAVE FACE ENCODING
            # =================================================

            student_encodings[

                student_id

            ].append(

                encodings[0]

            )


            print(

                "✓ Face encoding loaded."

            )


        except Exception as error:

            print(

                f"Error loading "

                f"{face_path}: {error}"

            )


    # ========================================================
    # KEEP ONLY STUDENTS WITH FACE ENCODINGS
    # ========================================================

    student_encodings = {

        student_id: encodings

        for student_id, encodings

        in student_encodings.items()

        if encodings

    }


    # ========================================================
    # SUMMARY
    # ========================================================

    total_encodings = sum(

        len(encodings)

        for encodings

        in student_encodings.values()

    )


    print()

    print("=" * 70)

    print(
        "REFERENCE DATA LOADED"
    )

    print("=" * 70)


    print(

        f"Students in database: "

        f"{len(students)}"

    )


    print(

        f"Students with face data: "

        f"{len(student_encodings)}"

    )


    print(

        f"Total face encodings: "

        f"{total_encodings}"

    )


    print("=" * 70)

    print()


    return (

        students,

        student_encodings

    )


# ============================================================
# RECOGNIZE ONE LIVE FACE
# ============================================================

def recognize_student(

    face_encoding,

    student_encodings

):


    best_student_id = None

    best_distance = float("inf")

    second_best_distance = float("inf")


    # ========================================================
    # COMPARE WITH EACH STUDENT
    # ========================================================

    for (

        student_id,

        reference_encodings

    ) in student_encodings.items():


        if not reference_encodings:

            continue


        distances = (

            face_recognition.face_distance(

                reference_encodings,

                face_encoding

            )

        )


        student_distance = float(

            np.min(distances)

        )


        # ====================================================
        # BEST MATCH
        # ====================================================

        if student_distance < best_distance:


            second_best_distance = (

                best_distance

            )


            best_distance = (

                student_distance

            )


            best_student_id = (

                student_id

            )


        elif student_distance < second_best_distance:


            second_best_distance = (

                student_distance

            )


    # ========================================================
    # NO MATCH
    # ========================================================

    if best_student_id is None:

        return None, None


    # ========================================================
    # THRESHOLD CHECK
    # ========================================================

    if best_distance > THRESHOLD:

        return (

            None,

            best_distance

        )


    # ========================================================
    # MATCH MARGIN CHECK
    # ========================================================

    if (

        MIN_MATCH_MARGIN > 0

        and second_best_distance != float("inf")

        and (

            second_best_distance

            - best_distance

        ) < MIN_MATCH_MARGIN

    ):

        return (

            None,

            best_distance

        )


    return (

        best_student_id,

        best_distance

    )


# ============================================================
# MAIN
# ============================================================

def main():


    print()

    print("=" * 70)

    print(
        "SMARTATTEND - TEAM SHADOW"
    )

    print(
        "FACE RECOGNITION SYSTEM"
    )

    print("=" * 70)


    # ========================================================
    # LOAD STUDENTS AND FACE DATA
    # ========================================================

    (

        STUDENTS,

        STUDENT_ENCODINGS

    ) = load_registered_faces()


    # ========================================================
    # CHECK STUDENTS
    # ========================================================

    if not STUDENTS:

        print(

            "No students found."

        )

        return


    # ========================================================
    # INITIALIZE ATTENDANCE
    #
    # ALL STUDENTS START AS ABSENT
    # ========================================================

    attendance_initialized = (

        initialize_attendance(

            STUDENTS

        )

    )


    if not attendance_initialized:

        print(

            "Could not initialize attendance."

        )

        return


    # ========================================================
    # CHECK FACE DATA
    # ========================================================

    if not STUDENT_ENCODINGS:


        print(

            "\nNo usable registered "
            "face encodings found."

        )


        return


    # ========================================================
    # SHOW AVAILABLE STUDENTS
    # ========================================================

    print()

    print(
        "Students available for recognition:"
    )

    print()


    for student_id in STUDENT_ENCODINGS:


        photo_count = len(

            STUDENT_ENCODINGS.get(

                student_id,

                []

            )

        )


        print(

            f"{student_id} -> "

            f"{STUDENTS[student_id]} "

            f"({photo_count} photos)"

        )


    # ========================================================
    # OPEN CAMERA
    # ========================================================

    print()

    print(

        f"Opening laptop camera "

        f"(index {CAMERA_INDEX})..."

    )


    camera = cv2.VideoCapture(

        CAMERA_INDEX

    )


    if not camera.isOpened():

        print(

            "\nCould not open laptop camera."

        )

        return


    # ========================================================
    # CAMERA RESOLUTION
    # ========================================================

    camera.set(

        cv2.CAP_PROP_FRAME_WIDTH,

        1280

    )


    camera.set(

        cv2.CAP_PROP_FRAME_HEIGHT,

        720

    )


    print()

    print(
        "Camera started."
    )


    print(

        f"Camera will automatically turn off "

        f"after {CAMERA_TIMEOUT_SECONDS} seconds."

    )


    print(
        "Press Q to quit."
    )


    # ========================================================
    # CAMERA STATE
    # ========================================================

    start_time = (

        time.monotonic()

    )


    frame_count = 0

    last_results = []


    # ========================================================
    # STUDENTS RECOGNIZED DURING SESSION
    # ========================================================

    present_students = set()


    # ========================================================
    # CAMERA LOOP
    # ========================================================

    try:


        while True:


            # =================================================
            # TIMER
            # =================================================

            elapsed = (

                time.monotonic()

                - start_time

            )


            if elapsed >= CAMERA_TIMEOUT_SECONDS:


                print()

                print(

                    f"{CAMERA_TIMEOUT_SECONDS} "

                    "seconds completed."

                )


                print(

                    "Automatically turning camera off..."

                )

                break


            # =================================================
            # READ CAMERA FRAME
            # =================================================

            success, frame = camera.read()


            if not success:

                print(

                    "Could not read camera frame."

                )

                break


            frame_count += 1


            # =================================================
            # PROCESS EVERY N FRAMES
            # =================================================

            if (

                frame_count

                % PROCESS_EVERY_N_FRAMES

                == 0

            ):


                # =============================================
                # RESIZE FRAME
                # =============================================

                small_frame = cv2.resize(

                    frame,

                    None,

                    fx=0.20,

                    fy=0.20

                )


                # =============================================
                # BGR TO RGB
                # =============================================

                rgb_frame = cv2.cvtColor(

                    small_frame,

                    cv2.COLOR_BGR2RGB

                )


                # =============================================
                # DETECT FACES
                # =============================================

                face_locations = (

                    face_recognition.face_locations(

                        rgb_frame,

                        model="hog"

                    )

                )


                # =============================================
                # CREATE FACE ENCODINGS
                # =============================================

                face_encodings = (

                    face_recognition.face_encodings(

                        rgb_frame,

                        face_locations

                    )

                )


                current_results = []


                # =============================================
                # RECOGNIZE EACH FACE
                # =============================================

                for (

                    face_location,

                    face_encoding

                ) in zip(

                    face_locations,

                    face_encodings

                ):


                    (

                        student_id,

                        best_distance

                    ) = recognize_student(

                        face_encoding,

                        STUDENT_ENCODINGS

                    )


                    # =========================================
                    # STUDENT RECOGNIZED
                    # =========================================

                    if student_id is not None:


                        student_name = (

                            STUDENTS.get(

                                student_id,

                                "Unknown"

                            )

                        )


                        label = (

                            f"{student_name} | "

                            f"ID: {student_id}"

                        )


                        color = (

                            0,

                            255,

                            0

                        )


                        # =====================================
                        # FIRST RECOGNITION
                        # =====================================

                        if student_id not in present_students:


                            present_students.add(

                                student_id

                            )


                            print()

                            print(

                                f"Student recognized: "

                                f"{student_name} "

                                f"(ID: {student_id})"

                            )


                            # =================================
                            # CHANGE ABSENT → PRESENT
                            # =================================

                            mark_attendance(

                                student_id,

                                student_name

                            )


                    # =========================================
                    # UNKNOWN FACE
                    # =========================================

                    else:


                        color = (

                            0,

                            0,

                            255

                        )


                        if best_distance is None:

                            distance_text = "-"

                        else:

                            distance_text = (

                                f"{best_distance:.2f}"

                            )


                        label = (

                            f"Unknown | "

                            f"{distance_text}"

                        )


                    # =========================================
                    # STORE RESULT
                    # =========================================

                    current_results.append(

                        (

                            face_location,

                            label,

                            color,

                            best_distance

                        )

                    )


                last_results = current_results


            # =================================================
            # DRAW FACE RESULTS
            # =================================================

            for (

                face_location,

                label,

                color,

                distance

            ) in last_results:


                (

                    top,

                    right,

                    bottom,

                    left

                ) = face_location


                # Coordinates back to original size

                top *= 5

                right *= 5

                bottom *= 5

                left *= 5


                # =============================================
                # DRAW FACE RECTANGLE
                # =============================================

                cv2.rectangle(

                    frame,

                    (left, top),

                    (right, bottom),

                    color,

                    2

                )


                # =============================================
                # LABEL BACKGROUND
                # =============================================

                label_top = max(

                    0,

                    bottom - 35

                )


                cv2.rectangle(

                    frame,

                    (left, label_top),

                    (right, bottom),

                    color,

                    cv2.FILLED

                )


                # =============================================
                # LABEL TEXT
                # =============================================

                cv2.putText(

                    frame,

                    label,

                    (

                        left + 5,

                        bottom - 10

                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.55,

                    (

                        255,

                        255,

                        255

                    ),

                    2

                )


            # =================================================
            # TITLE
            # =================================================

            cv2.putText(

                frame,

                "SmartAttend - Team Shadow",

                (20, 35),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (

                    0,

                    255,

                    255

                ),

                2

            )


            # =================================================
            # REMAINING TIME
            # =================================================

            remaining = max(

                0,

                int(

                    CAMERA_TIMEOUT_SECONDS

                    - elapsed

                )

            )


            cv2.putText(

                frame,

                f"Camera OFF in: {remaining}s",

                (20, 70),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.65,

                (

                    0,

                    255,

                    255

                ),

                2

            )


            # =================================================
            # PRESENT COUNT
            # =================================================

            present_count = len(

                present_students

            )


            total_students = len(

                STUDENTS

            )


            cv2.putText(

                frame,

                f"Present: "

                f"{present_count}/{total_students}",

                (20, 105),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.65,

                (

                    0,

                    255,

                    255

                ),

                2

            )


            # =================================================
            # SHOW CAMERA
            # =================================================

            cv2.imshow(

                "SmartAttend - Face Recognition",

                frame

            )


            # =================================================
            # PRESS Q TO QUIT
            # =================================================

            if (

                cv2.waitKey(1)

                & 0xFF

                == ord("q")

            ):


                print()

                print(

                    "Camera closed manually."

                )

                break


    finally:


        # ====================================================
        # CLOSE CAMERA
        # ====================================================

        camera.release()

        cv2.destroyAllWindows()


        # ====================================================
        # FINAL SESSION SUMMARY
        # ====================================================

        absent_count = (

            len(STUDENTS)

            - len(present_students)

        )


        print()

        print("=" * 70)

        print(

            "RECOGNITION SESSION COMPLETED"

        )

        print("=" * 70)


        print(

            f"Total Students: "

            f"{len(STUDENTS)}"

        )


        print(

            f"Present Students: "

            f"{len(present_students)}"

        )


        print(

            f"Absent Students: "

            f"{absent_count}"

        )


        print()

        print(

            "Attendance is saved in Supabase."

        )


        print("=" * 70)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()