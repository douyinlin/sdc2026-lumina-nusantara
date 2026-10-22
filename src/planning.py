"""Pure role filtering and sequential study-duration calculations."""
import math

def filter_roles(roles, metadata, persona, field, domains, adjacent):
    if persona == "worker" and field == "all":
        return list(roles)
    primary = domains.get(field)
    if primary is None:
        raise ValueError("Unknown field")
    same = [r for r in roles if metadata[r.name]["domain"] == primary]
    near = [r for r in roles if metadata[r.name]["domain"] in adjacent.get(primary, [])]
    return same or near or list(roles)

def learning_duration(skill: str, courses: dict, hours_per_week: float) -> dict:
    if isinstance(hours_per_week, bool) or not isinstance(hours_per_week, (int, float)) or not math.isfinite(hours_per_week) or hours_per_week <= 0:
        raise ValueError("Weekly study hours must be finite and positive")
    course = courses.get(skill, {})
    hours = course.get("hours")
    if isinstance(hours, (int, float)) and not isinstance(hours, bool) and math.isfinite(hours) and hours > 0:
        basis = "duration_verified" if course.get("duration_verified") is True and course.get("duration_source_url") else "duration_catalogue"
    else:
        # Explicit prototype assumption, retained from the original 8h/week model.
        from src.utils import GAP_COST
        hours = max(1, round(GAP_COST.get(skill, 0.7) * 6)) * 8
        basis = "duration_team"
    return {"hours": hours, "weeks": math.ceil(hours / hours_per_week), "basis": basis}
