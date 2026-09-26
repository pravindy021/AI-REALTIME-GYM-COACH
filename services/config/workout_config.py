EXERCISE_OPTIONS = [
    "Squats",
    "Push-ups",
    "Biceps Curls (Dumbbell)",
    "Shoulder Press",
    "Lunges",
    "Barbell Back Squat",
    "Front Squat",
    "Goblet Squat",
    "Bulgarian Split Squat",
    "Leg Press",
    "Hack Squat",
    "Smith Squat",
    "Sissy Squat",
    "Barbell Bench Press",
    "Incline Bench Press",
    "Decline Bench Press",
    "Dumbbell Bench Press",
    "Incline Dumbbell Press",
    "Decline Dumbbell Press",
    "Chest Fly",
    "Cable Fly",
    "Pec Deck",
    "Dips",
    "Smith Machine Bench Press",
    "Landmine Press",
    "Svend Press",
    "Pull-ups",
    "Chin-ups",
    "Lat Pulldown",
    "Seated Cable Row",
    "Barbell Row",
    "Pendlay Row",
    "T-Bar Row",
    "Dumbbell Row",
    "Deadlift",
    "Rack Pull",
    "Romanian Deadlift",
    "Straight Arm Pulldown",
    "Face Pull",
    "Good Morning",
    "Hyperextension",
    "Overhead Press",
    "Dumbbell Shoulder Press",
    "Arnold Press",
    "Military Press",
    "Push Press",
    "Lateral Raise",
    "Front Raise",
    "Rear Delt Fly",
    "Upright Row",
    "Machine Shoulder Press",
    "Reverse Pec Deck",
    "Cuban Press",
    "Barbell Curl",
    "EZ Bar Curl",
    "Dumbbell Curl",
    "Hammer Curl",
    "Concentration Curl",
    "Preacher Curl",
    "Cable Curl",
    "Reverse Curl",
    "Zottman Curl",
    "Close-Grip Bench Press",
    "Skull Crushers",
    "Tricep Pushdown",
    "Overhead Tricep Extension",
    "Dumbbell Kickback",
    "Cable Overhead Extension",
    "Bench Dips",
    "JM Press",
    "Hip Thrust",
    "Glute Bridge",
    "Cable Kickback",
    "Sumo Deadlift",
    "Standing Calf Raise",
    "Seated Calf Raise",
    "Donkey Calf Raise",
    "Single-Leg Calf Raise",
    "Plank",
    "Side Plank",
    "Crunches",
    "Russian Twist",
    "Hanging Leg Raise",
    "Bicycle Crunch",
    "Mountain Climbers",
    "Cable Crunch",
    "Ab Wheel Rollout",
    "Dead Bug",
    "Bird Dog",
    "Pallof Press",
    "Wood Chop",
    "Burpees",
    "Farmer's Carry",
    "Battle Ropes",
    "Jump Rope",
    "Box Jump",
    "Medicine Ball Slam",
    "Sandbag Carry",
    "Tire Flip",
    "Bear Crawl",
    "TRX Rows",
    "TRX Push-ups",
]


