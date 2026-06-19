import uuid
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_observations_collection, get_progress_collection


def submit_observation(child_id, focus_area, observation_text):
    observations = get_observations_collection()

    # An observation is only valid when no observation for the same focus area
    # was already recorded within the same calendar day (UTC session window).
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    duplicate = observations.find_one({
        "child_id": child_id,
        "focus_area": focus_area,
        "submitted_at": {"$gte": today}
    })
    is_valid = duplicate is None

    obs = {
        "obs_id": str(uuid.uuid4()),
        "child_id": child_id,
        "focus_area": focus_area,
        "observation_text": observation_text,
        "submitted_at": datetime.utcnow(),
        "is_valid": is_valid
    }
    observations.insert_one(obs)
    update_progress_score(child_id)

    if is_valid:
        msg = "Observation saved successfully!"
    else:
        msg = (
            f"Observation saved, but not counted toward progress — "
            f"a {focus_area} observation was already recorded today."
        )
    return True, is_valid, msg


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

    # is_valid: {"$ne": False} treats both True and legacy documents (no field) as valid.
    total_observations = observations.count_documents({
        "child_id": child_id,
        "is_valid": {"$ne": False}
    })

    # Both the observation score component and active-weeks use the same 12-week window.
    recency_cutoff = datetime.utcnow() - timedelta(weeks=12)
    recent_valid = list(observations.find({
        "child_id": child_id,
        "is_valid": {"$ne": False},
        "submitted_at": {"$gte": recency_cutoff}
    }))

    recent_observations = len(recent_valid)
    # Score uses only observations within the recency window, capped at 20.
    valid_obs = min(recent_observations, 20)

    weeks = set()
    for obs in recent_valid:
        week = obs["submitted_at"].isocalendar()[:2]  # (ISO year, ISO week number)
        weeks.add(week)

    active_weeks = min(len(weeks), 12)

    # Composite score: max 40 pts from observations + max 60 pts from weeks, capped at 100.
    score = min((valid_obs * 2) + (active_weeks * 5), 100)

    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    progress.update_one(
        {"child_id": child_id},
        {
            "$set": {
                "child_id": child_id,
                "composite_score": score,
                "progress_level": level,
                "valid_observations": valid_obs,
                "total_observations": total_observations,
                "recent_observations": recent_observations,
                "active_weeks": active_weeks,
                "last_update": datetime.utcnow()
            },
            "$push": {
                "score_history": {
                    "score": score,
                    "level": level,
                    "recorded_at": datetime.utcnow()
                }
            }
        },
        upsert=True
    )
    return score, level


def get_progress_record(child_id):
    progress = get_progress_collection()
    return progress.find_one({"child_id": child_id})
