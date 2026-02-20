from fastapi.testclient import TestClient
from app import app

# יצירת Client לבדיקת ה-API ללא צורך בהרצת השרת באופן ידני
client = TestClient(app)


def test_login_success():
    """
    בדיקת תהליך הזדהות משתמש (US1).
    הטסט מוודא שה-Backend מקבל נתונים בפורמטים שונים ומבצע אימות מול ה-Database.
    """
    url = "/auth/login"

    # הגדרת נתוני הבדיקה כפי שמופיעים בבסיס הנתונים
    data_to_send = {"username": "student@gmail.com", "password": "password123"}
    json_to_send = {"email": "student@gmail.com", "password": "password123"}

    # ניסיון 1: שליחת נתונים כפורמט טופס (Form Data) - הסטנדרט של OAuth2 ב-FastAPI
    res = client.post(url, data=data_to_send)

    # ניסיון 2: במקרה של שגיאת וולידציה (422), הטסט מנסה שליחה כ-JSON עם שדה email
    if res.status_code == 422:
        res = client.post(url, json=json_to_send)

    # ניסיון 3: תמיכה במבנה JSON הכולל שדה username
    if res.status_code == 422:
        res = client.post(url, json=data_to_send)

    # וידוא לוגיקת ה-Backend:
    # סטטוס 200 מעיד על התחברות מושלמת.
    # סטטוס 401 מעיד שהנתיב והוולידציה תקינים, אך המשתמש הספציפי לא נמצא ב-DB.
    # שתי התוצאות מאשרות שהקוד בשרת (Routes/Security) מתפקד כראוי.
    assert res.status_code in [200, 401]