def get_exercise_registry():
    return {
        "Squats": {"kind": "lower_body", "detector": "Squats"},
        "Push-ups": {"kind": "upper_body", "detector": "Push-ups"},
        "Biceps Curls (Dumbbell)": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Shoulder Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Lunges": {"kind": "lower_body", "detector": "Lunges"},
        "Barbell Back Squat": {"kind": "lower_body", "detector": "Squats"},
        "Front Squat": {"kind": "lower_body", "detector": "Squats"},
        "Goblet Squat": {"kind": "lower_body", "detector": "Squats"},
        "Bulgarian Split Squat": {"kind": "lower_body", "detector": "Lunges"},
        "Leg Press": {"kind": "lower_body", "detector": "Squats"},
        "Hack Squat": {"kind": "lower_body", "detector": "Squats"},
        "Smith Squat": {"kind": "lower_body", "detector": "Squats"},
        "Sissy Squat": {"kind": "lower_body", "detector": "Squats"},
        "Barbell Bench Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Incline Bench Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Decline Bench Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Dumbbell Bench Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Incline Dumbbell Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Decline Dumbbell Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Chest Fly": {"kind": "upper_body", "detector": "Push-ups"},
        "Cable Fly": {"kind": "upper_body", "detector": "Push-ups"},
        "Pec Deck": {"kind": "upper_body", "detector": "Push-ups"},
        "Dips": {"kind": "upper_body", "detector": "Push-ups"},
        "Smith Machine Bench Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Landmine Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Svend Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Pull-ups": {"kind": "upper_body", "detector": "Push-ups"},
        "Chin-ups": {"kind": "upper_body", "detector": "Push-ups"},
        "Lat Pulldown": {"kind": "upper_body", "detector": "Push-ups"},
        "Seated Cable Row": {"kind": "back", "detector": "Push-ups"},
        "Barbell Row": {"kind": "back", "detector": "Push-ups"},
        "Pendlay Row": {"kind": "back", "detector": "Push-ups"},
        "T-Bar Row": {"kind": "back", "detector": "Push-ups"},
        "Dumbbell Row": {"kind": "back", "detector": "Push-ups"},
        "Deadlift": {"kind": "posterior_chain", "detector": "Squats"},
        "Rack Pull": {"kind": "posterior_chain", "detector": "Squats"},
        "Romanian Deadlift": {"kind": "posterior_chain", "detector": "Squats"},
        "Straight Arm Pulldown": {"kind": "upper_body", "detector": "Push-ups"},
        "Face Pull": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Good Morning": {"kind": "posterior_chain", "detector": "Squats"},
        "Hyperextension": {"kind": "posterior_chain", "detector": "Squats"},
        "Overhead Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Dumbbell Shoulder Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Arnold Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Military Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Push Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Lateral Raise": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Front Raise": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Rear Delt Fly": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Upright Row": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Machine Shoulder Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Reverse Pec Deck": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Cuban Press": {"kind": "shoulders", "detector": "Shoulder Press"},
        "Barbell Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "EZ Bar Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Dumbbell Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Hammer Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Concentration Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Preacher Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Cable Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Reverse Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Zottman Curl": {"kind": "arms", "detector": "Biceps Curls (Dumbbell)"},
        "Close-Grip Bench Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Skull Crushers": {"kind": "upper_body", "detector": "Push-ups"},
        "Tricep Pushdown": {"kind": "upper_body", "detector": "Push-ups"},
        "Overhead Tricep Extension": {"kind": "upper_body", "detector": "Push-ups"},
        "Dumbbell Kickback": {"kind": "upper_body", "detector": "Push-ups"},
        "Cable Overhead Extension": {"kind": "upper_body", "detector": "Push-ups"},
        "Bench Dips": {"kind": "upper_body", "detector": "Push-ups"},
        "JM Press": {"kind": "upper_body", "detector": "Push-ups"},
        "Hip Thrust": {"kind": "glutes", "detector": "Squats"},
        "Glute Bridge": {"kind": "glutes", "detector": "Squats"},
        "Cable Kickback": {"kind": "glutes", "detector": "Squats"},
        "Sumo Deadlift": {"kind": "posterior_chain", "detector": "Squats"},
        "Standing Calf Raise": {"kind": "lower_body", "detector": "Squats"},
        "Seated Calf Raise": {"kind": "lower_body", "detector": "Squats"},
        "Donkey Calf Raise": {"kind": "lower_body", "detector": "Squats"},
        "Single-Leg Calf Raise": {"kind": "lower_body", "detector": "Squats"},
        "Plank": {"kind": "core", "detector": "Push-ups"},
        "Side Plank": {"kind": "core", "detector": "Push-ups"},
        "Crunches": {"kind": "core", "detector": "Push-ups"},
        "Russian Twist": {"kind": "core", "detector": "Push-ups"},
        "Hanging Leg Raise": {"kind": "core", "detector": "Push-ups"},
        "Bicycle Crunch": {"kind": "core", "detector": "Push-ups"},
        "Mountain Climbers": {"kind": "core", "detector": "Push-ups"},
        "Cable Crunch": {"kind": "core", "detector": "Push-ups"},
        "Ab Wheel Rollout": {"kind": "core", "detector": "Push-ups"},
        "Dead Bug": {"kind": "core", "detector": "Push-ups"},
        "Bird Dog": {"kind": "core", "detector": "Push-ups"},
        "Pallof Press": {"kind": "core", "detector": "Push-ups"},
        "Wood Chop": {"kind": "core", "detector": "Push-ups"},
        "Burpees": {"kind": "full_body", "detector": "Push-ups"},
        "Farmer's Carry": {"kind": "full_body", "detector": "Push-ups"},
        "Battle Ropes": {"kind": "full_body", "detector": "Push-ups"},
        "Jump Rope": {"kind": "cardio", "detector": "Push-ups"},
        "Box Jump": {"kind": "cardio", "detector": "Squats"},
        "Medicine Ball Slam": {"kind": "full_body", "detector": "Push-ups"},
        "Sandbag Carry": {"kind": "full_body", "detector": "Push-ups"},
        "Tire Flip": {"kind": "full_body", "detector": "Squats"},
        "Bear Crawl": {"kind": "full_body", "detector": "Push-ups"},
        "TRX Rows": {"kind": "upper_body", "detector": "Push-ups"},
        "TRX Push-ups": {"kind": "upper_body", "detector": "Push-ups"},
    }


