from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client
from dotenv import load_dotenv
import os


# ==========================================
# CREATE FASTAPI APP
# ==========================================

app = FastAPI(
    title="Teacher Attendance System API"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://127.0.0.1:5500",

        "http://localhost:5500"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# ==========================================
# LOAD .ENV FILE
# ==========================================

BASE_DIR = os.path.dirname(

    os.path.abspath(__file__)

)


load_dotenv(

    os.path.join(

        BASE_DIR,

        ".env"

    )

)


# ==========================================
# GET SUPABASE CREDENTIALS
# ==========================================

print()

print(

    "Looking for .env at:",

    os.path.join(

        BASE_DIR,

        ".env"

    )

)


SUPABASE_URL = os.getenv(

    "SUPABASE_URL"

)


SUPABASE_KEY = os.getenv(

    "SUPABASE_KEY"

)


print(

    "SUPABASE_URL loaded:",

    bool(SUPABASE_URL)

)


print(

    "SUPABASE_KEY loaded:",

    bool(SUPABASE_KEY)

)


# ==========================================
# CHECK CREDENTIALS
# ==========================================

if not SUPABASE_URL or not SUPABASE_KEY:

    raise ValueError(

        "SUPABASE_URL or SUPABASE_KEY is missing from .env file!"

    )


# ==========================================
# CONNECT TO SUPABASE
# ==========================================

supabase: Client = create_client(

    SUPABASE_URL,

    SUPABASE_KEY

)


print()

print(

    "Supabase connected successfully!"

)

print()


# ==========================================
# HOME ROUTE
# ==========================================

@app.get("/")
def home():

    return {

        "message":

            "Teacher Attendance System API is running!"

    }


# ==========================================
# GET ALL STUDENTS
# ==========================================

@app.get("/students")
def get_students():

    try:

        response = (

            supabase

            .table("students")

            .select("*")

            .execute()

        )


        return {

            "success": True,

            "data": response.data or []

        }


    except Exception as error:

        print(

            "STUDENTS ERROR:",

            str(error)

        )


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ==========================================
# GET ALL ATTENDANCE
# ==========================================

@app.get("/attendance")
def get_attendance():

    try:

        response = (

            supabase

            .table("attendance")

            .select("*")

            .execute()

        )


        return {

            "success": True,

            "data": response.data or []

        }


    except Exception as error:

        print(

            "ATTENDANCE ERROR:",

            str(error)

        )


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ==========================================
# GET ATTENDANCE BY DATE
# ==========================================
#
# Example:
#
# GET /attendance/date/2026-09-07
#
# Used for Modify Attendance
#
# ==========================================

@app.get("/attendance/date/{attendance_date}")
def get_attendance_by_date(

    attendance_date: str

):

    try:

        print()

        print("=" * 60)

        print(

            "GETTING ATTENDANCE BY DATE"

        )

        print(

            "Date:",

            attendance_date

        )

        print("=" * 60)


        response = (

            supabase

            .table("attendance")

            .select("*")

            .eq(

                "attendance_date",

                attendance_date

            )

            .execute()

        )


        attendance_records = (

            response.data

            or

            []

        )


        return {

            "success": True,

            "date": attendance_date,

            "data": attendance_records

        }


    except Exception as error:

        print(

            "GET ATTENDANCE BY DATE ERROR:",

            str(error)

        )


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ==========================================
# ATTENDANCE DATA MODEL
# ==========================================

class AttendanceItem(BaseModel):

    student_id: str

    student_name: str

    status: str

    attendance_date: str


# ==========================================
# SAVE NEW ATTENDANCE
# ==========================================

@app.post("/attendance")
def save_attendance(

    attendance: List[AttendanceItem]

):

    try:

        attendance_data = []


        # ======================================
        # PREPARE DATA
        # ======================================

        for item in attendance:


            # ==================================
            # VALIDATE STATUS
            # ==================================

            if item.status not in [

                "Present",

                "Absent"

            ]:

                raise HTTPException(

                    status_code=400,

                    detail=

                        f"Invalid status for {item.student_name}"

                )


            attendance_data.append(

                {

                    "student_id":

                        str(item.student_id),


                    "student_name":

                        item.student_name,


                    "status":

                        item.status,


                    "attendance_date":

                        item.attendance_date

                }

            )


        # ======================================
        # INSERT DATA
        # ======================================

        response = (

            supabase

            .table("attendance")

            .insert(

                attendance_data

            )

            .execute()

        )


        return {

            "success": True,

            "message":

                "Attendance saved successfully!",


            "data":

                response.data

                or

                []

        }


    except HTTPException:

        raise


    except Exception as error:

        print(

            "SAVE ATTENDANCE ERROR:",

            str(error)

        )


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ==========================================
# UPDATE ATTENDANCE MODEL
# ==========================================

class AttendanceUpdate(BaseModel):

    status: str

    attendance_date: str


# ==========================================
# UPDATE ATTENDANCE
# ==========================================
#
# Example:
#
# PUT /attendance/103
#
# {
#
#     "status": "Absent",
#
#     "attendance_date": "2026-09-07"
#
# }
#
# ==========================================

@app.put("/attendance/{student_id}")
def update_attendance(

    student_id: str,

    attendance_update: AttendanceUpdate

):

    try:

        print()

        print("=" * 60)

        print(

            "UPDATING ATTENDANCE"

        )

        print("=" * 60)

        print(

            "Student ID:",

            student_id

        )

        print(

            "New Status:",

            attendance_update.status

        )

        print(

            "Attendance Date:",

            attendance_update.attendance_date

        )

        print("=" * 60)


        # ==================================
        # VALIDATE STATUS
        # ==================================

        valid_statuses = [

            "Present",

            "Absent"

        ]


        if (

            attendance_update.status

            not in

            valid_statuses

        ):

            raise HTTPException(

                status_code=400,

                detail=

                    "Status must be Present or Absent"

            )


        # ==================================
        # CHECK RECORD EXISTS
        # ==================================

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

                attendance_update.attendance_date

            )

            .execute()

        )


        existing_records = (

            existing_response.data

            or

            []

        )


        # ==================================
        # RECORD DOES NOT EXIST
        # ==================================

        if not existing_records:

            raise HTTPException(

                status_code=404,

                detail=(

                    f"No attendance record found for "

                    f"student {student_id} "

                    f"on {attendance_update.attendance_date}"

                )

            )


        # ==================================
        # UPDATE STATUS
        # ==================================

        update_response = (

            supabase

            .table("attendance")

            .update(

                {

                    "status":

                        attendance_update.status

                }

            )

            .eq(

                "student_id",

                str(student_id)

            )

            .eq(

                "attendance_date",

                attendance_update.attendance_date

            )

            .execute()

        )


        print()

        print(

            "✓ ATTENDANCE UPDATED SUCCESSFULLY"

        )

        print(

            f"Student ID: {student_id}"

        )

        print(

            f"Status: {attendance_update.status}"

        )

        print(

            f"Date: {attendance_update.attendance_date}"

        )

        print()


        return {

            "success": True,

            "message":

                "Attendance updated successfully!",


            "data":

                update_response.data

                or

                []

        }


    except HTTPException:

        raise


    except Exception as error:

        print()

        print(

            "UPDATE ATTENDANCE ERROR:"

        )

        print(

            str(error)

        )

        print()


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ==========================================
# RESET / DELETE ATTENDANCE BY DATE
# ==========================================
#
# Example:
#
# DELETE /attendance/reset/2026-09-07
#
# ==========================================

