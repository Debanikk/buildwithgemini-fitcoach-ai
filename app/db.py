# Copyright 2026 Google LLC
# Firestore database initialization with hardcoded project ID for Agent Platform compatibility.

from google.cloud import firestore

# Hardcoded project ID as required for Agent Platform runtime compatibility
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-675a8fdff8e3"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT_ID)
