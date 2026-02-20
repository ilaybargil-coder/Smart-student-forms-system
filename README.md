# Smart-student-forms-system

# יצירת סביבה וירטואלית
python -m venv .venv

# הפעלת הסביבה (Windows)
.venv\Scripts\activate
# הפעלת הסביבה (Mac/Linux)
source .venv/bin/activate

# התקנת הספריות הנדרשות
pip install -r requirements.txt


את זה לשים בקובץ .env: 
# הגדרות חיבור ל-Supabase PostgreSQL
DATABASE_URL=postgresql+psycopg2://postgres:bopjyr-7fiwte-Tijvaq@db.battqvwiqdcpdehnvgdi.supabase.co:5432/postgres?sslmode=require

# מפתחות API של Supabase (עבור Storage וניהול משתמשים)
SUPABASE_URL=https://battqvwiqdcpdehnvgdi.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJhdHRxdndpcWRjcGRlaG52Z2RpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzAwNTI2MiwiZXhwIjoyMDgyNTgxMjYyfQ.9eevr1mwtrdv-o6Gd_QI_x-piaLj7Nve-fM7XHF8DzI

הרצת השרת:
cd backend
python -m uvicorn app:app --reload
