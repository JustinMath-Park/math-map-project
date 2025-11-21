"""Seed lecture flow data into Firestore."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT.parent / 'backend' / '.env'
DATA_PATH = ROOT / 'data' / 'lectures.json'
COLLECTION_NAME = os.getenv('LECTURE_COLLECTION', 'lecture_flows')

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

PROJECT_ID = os.getenv('PROJECT_ID', 'my-mvp-backend')
SERVICE_ACCOUNT_KEY = os.getenv('SERVICE_ACCOUNT_KEY', 'your-service-account-key.json')


def init_firestore():
    key_path = Path(SERVICE_ACCOUNT_KEY)
    if not key_path.is_absolute():
        backend_candidate = ROOT.parent / 'backend' / SERVICE_ACCOUNT_KEY
        repo_candidate = ROOT / SERVICE_ACCOUNT_KEY
        if backend_candidate.exists():
            key_path = backend_candidate
        elif repo_candidate.exists():
            key_path = repo_candidate

    try:
        firebase_admin.get_app()
    except ValueError:
        if key_path.exists():
            cred = credentials.Certificate(str(key_path))
            firebase_admin.initialize_app(cred, options={'projectId': PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={'projectId': PROJECT_ID})
    return firestore.client()


def seed_lectures():
    with open(DATA_PATH, 'r', encoding='utf-8') as fp:
        payload = json.load(fp)

    db = init_firestore()
    for lecture in payload:
        lecture_id = lecture.get('lecture_id')
        if not lecture_id:
            continue
        db.collection(COLLECTION_NAME).document(lecture_id).set(lecture)
        print(f"[OK] Upserted lecture {lecture_id}")


if __name__ == '__main__':
    seed_lectures()
