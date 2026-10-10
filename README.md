### Environment Setup

SmartAttend uses Supabase for student records and face-image storage. You must configure your own Supabase project before running the application.

**1. Clone the repository**

```bash
git clone YOUR_REPOSITORY_URL
cd SmartAttend
```

**2. Create your environment file**

Copy `.env.example` to a new file named `.env` in the project root.

On Windows Command Prompt:

```cmd
copy .env.example .env
```

**3. Configure your credentials**

Open `.env` and replace the placeholder values with your own Supabase project URL and publishable key.

```dotenv
SUPABASE_URL=your_supabase_project_url
SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
```

**4. Install dependencies**

```bash
pip install -r backend/requirements.txt
```

**5. Run the application**

Follow the project-specific instructions for running the registration and face-recognition scripts.

**Important:** Never commit your `.env` file or share your secret credentials publicly. You must also configure the required Supabase database tables and the `face-images` storage bucket before using the Supabase features.
