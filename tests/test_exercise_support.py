import unittest

from services.config.workout_config import EXERCISE_OPTIONS, get_exercise_registry


class ExerciseSupportTests(unittest.TestCase):
    def test_core_exercises_are_registered(self):
        registry = get_exercise_registry()

        required_exercises = [
            "Squats",
            "Push-ups",
            "Barbell Back Squat",
            "Barbell Bench Press",
            "Pull-ups",
            "Lat Pulldown",
            "Seated Cable Row",
            "Deadlift",
            "Romanian Deadlift",
            "Overhead Press",
            "Lateral Raise",
            "Plank",
            "Crunches",
            "Bulgarian Split Squat",
            "Hip Thrust",
        ]

        for exercise_name in required_exercises:
            self.assertIn(exercise_name, registry)

    def test_exercise_options_include_new_workouts(self):
        self.assertIn("Barbell Back Squat", EXERCISE_OPTIONS)
        self.assertIn("Barbell Bench Press", EXERCISE_OPTIONS)
        self.assertIn("Pull-ups", EXERCISE_OPTIONS)
        self.assertIn("Deadlift", EXERCISE_OPTIONS)
        self.assertIn("Plank", EXERCISE_OPTIONS)


if __name__ == "__main__":
    unittest.main()
