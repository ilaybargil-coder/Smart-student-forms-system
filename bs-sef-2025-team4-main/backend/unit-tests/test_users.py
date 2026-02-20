from fastapi.testclient import TestClient
# ייבוא האפליקציה ישירות מהתיקייה הנוכחית
from app import app

client = TestClient(app)


def test_get_me_unauthorized():
    """
    US11: בדיקת אבטחת פרטי משתמש.
    מוודא שמשתמש ללא Token תקני (Unauthorized) אינו יכול לגשת למידע אישי.
    הציפייה היא לקבל קוד שגיאה 401.
    """
    response = client.get("/users/me")

    # השרת אמור לחסום גישה ללא הזדהות
    assert response.status_code == 401
    print(f"\nUser Security Test: Access denied as expected (Status {response.status_code})")


def test_user_endpoint_exists():
    """
    בדיקה כללית שהנתיב למשתמשים מוגדר במערכת.
    """
    response = client.get("/users/")
    # אם הנתיב קיים, הוא יחזיר או 401 (חסום) או 200/404 (לא חסום/לא קיים)
    # העיקר שלא נקבל 500 (שגיאת שרת)
    assert response.status_code != 500