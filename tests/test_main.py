import pytest
from app.models.student import StudentCreate, StudentUpdate
from app.models.user import UserCreate, UserUpdate
from app.schemas.auth import LoginRequest, Token
from app.auth.security import verify_password, get_password_hash, create_access_token, decode_access_token
from datetime import timedelta


def test_student_create_valid():
    student = StudentCreate(
        name="John Doe",
        course="BCA",
        college="Test College",
        admission_through="KCET"
    )
    assert student.name == "John Doe"
    assert student.admission_through == "KCET"


def test_student_create_invalid_admission():
    with pytest.raises(ValueError):
        StudentCreate(
            name="John Doe",
            course="BCA",
            college="Test College",
            admission_through="INVALID"
        )


def test_student_create_missing_fields():
    with pytest.raises(ValueError):
        StudentCreate(
            name="John Doe"
        )


def test_student_update_valid():
    update = StudentUpdate(
        name="Jane Doe",
        course="MCA"
    )
    assert update.name == "Jane Doe"
    assert update.course == "MCA"
    assert update.college is None


def test_user_create_valid():
    user = UserCreate(
        username="testuser",
        password="password123",
        role="staff"
    )
    assert user.username == "testuser"
    assert user.role == "staff"


def test_user_create_invalid_role():
    with pytest.raises(ValueError):
        UserCreate(
            username="testuser",
            password="password123",
            role="invalid"
        )


def test_login_request():
    login = LoginRequest(username="admin", password="password")
    assert login.username == "admin"
    assert login.password == "password"


def test_token_schema():
    token = Token(access_token="test_token", token_type="bearer")
    assert token.access_token == "test_token"
    assert token.token_type == "bearer"


def test_password_hashing():
    password = "test_password_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_creation():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))

    assert isinstance(token, str)
    assert len(token) > 0


def test_jwt_token_decoding():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "testuser"


def test_jwt_token_invalid():
    payload = decode_access_token("invalid_token")
    assert payload is None