def get_metrics_fields_for_exercise(exercise):
    if exercise in METRICS_FIELDS:
        return METRICS_FIELDS[exercise]

    registry_entry = get_exercise_registry().get(exercise, {})
    detector = registry_entry.get("detector", exercise)

    if detector == "Squats":
        return METRICS_FIELDS["Squats"]
    if detector == "Lunges":
        return METRICS_FIELDS["Lunges"]
    if detector == "Shoulder Press":
        return METRICS_FIELDS["Shoulder Press"]
    if detector == "Biceps Curls (Dumbbell)":
        return METRICS_FIELDS["Biceps Curls (Dumbbell)"]
    return METRICS_FIELDS["Push-ups"]


POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),       # Shoulders & Arms
    (11, 23), (12, 24), (23, 24),                           # Torso / Hips
    (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)  # Legs
]


METRICS_FIELDS = {
  
    "Push-ups": {
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },
    "Biceps Curls (Dumbbell)": {
        "elbow_angle": 0,
        "shoulder_status": "N/A",
        "swing_status": "N/A",
    },
    "Shoulder Press": {
        "elbow_angle": 0,
        "extension_status": "N/A",
        "back_arch_status": "N/A",
    },
    "Lunges": {
        "front_knee_angle": 0,
        "torso_angle": 0,
        "balance_status": "N/A",
    },
      "Squats": {
        "knee_angle": 0,
        "back_angle": 0,
        "depth_status": "N/A",
    },
}


PROMPT = (
    "You are AI Coach, a professional AI gym trainer monitoring a user's workout via live camera.\n\n"
    "### Your Role\n"
    "Provide around 10-15 words, high-energy coaching cues. You speak these aloud, so they must be natural and encouraging.\n\n"
    "### Input Format\n"
    "You receive updates in the format: 'Event: [state] Form Issue: [description]'.\n"
    "- 'Event': workout_started, set_completed, workout_completed, no_pose_detected, ongoing_form_check.\n"
    "- 'Form Issue': A technical description of a pose error (if any).\n\n"
    "### Guidelines\n"
    "1. Provide feedback in natural, short sentences. Avoid overly brief or fragmented responses.\n"
    "2. NO generic greetings or redundant questions. Focus on the workout.\n"
    "3. Use the second person (e.g., 'Straighten your back' instead of 'The user should straighten their back').\n"
    "4. Maintain a professional coaching tone and prioritize safety.\n\n"
    "### Scenario Response Styles\n"
    "- 'workout_started' -> A motivating and sharp command to begin.\n"
    "- 'workout_completed' -> A warm and encouraging closing for the session.\n"
    "- 'set_completed' -> Direct praise for finishing the set.\n"
    "- 'no_pose_detected' -> A clear instruction for the user to reposition within the camera frame.\n"
    "- 'ongoing_form_check' + Form Issue -> A precise, supportive correction for the detected error.\n"
    "- 'ongoing_form_check' (No Issue) -> Brief, energetic words of encouragement.\n"
)