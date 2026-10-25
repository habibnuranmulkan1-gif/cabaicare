"""Mesin inferensi sistem pakar pemupukan cabai berbasis forward chaining."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


def combine_cf(values: list[float]) -> float:
    """Gabungkan beberapa CF positif untuk hipotesis yang sama."""
    result = 0.0
    for value in values:
        value = max(0.0, min(1.0, float(value)))
        result = result + value * (1.0 - result)
    return round(result, 4)


@dataclass
class Diagnosis:
    code: str
    nutrient: str
    confidence: float
    recommendation: str
    matched_rules: list[dict[str, Any]]


class ExpertSystem:
    """Sistem pakar sederhana dengan basis aturan dan memori kerja."""

    def __init__(
        self,
        rules: list[dict[str, Any]],
        symptoms: dict[str, dict[str, str]],
        phase_guidance: Optional[dict[str, dict[str, str]]] = None,
        rule_sources: Optional[dict[str, list[str]]] = None,
    ):
        self.rules = rules
        self.symptoms = symptoms
        self.phase_guidance = phase_guidance or {}
        self.rule_sources = rule_sources or {}
        self.working_memory: set[str] = set()
        self.reasoning_trace: list[str] = []

    def diagnose(self, selected_symptoms: list[str], user_cf: float, phase: str) -> dict[str, Any]:
        """Menjalankan forward chaining berdasarkan gejala yang dipilih pengguna."""
        self.working_memory = set(selected_symptoms)
        self.reasoning_trace = [
            f"Fakta awal: {', '.join(selected_symptoms) if selected_symptoms else 'tidak ada gejala dipilih'}.",
            f"Fase tanaman: {phase}.",
        ]
        phase_advice = self.phase_guidance.get(phase, {})
        phase_note = phase_advice.get(
            "guidance",
            "Pada fase vegetatif, perhatikan pertumbuhan daun dan batang."
            if phase == "Vegetatif" else
            "Pada fase generatif, perhatikan pembungaan dan pembentukan buah.",
        )
        source_id = phase_advice.get("source_id")
        self.reasoning_trace.append(
            f"Panduan fase diterapkan{f' berdasarkan {source_id}' if source_id else ''}: {phase_note}"
        )
        matched: list[dict[str, Any]] = []

        for rule in self.rules:
            antecedents = set(rule.get("if", []))
            if antecedents and antecedents.issubset(self.working_memory):
                effective_cf = round(float(rule.get("cf", 0.5)) * float(user_cf), 4)
                source_ids = self.rule_sources.get(rule["id"], [])
                item = {**rule, "effective_cf": effective_cf, "source_ids": source_ids}
                matched.append(item)
                self.reasoning_trace.append(
                    f"{rule['id']} cocok karena semua gejala IF ditemukan; "
                    f"rujukan: {', '.join(source_ids) if source_ids else 'belum dipetakan'}; "
                    f"CF aturan {float(rule.get('cf', 0.5)):.2f} × CF pengguna {user_cf:.2f} = {effective_cf:.2f}."
                )
                self.working_memory.add(rule["then"])

        by_hypothesis: dict[str, list[dict[str, Any]]] = {}
        for item in matched:
            by_hypothesis.setdefault(item["then"], []).append(item)

        diagnoses: list[Diagnosis] = []
        for code, items in by_hypothesis.items():
            confidence = combine_cf([item["effective_cf"] for item in items])
            best = max(items, key=lambda item: item["effective_cf"])
            diagnoses.append(Diagnosis(
                code=code,
                nutrient=best["nutrient"],
                confidence=confidence,
                recommendation=best["recommendation"],
                matched_rules=items,
            ))

        diagnoses.sort(key=lambda d: d.confidence, reverse=True)
        self.reasoning_trace.append(
            f"Inferensi selesai: {len(matched)} aturan cocok dan {len(diagnoses)} hipotesis dihasilkan."
        )

        if not diagnoses:
            conclusion = "Belum ada diagnosis yang cukup didukung oleh aturan pada basis pengetahuan."
            recommendation = (
                "Periksa kembali gejala, kelembapan dan drainase, serta kemungkinan hama atau penyakit. "
                "Pertimbangkan uji tanah atau konsultasi dengan penyuluh pertanian sebelum menambah pupuk. "
                f"{phase_note}"
            )
        else:
            top = diagnoses[0]
            conclusion = f"Gejala paling sesuai dengan kemungkinan masalah unsur hara: {top.nutrient}."
            recommendation = f"{top.recommendation} {phase_note}"

        return {
            "conclusion": conclusion,
            "recommendation": recommendation,
            "diagnoses": [d.__dict__ for d in diagnoses],
            "trace": list(self.reasoning_trace),
            "matched_rules": matched,
            "facts": sorted(self.working_memory),
            "phase": phase,
            "user_cf": float(user_cf),
        }
