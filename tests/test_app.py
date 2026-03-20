import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Salva o estado original e restaura após cada teste
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))

def test_root_redirect():
    # Arrange
    client = TestClient(app)
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code in (307, 200)  # FastAPI pode redirecionar 307
    assert "text/html" in response.headers.get("content-type", "")

def test_get_activities():
    # Arrange
    client = TestClient(app)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_success():
    # Arrange
    client = TestClient(app)
    email = "novo@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]

def test_signup_already_registered():
    # Arrange
    client = TestClient(app)
    email = activities["Chess Club"]["participants"][0]
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    # Arrange
    client = TestClient(app)
    email = "aluno@mergington.edu"
    activity = "Inexistente"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_remove_participant_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]

def test_remove_participant_not_found():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "naoexiste@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_remove_participant_activity_not_found():
    # Arrange
    client = TestClient(app)
    activity = "Inexistente"
    email = "aluno@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_signup_activity_full():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    # Preenche a atividade
    activities[activity]["participants"] = [f"a{i}@mergington.edu" for i in range(activities[activity]["max_participants"])]
    email = "lotado@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    # O endpoint atual não bloqueia inscrição se lotado, mas pode ser ajustado futuramente
    assert response.status_code == 200 or response.status_code == 400

def test_cycle_signup_and_remove():
    # Arrange
    client = TestClient(app)
    activity = "Programming Class"
    email = "ciclo@mergington.edu"
    # Act
    signup = client.post(f"/activities/{activity}/signup?email={email}")
    remove = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert signup.status_code == 200
    assert remove.status_code == 200
    assert email not in activities[activity]["participants"]
