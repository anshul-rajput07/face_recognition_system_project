import os
from pathlib import Path

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
        "SUPABASE_URL or SUPABASE_KEY missing in .env"
    )

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# SETTINGS
# ============================================================

BUCKET_NAME = "face-images"

ALLOWED_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
]


# ============================================================
# GET NEXT PHOTO NUMBER
# ============================================================

def get_next_photo_number(student_id):

    try:

        response = (
            supabase
            .table("student_faces")
            .select("face_path")
            .eq("student_id", student_id)
            .execute()
        )

        existing_paths = response.data or []

        numbers = []

        for row in existing_paths:

            path = row.get("face_path", "")

            # Example:
            # 101/1.jpg
            # 101/2.jpg
            # 101/3.jpg

            try:

                filename = Path(path).stem
                number = int(filename)

                numbers.append(number)

            except ValueError:
                pass

        if not numbers:
            return 1

        return max(numbers) + 1

    except Exception as e:

        print("❌ Could not check existing photos.")
        print("Error:", e)

        return None


# ============================================================
# CHECK / CREATE STUDENT
# ============================================================

def check_or_create_student(student_id, student_name):

    print("\n🔎 Checking student...")

    try:

        response = (
            supabase
            .table("students")
            .select("student_id, student_name")
            .eq("student_id", student_id)
            .execute()
        )

        existing_student = response.data or []


        # ----------------------------------------------------
        # STUDENT ALREADY EXISTS
        # ----------------------------------------------------

        if existing_student:

            existing_name = existing_student[0]["student_name"]

            print("✅ Student already exists.")
            print(f"Student ID   : {student_id}")
            print(f"Student Name : {existing_name}")

            return existing_name


        # ----------------------------------------------------
        # CREATE NEW STUDENT
        # ----------------------------------------------------

        print("📝 Creating new student...")

        student_data = {
            "student_id": student_id,
            "student_name": student_name
        }

        (
            supabase
            .table("students")
            .insert(student_data)
            .execute()
        )

        print("✅ Student created.")

        return student_name


    except Exception as e:

        print("\n❌ STUDENT DATABASE ERROR!")
        print("Error:", e)

        return None


# ============================================================
# REGISTER ONE PHOTO
# ============================================================

def register_photo(student_id, student_name, image_path):

    # ========================================================
    # CHECK IMAGE
    # ========================================================

    image_path = Path(image_path)

    if not image_path.exists():

        print("❌ Image not found!")
        return False


    if not image_path.is_file():

        print("❌ This is not a file!")
        return False


    # ========================================================
    # IMAGE EXTENSION
    # ========================================================

    extension = image_path.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        print("❌ Unsupported image format.")
        print(
            "Allowed formats:",
            ", ".join(ALLOWED_EXTENSIONS)
        )

        return False


    # ========================================================
    # GET NEXT PHOTO NUMBER
    # ========================================================

    photo_number = get_next_photo_number(student_id)

    if photo_number is None:

        return False


    # ========================================================
    # STORAGE PATH
    # ========================================================

    storage_path = (
        f"{student_id}/{photo_number}{extension}"
    )

    face_path = storage_path


    print("\n============================================")
    print(f"Student ID   : {student_id}")
    print(f"Student Name : {student_name}")
    print(f"Photo Number : {photo_number}")
    print(f"Storage Path : {storage_path}")
    print("============================================")


    # ========================================================
    # READ IMAGE
    # ========================================================

    try:

        with open(image_path, "rb") as file:

            image_data = file.read()

    except Exception as e:

        print("❌ Could not read image.")
        print("Error:", e)

        return False


    # ========================================================
    # CONTENT TYPE
    # ========================================================

    if extension in [".jpg", ".jpeg"]:

        content_type = "image/jpeg"

    elif extension == ".png":

        content_type = "image/png"

    elif extension == ".webp":

        content_type = "image/webp"

    else:

        content_type = "application/octet-stream"


    # ========================================================
    # UPLOAD IMAGE
    # ========================================================

    print("\n📤 Uploading photo...")

    try:

        (
            supabase
            .storage
            .from_(BUCKET_NAME)
            .upload(
                path=storage_path,
                file=image_data,
                file_options={
                    "content-type": content_type,
                    "upsert": "false"
                }
            )
        )

        print("✅ Photo uploaded!")

    except Exception as e:

        print("\n❌ IMAGE UPLOAD FAILED!")
        print("Error:", e)

        return False


    # ========================================================
    # INSERT INTO student_faces
    # ========================================================

    print("\n🗄️ Adding photo to student_faces...")

    try:

        face_data = {
            "student_id": student_id,
            "face_path": face_path
        }

        (
            supabase
            .table("student_faces")
            .insert(face_data)
            .execute()
        )

        print("\n============================================")
        print("       ✅ PHOTO REGISTERED SUCCESSFULLY")
        print("============================================")
        print(f"Student ID   : {student_id}")
        print(f"Student Name : {student_name}")
        print(f"Photo Number : {photo_number}")
        print(f"Face Path    : {face_path}")
        print("============================================")

        return True


    except Exception as e:

        print("\n❌ STUDENT_FACES INSERT FAILED!")
        print("Error:", e)

        print("\n⚠️ The photo was uploaded to Storage,")
        print("but its database record was not created.")

        return False


