# Copyright 2026 Google LLC
# Seed script for initializing the exercises collection in Firestore.

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-675a8fdff8e3"

INITIAL_EXERCISES = [
    {
        "id": "ex-001",
        "name": "Barbell Back Squats",
        "muscle_group": "Legs",
        "difficulty": "Intermediate",
        "description": "Compound lower body exercise targeting quadriceps, glutes, and hamstrings.",
        "recommended_reps": "4 sets of 8-12 reps",
        "calories_burned_per_min": 8,
    },
    {
        "id": "ex-002",
        "name": "Push-ups",
        "muscle_group": "Chest",
        "difficulty": "Beginner",
        "description": "Bodyweight upper body exercise targeting chest, shoulders, and triceps.",
        "recommended_reps": "3 sets of 15-20 reps",
        "calories_burned_per_min": 6,
    },
    {
        "id": "ex-003",
        "name": "Romanian Deadlifts",
        "muscle_group": "Posterior Chain",
        "difficulty": "Intermediate",
        "description": "Hip-hinge movement focusing on hamstrings, glutes, and lower back.",
        "recommended_reps": "3 sets of 10-12 reps",
        "calories_burned_per_min": 7,
    },
    {
        "id": "ex-004",
        "name": "HIIT Jump Rope",
        "muscle_group": "Cardio",
        "difficulty": "All Levels",
        "description": "High-intensity cardio interval training for endurance and agility.",
        "recommended_reps": "5 intervals of 2 mins",
        "calories_burned_per_min": 12,
    },
    {
        "id": "ex-005",
        "name": "Pull-ups",
        "muscle_group": "Back",
        "difficulty": "Intermediate",
        "description": "Upper body pulling exercise strengthening lats, rhomboids, and biceps.",
        "recommended_reps": "3 sets of 8-10 reps",
        "calories_burned_per_min": 8,
    },
]


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("exercises")
    
    print(f"Seeding Firestore collection 'exercises' in project {PROJECT_ID}...")
    for exercise in INITIAL_EXERCISES:
        doc_ref = collection_ref.document(exercise["id"])
        doc_ref.set(exercise)
        print(f"  ✓ Added exercise: {exercise['name']} ({exercise['id']})")
    
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
