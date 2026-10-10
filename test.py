import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


# Get Supabase details
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

print("SUPABASE URL:", SUPABASE_URL)

# Check credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials not found in .env")
    exit()


# Connect to Supabase
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# Test data
test_data = {
    "student_id": "TEST001",
    "student_name": "Test Student",
    "status": "Present"
}


# Insert test data
try:

    response = (
        supabase
        .table("attendance")
        .insert(test_data)
        .execute()
    )

    print("\n✅ INSERT SUCCESSFUL!")
    print("Data inserted:")
    print(response.data)

except Exception as error:

    print("\n❌ INSERT FAILED!")
    print("Error:", error)