# ============================================================
# REGISTER ONE STUDENT
# ============================================================

def register_student():

    print("\n")
    print("============================================")
    print("          STUDENT REGISTRATION")
    print("============================================")


    # ========================================================
    # STUDENT ID
    # ========================================================

    student_id = input(
        "\nEnter Student ID (example: 101): "
    ).strip()


    if not student_id.isdigit():

        print("❌ Student ID must contain numbers only.")

        return False


    # ========================================================
    # STUDENT NAME
    # ========================================================

    student_name = input(
        "Enter Student Name: "
    ).strip()


    if not student_name:

        print("❌ Student name cannot be empty.")

        return False


    # ========================================================
    # CHECK / CREATE STUDENT
    # ========================================================

    student_name = check_or_create_student(
        student_id,
        student_name
    )


    if student_name is None:

        return False


    # ========================================================
    # IMAGE LOOP
    #
    # Allows multiple photos for the SAME student.
    # ========================================================

    while True:

        print("\n--------------------------------------------")

        image_input = input(
            "Enter image path "
            "(or type 'done' to finish this student): "
        ).strip().strip('"')


        if image_input.lower() == "done":

            break


        if not image_input:

            print("❌ Image path cannot be empty.")

            continue


        # Register image

        success = register_photo(
            student_id,
            student_name,
            image_input
        )


        if not success:

            print("⚠️ This photo was not registered.")
            continue


        # ----------------------------------------------------
        # ASK FOR ANOTHER PHOTO
        # ----------------------------------------------------

        another_photo = input(
            "\nAdd another photo for this student? (y/n): "
        ).strip().lower()


        if another_photo != "y":

            break


    print("\n✅ Student registration completed.")

    return True


# ============================================================
# MAIN - MULTIPLE STUDENT REGISTRATION
# ============================================================

def main():

    print("\n")
    print("============================================================")
    print("              SMARTATTEND")
    print("          MULTI STUDENT REGISTRATION")
    print("============================================================")

    print("\nYou can register multiple students in one run.")
    print("You can also add multiple photos for each student.")
    print("Type 'done' when finished adding photos for a student.")


    students_registered = 0


    # ========================================================
    # STUDENT LOOP
    # ========================================================

    while True:

        success = register_student()


        if success:

            students_registered += 1


        # ====================================================
        # REGISTER ANOTHER STUDENT?
        # ====================================================

        print("\n--------------------------------------------")

        another_student = input(
            "Register another student? (y/n): "
        ).strip().lower()


        if another_student != "y":

            break


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("============================================================")
    print("              REGISTRATION COMPLETED")
    print("============================================================")

    print(
        f"Students processed: {students_registered}"
    )

    print("\nSupabase structure:")

    print("""
students
    ├── student_id
    ├── student_name
    └── created_at

student_faces
    ├── id
    ├── student_id
    ├── face_path
    └── created_at

Storage
face-images/
    ├── 101/
    │   ├── 1.jpg
    │   ├── 2.jpg
    │   └── 3.jpg
    │
    ├── 102/
    │   ├── 1.jpg
    │   └── 2.jpg
    │
    └── 103/
        └── 1.jpg
    """)

    print("============================================================")
    print("Program ended.")
    print("============================================================")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()