import pytest
# שינוי הייבוא: מייבאים ישירות מהקובץ שנמצא בתיקייה המקבילה
from security import hash_password, verify_password


def test_password_hashing_logic():
    """
    בדיקת הצפנת סיסמה (Hashing).
    מוודא שהמערכת לעולם לא שומרת סיסמאות כטקסט פשוט (Plaintext).
    """
    pwd = "StudentPassword123"
    hashed = hash_password(pwd)

    # וידוא שהסיסמה אכן עברה שינוי (הצפנה)
    assert hashed != pwd
    # וידוא שפונקציית האימות מצליחה לזהות את הסיסמה המקורית מול ההאש
    assert verify_password(pwd, hashed) is True


def test_invalid_password_rejection():
    """
    בדיקת דחיית סיסמה שגויה.
    מוודא שמנגנון ה-Verify יודע לחסום ניסיונות גישה עם סיסמאות לא תואמות.
    """
    correct_pwd = "my_secure_password"
    wrong_pwd = "wrong_password"
    hashed = hash_password(correct_pwd)

    # וידוא שסיסמה שגויה מחזירה False ולא מאפשרת כניסה
    assert verify_password(wrong_pwd, hashed) is False


def test_security_robustness():
    """
    בדיקת עמידות המנגנון.
    מוודא שהמערכת מטפלת בצורה תקינה גם בסיסמאות הכוללות תווים מיוחדים.
    """
    special_pwd = "Pass!@#123_$%^"
    hashed = hash_password(special_pwd)
    assert verify_password(special_pwd, hashed) is True