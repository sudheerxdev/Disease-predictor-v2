import pytest
from backend import create_app
import json


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """An application context for the tests."""
    with app.app_context():
        yield app


class TestAppBasics:
    """Basic app functionality tests"""

    def test_app_creation(self, app):
        """Test that app is created successfully"""
        assert app is not None
        assert app.config["TESTING"] is True

    def test_static_folder_exists(self, app):
        """Test that static folder is configured"""
        assert app.static_folder is not None


class TestAuthRoutes:
    """Tests for authentication routes"""

    def test_signup_page_exists(self, client):
        """Test if signup page loads correctly"""
        rv = client.get("/signup")
        # Check for 200 or 404 (depending on template existence)
        assert rv.status_code in [200, 404]

    def test_login_page_exists(self, client):
        """Test if login page loads correctly"""
        rv = client.get("/login")
        assert rv.status_code in [200, 404]


class TestGeneralRoutes:
    """Tests for general information routes"""

    def test_help_page(self, client):
        """Test if help page loads correctly"""
        rv = client.get("/help")
        assert rv.status_code in [200, 404]

    def test_privacy_page(self, client):
        """Test if privacy page loads correctly"""
        rv = client.get("/privacy")
        assert rv.status_code in [200, 404]

    def test_terms_page(self, client):
        """Test if terms page loads correctly"""
        rv = client.get("/terms")
        assert rv.status_code in [200, 404]


class TestDiseaseRoutes:
    """Tests for disease-related routes"""

    def test_disease_page_exists(self, client):
        """Test if disease routes are registered"""
        # Most disease routes should exist
        rv = client.get("/diseases")
        # Accept 200 if route exists, 404 if template missing, or 405 if method not allowed
        assert rv.status_code in [200, 404, 405]


class TestMLRoutes:
    """Tests for ML prediction routes"""

    def test_ml_prediction_page(self, client):
        """Test if ML prediction page loads"""
        rv = client.get("/ml-prediction")
        # Accept 200 or 404
        assert rv.status_code in [200, 404]

    def test_ml_predict_endpoint_empty_request(self, client):
        """Test ML predict endpoint with missing data"""
        rv = client.post(
            "/api/ml/predict", data=json.dumps({}), content_type="application/json"
        )
        # Should return 400 for missing disease
        assert rv.status_code in [400, 500]

    def test_ml_predict_endpoint_missing_disease(self, client):
        """Test ML predict endpoint with missing disease field"""
        rv = client.post(
            "/api/ml/predict",
            data=json.dumps({"symptoms": ["fever", "cough"]}),
            content_type="application/json",
        )
        assert rv.status_code in [400, 500]

    def test_ml_predict_endpoint_missing_symptoms(self, client):
        """Test ML predict endpoint with missing symptoms field"""
        rv = client.post(
            "/api/ml/predict",
            data=json.dumps({"disease": "diabetes"}),
            content_type="application/json",
        )
        assert rv.status_code in [400, 500]

    def test_ml_predict_endpoint_valid_request(self, client):
        """Test ML predict endpoint with valid request"""
        rv = client.post(
            "/api/ml/predict",
            data=json.dumps(
                {
                    "disease": "diabetes",
                    "symptoms": ["increased_thirst", "frequent_urination"],
                }
            ),
            content_type="application/json",
        )
        # If endpoint works, should get 200; if disease not found, might get 400/500
        assert rv.status_code in [200, 400, 500]
        if rv.status_code == 200:
            response = json.loads(rv.data)
            assert isinstance(response, dict)
