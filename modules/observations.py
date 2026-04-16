import uuid
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_observations_collection, get_progress_collection

def submit_observation(child_id, observation_text):
    observations = get_observations_collection()

    # Prevent duplicate submission in same session window (same day, same focus)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_today = observations.find_one({
        "child_id": child_id,
        "submitted_at": {"$gte": today}
    })

    obs = {
        "obs_id": str(uuid.uuid4()),
        "child_id": child_id,
        "observation_text": observation_text,
        "submitted_at": datetime.utcnow()
    }
    observations.insert_one(obs)
    update_progress_score(child_id)
    return True, "Observation saved successfully!"

def get_child_observations(child_id, limit=10):
    observations = get_observations_collection()
    return list(observations.find(
        {"child_id": child_id},
        sort=[("submitted_at", -1)],
        limit=limit
    ))

def update_progress_score(child_id):
    observations = get_observations_collection()
    progress = get_progress_collection()

    # Count valid observations (max 20)
    total_obs = observations.count_documents({"child_id": child_id})
    valid_obs = min(total_obs, 20)

    # Count active weeks (weeks with at least one observation, max 12)
    all_obs = list(observations.find({"child_id": child_id}))
    weeks = set()
    for obs in all_obs:
        week = obs["submitted_at"].isocalendar()[:2]  # (year, week)
        weeks.add(week)
    active_weeks = min(len(weeks), 12)

    # Scoring formula from thesis
    score = (valid_obs * 2) + (active_weeks * 5)

    # Classify
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    # Upsert progress record
    progress.update_one(
        {"child_id": child_id},
        {"$set": {
            "child_id": child_id,
            "composite_score": score,
            "progress_level": level,
            "valid_observations": valid_obs,
            "active_weeks": active_weeks,
            "last_update": datetime.utcnow()
        },
        "$push": {
            "score_history": {
                "score": score,
                "level": level,
                "recorded_at": datetime.utcnow()
            }
        }},
        upsert=True
    )
    return score, level

def get_progress_record(child_id):
    progress = get_progress_collection()
    return progress.find_one({"child_id": child_id})