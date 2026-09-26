import importlib
import os
import tempfile
import unittest

from services.coaching.dashboard_plan import build_weekly_plan, format_plan_label


class DashboardPlanStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_data.db")

        self.repository = importlib.import_module("services.persistence.exercise_repository")
        self.repository._DB_PATH = self.db_path
        self.repository.init_db()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_retrieve_user_plan(self):
        user = self.repository.create_user("coach-user")
        plan = {
            "goal": "muscle gain and strength",
            "days_per_week": 5,
            "workout_days": [{"day": "Monday", "exercises": ["Squats"]}],
            "diet_plan": [{"meal": "Breakfast", "suggestion": "Eggs and oats"}],
        }

        self.repository.save_user_plan(user["id"], plan)
        loaded_plan = self.repository.get_user_plan(user["id"])

        self.assertEqual(loaded_plan["goal"], plan["goal"])
        self.assertEqual(loaded_plan["days_per_week"], plan["days_per_week"])
        self.assertEqual(loaded_plan["workout_days"][0]["day"], "Monday")

    def test_plan_labels_are_readable(self):
        plan = build_weekly_plan("general_fitness", "full_body", "beginner", 3)

        self.assertEqual(plan["workout_days"][0]["focus"], "Full Body Focus")
        self.assertEqual(format_plan_label("_array_Monday"), "Monday")
        self.assertEqual(format_plan_label("_array_Tuesday"), "Tuesday")
        self.assertEqual(format_plan_label(["Wednesday"]), "Wednesday")
        self.assertEqual(format_plan_label(["_array_", "Thursday"]), "Thursday")
        self.assertNotIn("_array_", format_plan_label("_array_right"))
        self.assertEqual(format_plan_label("Full_Body focus"), "Full Body focus")


if __name__ == "__main__":
    unittest.main()
