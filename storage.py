"""Fungsi penyimpanan lokal untuk basis aturan dan riwayat konsultasi."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Any
import csv

BASE_DIR = Path(__file__).resolve().parent
KB_PATH = BASE_DIR / "knowledge_base.json"
HISTORY_PATH = BASE_DIR / "history.csv"


def load_knowledge_base(path: Path = KB_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data.get("rules"), list) or not isinstance(data.get("symptoms"), dict):
        raise ValueError("Format knowledge_base.json tidak valid.")
    return data


def save_knowledge_base(data: dict[str, Any], path: Path = KB_PATH) -> None:
    if not isinstance(data.get("rules"), list) or not isinstance(data.get("symptoms"), dict):
        raise ValueError("Basis pengetahuan harus memiliki rules dan symptoms.")
    sources = data.get("sources", {})
    rule_sources = data.get("rule_sources", {})
    ids = [r.get("id") for r in data["rules"]]
    if len(ids) != len(set(ids)):
        raise ValueError("ID rule tidak boleh duplikat.")
    for rule in data["rules"]:
        if not rule.get("id") or not rule.get("if") or not rule.get("then"):
            raise ValueError("Setiap rule harus memiliki ID, IF, dan THEN.")
        if not 0 <= float(rule.get("cf", -1)) <= 1:
            raise ValueError("CF rule harus berada pada rentang 0 sampai 1.")
        if any(symptom not in data["symptoms"] for symptom in rule["if"]):
            raise ValueError(f"Rule {rule['id']} menggunakan gejala yang tidak terdaftar.")
        source_ids = rule_sources.get(rule["id"], [])
        if not source_ids or any(source_id not in sources for source_id in source_ids):
            raise ValueError(f"Rule {rule['id']} harus memiliki rujukan yang terdaftar.")
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def append_history(record: dict[str, Any], path: Path = HISTORY_PATH) -> None:
    columns = ["timestamp", "phase", "symptoms", "conclusion", "top_nutrient", "confidence", "matched_rules"]
    diagnosis_list = record.get("diagnoses", [])
    top = diagnosis_list[0] if diagnosis_list else {}
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "phase": record.get("phase", ""),
        "symptoms": ";".join(record.get("selected_symptoms", [])),
        "conclusion": record.get("conclusion", ""),
        "top_nutrient": top.get("nutrient", "Belum teridentifikasi"),
        "confidence": top.get("confidence", 0),
        "matched_rules": ";".join(r.get("id", "") for r in record.get("matched_rules", [])),
    }
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
