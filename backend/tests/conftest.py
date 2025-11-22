import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

@pytest.fixture
def app():
    # Mock Firebase and AI client to avoid connecting to real services during tests
    with patch('app.initialize_firebase') as mock_firebase, \
         patch('app.initialize_ai_client') as mock_ai:
        
        # Setup mocks
        mock_db = MagicMock()
        mock_firebase.return_value = mock_db
        
        mock_ai_client = MagicMock()
        mock_ai.return_value = mock_ai_client
        
        app = create_app()
        app.config.update({
            "TESTING": True,
        })
        
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
