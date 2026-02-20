from fastapi.testclient import TestClient
from app import app

# אתחול ה-TestClient כדי לבצע קריאות API לנתיבי הקורסים
client = TestClient(app)


def test_get_courses_list():
    """
    בדיקת שליפת רשימת קורסים (Data Fetching).
    הטסט מוודא שה-Endpoint של הקורסים פעיל, מוגן במידת הצורך,
    ומחזיר נתונים במבנה תקין של רשימה (List).
    """
    # ניסיון גישה לנתיב הקורסים (בדיקת גמישות לנתיב עם או בלי לוכסן)
    url = "/courses"
    response = client.get(url)

    if response.status_code == 404:
        url = "/courses/"
        response = client.get(url)

    # וידוא תקינות התגובה מהשרת:
    # 200 = הצלחה בשליפת נתונים.
    # 401 = הנתיב קיים אך דורש הזדהות (Token), מה שמעיד על אבטחה תקינה.
    assert response.status_code in [200, 401]

    # במידה והגישה אושרה (200), נוודא שהנתונים חוזרים בפורמט JSON כרשימה
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list), "השרת חייב להחזיר רשימת קורסים"