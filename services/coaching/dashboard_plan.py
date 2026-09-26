import os
import re
import textwrap
from collections import defaultdict
from io import BytesIO

import streamlit as st
from services.persistence.exercise_repository import delete_user_plan, get_user_plan, save_user_plan


WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def format_plan_label(value) -> str:
    """Convert stored plan values into clean readable labels."""

    if value is None:
        return ""

    values = value if isinstance(value, (list, tuple)) else [value]
    for item in values:
        item_text = str(item)
        for weekday in WEEKDAYS:
            if weekday.lower() in item_text.lower():
                return weekday

    label = str(values[0]) if values else ""

    # Remove the prefix produced when a one-item array is stringified.
    label = re.sub(r'^_array_+', '', label, flags=re.IGNORECASE)

    # Remove brackets and quotes
    label = label.replace("[", "").replace("]", "")
    label = label.replace("'", "").replace('"', "")

    # Replace underscores with spaces
    label = label.replace("_", " ")

    return label.strip()


def build_weekly_plan(goal: str, focus_area: str, experience: str, days_per_week: int) -> dict:
    focus_map = {
        "fat_loss": "fat loss and conditioning",
        "muscle_gain": "muscle gain and strength",
        "endurance": "endurance and stamina",
        "general_fitness": "general fitness",
    }
    experience_map = {
        "beginner": "beginner-friendly",
        "intermediate": "balanced",
        "advanced": "challenging but sustainable",
    }

    goal_text = focus_map.get(goal, goal)
    experience_text = experience_map.get(experience, experience)

    days = max(3, min(days_per_week, 7))
    plan = {
        "goal": goal_text,
        "experience": experience_text,
        "days_per_week": days,
        "workout_days": [],
        "diet_plan": [],
    }

    workout_templates = [
        ("Monday", ["Squats", "Push-ups", "Plank"]),
        ("Tuesday", ["Lunges", "Shoulder Press", "Dead Bug"]),
        ("Wednesday", ["Biceps Curls (Dumbbell)", "Lat Pulldown", "Bird Dog"]),
        ("Thursday", ["Romanian Deadlift", "Burpees", "Side Plank"]),
        ("Friday", ["Barbell Bench Press", "Pull-ups", "Mountain Climbers"]),
        ("Saturday", ["Hip Thrust", "Jump Rope", "Russian Twist"]),
        ("Sunday", ["Walking", "Stretching", "Mobility"]),
    ]

    for day_name, exercises in workout_templates[:days]:
        plan["workout_days"].append({
            "day": day_name,
            "focus": f"{format_plan_label(focus_area).title()} Focus",
            "exercises": exercises,
        })

    protein_target = "protein-rich meals" if goal in {"muscle_gain", "fat_loss"} else "balanced meals"
    plan["diet_plan"] = [
        {
            "meal": "Breakfast",
            "suggestion": "Greek yogurt, oats, berries, and a boiled egg",
        },
        {
            "meal": "Lunch",
            "suggestion": f"Grilled chicken or tofu bowl with brown rice and vegetables for {protein_target}",
        },
        {
            "meal": "Dinner",
            "suggestion": "Salmon or lentil curry with sweet potato and greens",
        },
        {
            "meal": "Snack",
            "suggestion": "Apple with peanut butter or a protein shake",
        },
    ]

    return plan


def build_coach_summary(plan: dict) -> str:
    goal = plan.get("goal", "")
    experience = plan.get("experience", "")
    days = plan.get("days_per_week", 0)

    if "muscle" in goal.lower():
        return (
            f"Coach summary: prioritize progressive overload, keep protein intake high, and recover well across {days} training days."
        )
    if "fat" in goal.lower():
        return (
            f"Coach summary: maintain consistency, keep meals structured, and focus on steady cardio and recovery across {days} training days."
        )
    if "endurance" in goal.lower():
        return (
            f"Coach summary: build stamina gradually, stay hydrated, and pace your effort for sustainable progress over {days} days."
        )
    return (
        f"Coach summary: keep the routine balanced, stay consistent, and adjust intensity based on your {experience} level."
    )


def build_day_tip(day_name: str, focus_area: str, goal: str) -> str:
    if "Monday" in day_name or "Wednesday" in day_name:
        return "Start with controlled reps and focus on form before adding intensity."
    if "Friday" in day_name or "Saturday" in day_name:
        return "Use a strong finish, but keep your effort sustainable and avoid overtraining."
    if "Sunday" in day_name:
        return "Treat this as recovery and mobility work to support the rest of the week."
    if "muscle" in goal.lower():
        return "Keep your tempo steady and push near fatigue with good form."
    if "fat" in goal.lower():
        return "Stay active and keep your pacing brisk to support calorie burn."
    if "endurance" in goal.lower():
        return "Aim for smooth effort and steady breathing throughout the session."
    return "Stay consistent and keep your effort balanced for the day."


