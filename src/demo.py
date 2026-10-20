"""Minimal Streamlit UI and validated synthetic catalogue (2026-10-20)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils import match_coverage, normalize_skills

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "demo.json"


def load_demo(path: Path = DATA_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("is_simulated") is not True:
        raise ValueError("Catalogue must explicitly identify simulated data.")
    skills = normalize_skills(data.get("skills"))
    if not skills or skills != sorted(data["skills"]):
        raise ValueError("Catalogue skills must be unique and normalized.")
    labels = data.get("labels")
    if not isinstance(labels, dict) or any(not isinstance(labels.get(s), str) or not labels[s].strip() for s in skills):
        raise ValueError("Every skill needs a display label.")
    profile = data.get("profile")
    if not isinstance(profile, dict) or not isinstance(profile.get("name"), str):
        raise ValueError("Missing synthetic profile.")
    if not set(normalize_skills(profile.get("skills"))) <= set(skills):
        raise ValueError("Unknown profile skill.")
    roles = data.get("roles")
    if not isinstance(roles, list) or len(roles) != 3:
        raise ValueError("The minimal demo requires exactly three roles.")
    names = set()
    for role in roles:
        if not isinstance(role, dict):
            raise ValueError("Malformed role record.")
        result = match_coverage([], role.get("name"), role.get("required_skills"))
        if result["role"] in names or not set(normalize_skills(role["required_skills"])) <= set(skills):
            raise ValueError("Duplicate role or unknown required skill.")
        names.add(result["role"])
    return data


def compare_skills(profile: object, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Server-side calculation used on every UI rerun and by the CLI."""
    skills = normalize_skills(profile)
    if not set(skills) <= set(data["skills"]):
        raise ValueError("Unknown skill; choose from the available options.")
    return [match_coverage(skills, role["name"], role["required_skills"]) for role in data["roles"]]


def render_demo() -> None:
    import streamlit as st

    st.title("SkillRadar MY · 第一版")
    st.caption("SDC Hackathon 2026 · Domain 1 · AI 时代职业转型与学习规划")
    st.warning("演示数据：用户为虚构人物；三个岗位及技能要求均为人工示例，不代表真实招聘。")
    st.info("未接入真实 AI／就业趋势，也未接入经核验的学习课程；本页不提供统计或预测。")
    try:
        data = load_demo()
        labels = data["labels"]
        st.write(f"示例用户：{data['profile']['name']}")
        profile = st.multiselect("选择你具备的技能（修改后自动重新计算）", data["skills"],
                                 default=data["profile"]["skills"], format_func=lambda s: labels[s], key="minimal_skills")
        if not profile:
            st.info("尚未选择技能：三个岗位的技能覆盖率均为 0%。")
        st.write("技能覆盖率＝已具备的岗位要求技能数 ÷ 岗位要求技能总数。每项技能只计一次。")
        st.warning("技能覆盖率不是录用概率。它不衡量熟练程度、经验或其他招聘条件。")
        for result in compare_skills(profile, data):
            with st.container(border=True):
                st.subheader(result["role"])
                st.metric("技能覆盖率", f"{result['coverage']:.1%}")
                st.caption(f"{len(result['covered'])} / {result['required_count']} 项岗位要求技能")
                st.write("已具备：" + ("、".join(labels[s] for s in result["covered"]) or "无"))
                st.write("缺少：" + ("、".join(labels[s] for s in result["missing"]) or "无"))
        st.caption("完整产品待完成：可更新的真实趋势、经核验的学习路线、岗位与技能的 SDG 理由、明确假设的未来情景。旧版实验功能可从侧栏打开，仅供评估。")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        st.error(f"示例资料无法加载或不符合格式：{exc}。请检查 data/demo.json。")
