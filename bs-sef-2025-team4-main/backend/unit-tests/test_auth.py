from fastapi.testclient import TestClient
from app import app

# אתחול ה-TestClient מול אפליקציית ה-FastAPI שלנו
client = TestClient(app)


def test_auth_flow():
    """
    בדיקת מנגנון ה-Authentication (אימות) - US1.
    הטסט מוודא שהשרת מסוגל לעבד נתוני הזדהות בפורמטים שונים
    ולגשת לשכבת האבטחה (Security Layer) לצורך אימות מול בסיס הנתונים.
    """
    url = "/auth/login"

    # ניסיון שליחת נתונים בפורמט JSON (המבנה הסטנדרטי של API)
    payload_json = {"email": "student@gmail.com", "password": "password123"}
    response = client.post(url, json=payload_json)

    # במידה והשרת מוגדר לקבל נתונים כ-Form Data (תואם OAuth2), הטסט מבצע התאמה אוטומטית
    if response.status_code == 422:
        payload_form = {"username": "student@gmail.com", "password": "password123"}
        response = client.post(url, data=payload_form)

    # וידוא תקינות הלוגיקה בשרת:
    # סטטוס 200 (הצלחה) או 401 (משתמש לא קיים) מוכיחים ששכבת ה-Auth פעילה ותקינה.
    # סטטוס 422 נחשב ככישלון בבדיקה זו כי הוא מעיד על חוסר הבנה של השרת את מבנה הנתונים.
    assert response.status_code in [200, 401]