def render_dashboard():
    st.title("🧠 Personal Coach Dashboard")
    st.markdown("Create a weekly workout and nutrition plan tailored to your goals.")

    if "dashboard_plan" not in st.session_state:
        st.session_state.dashboard_plan = None

    user_id = st.session_state.get("user_id")
    if user_id is not None and st.session_state.dashboard_plan is None:
        saved_plan = get_user_plan(user_id)
        if saved_plan:
            st.session_state.dashboard_plan = saved_plan

    with st.form("dashboard_form"):
        goal = st.selectbox(
            "Primary goal",
            options=["fat_loss", "muscle_gain", "endurance", "general_fitness"],
            format_func=lambda x: {
                "fat_loss": "Fat loss",
                "muscle_gain": "Muscle gain",
                "endurance": "Endurance",
                "general_fitness": "General fitness",
            }[x],
        )
        focus_area = st.selectbox(
            "Focus area",
            options=["full_body", "upper_body", "lower_body", "core"],
            format_func=lambda x: {
                "full_body": "Full body",
                "upper_body": "Upper body",
                "lower_body": "Lower body",
                "core": "Core",
            }[x],
        )
        experience = st.selectbox(
            "Experience level",
            options=["beginner", "intermediate", "advanced"],
            format_func=lambda x: {
                "beginner": "Beginner",
                "intermediate": "Intermediate",
                "advanced": "Advanced",
            }[x],
        )
        days_per_week = st.slider("Training days per week", min_value=3, max_value=7, value=5)
        submitted = st.form_submit_button("Generate weekly plan")

    if submitted:
        st.session_state.dashboard_plan = build_weekly_plan(goal, focus_area, experience, days_per_week)
        if user_id is not None:
            save_user_plan(user_id, st.session_state.dashboard_plan)

    plan = st.session_state.dashboard_plan

    if plan:
        st.success(f"Weekly plan generated for {plan['goal']} with {plan['days_per_week']} training days.")

        st.markdown("### 🧾 Latest Saved Plan")
        card_col1, card_col2, card_col3 = st.columns(3)
        card_col1.metric("Goal", plan["goal"].title())
        card_col2.metric("Training Days", plan["days_per_week"])
        card_col3.metric("Diet Entries", len(plan["diet_plan"]))

        st.info(build_coach_summary(plan))
        st.markdown("---")
        st.subheader("🏋️ Weekly Workout Plan")
        for day_index, day in enumerate(plan["workout_days"]):
            day_name = WEEKDAYS[day_index] if day_index < len(WEEKDAYS) else format_plan_label(day["day"])
            focus = format_plan_label(day["focus"]).title()
            with st.container(border=True):
                st.markdown(f"### {day_name}")
                st.write(f"**Focus:** {focus}")
                st.write(f"💡 {build_day_tip(day_name, focus, plan['goal'])}")
                st.write("**Exercises:**")
                st.write("- " + "\n- ".join(day["exercises"]))

        st.markdown("---")
        st.subheader("🥗 Weekly Diet Plan")
        for entry in plan["diet_plan"]:
            st.write(f"**{entry['meal']}:** {entry['suggestion']}")

        st.markdown("---")
        export_text = "\n".join([
            f"Weekly Plan",
            f"Goal: {plan['goal']}",
            f"Training Days: {plan['days_per_week']}",
            "",
            "Workout Plan:",
            *[
                f"- {format_plan_label(day['day'])}: {format_plan_label(day['focus']).title()} -> {', '.join(day['exercises'])}"
                for day in plan["workout_days"]
            ],
            "",
            "Diet Plan:",
            *[f"- {entry['meal']}: {entry['suggestion']}" for entry in plan['diet_plan']],
        ])

        st.download_button(
            label="Download plan as .txt",
            data=export_text,
            file_name="weekly_plan.txt",
            mime="text/plain",
        )

        if st.button("Clear saved plan", key="clear_plan_button"):
            if user_id is not None:
                delete_user_plan(user_id)
            st.session_state.dashboard_plan = None
            st.rerun()

        st.caption("Coach note: Keep protein intake high, hydrate well, and progress gradually.")
    else:
        st.info("Fill out the form to create your first personalized plan.")