@app.delete("/attendance/reset/{attendance_date}")
def reset_attendance(

    attendance_date: str

):

    try:

        print()

        print("=" * 60)

        print(

            "RESETTING ATTENDANCE"

        )

        print(

            "Date:",

            attendance_date

        )

        print("=" * 60)


        # ==================================
        # CHECK RECORDS FIRST
        # ==================================

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

            existing_response.data

            or

            []

        )


        # ==================================
        # NO RECORDS
        # ==================================

        if not existing_records:

            return {

                "success": True,

                "message":

                    "No attendance records found for this date.",


                "deleted_count":

                    0

            }


        # ==================================
        # COUNT RECORDS
        # ==================================

        deleted_count = (

            len(existing_records)

        )


        # ==================================
        # DELETE RECORDS
        # ==================================

        delete_response = (

            supabase

            .table("attendance")

            .delete()

            .eq(

                "attendance_date",

                attendance_date

            )

            .execute()

        )


        print()

        print(

            "✓ ATTENDANCE RESET SUCCESSFULLY"

        )

        print(

            "Deleted Records:",

            deleted_count

        )

        print()


        return {

            "success": True,

            "message":

                "Attendance reset successfully!",


            "deleted_count":

                deleted_count,


            "data":

                delete_response.data

                or

                []

        }


    except Exception as error:

        print()

        print(

            "RESET ATTENDANCE ERROR:"

        )

        print(

            str(error)

        )

        print()


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ==========================================
# GET STUDENT FACES
# ==========================================

@app.get("/student-faces")
def get_student_faces():

    try:

        response = (

            supabase

            .table("student_faces")

            .select("*")

            .execute()

        )


        faces = (

            response.data

            or

            []

        )


        # ==================================
        # CONVERT FACE PATH TO PUBLIC URL
        # ==================================

        for face in faces:


            if face.get(

                "face_path"

            ):


                public_url = (

                    supabase

                    .storage

                    .from_(

                        "face-images"

                    )

                    .get_public_url(

                        face["face_path"]

                    )

                )


                face[

                    "image_url"

                ] = (

                    public_url

                )


        return {

            "success": True,

            "data":

                faces

        }


    except Exception as error:

        print(

            "STUDENT FACES ERROR:",

            str(error)

        )


        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ==========================================
# RUN FASTAPI SERVER
# ==========================================

if __name__ == "__main__":

    import uvicorn


    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8000,

        reload=True

    )