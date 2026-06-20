"""Ball va daraja hisoblash logikasi (PHASE 6)."""

# Seksiya maksimal ballari (TASK PHASE 6)
SECTION_MAX = {
    "grammar": 20,
    "reading": 6,
    "listening": 6,
    "writing": 10,
    "speaking": 10,
}
TOTAL_MAX = sum(SECTION_MAX.values())  # 52


def percentage_to_level(percentage: float) -> str:
    """Foizni CEFR darajasiga aylantirish."""
    p = percentage
    if p < 20:
        return "A1"
    if p < 40:
        return "A2"
    if p < 60:
        return "B1"
    if p < 75:
        return "B2"
    if p < 90:
        return "C1"
    return "C2"


def pct(score: float, maximum: float) -> float:
    """Foiz hisoblash (0 ga bo'lishdan himoyalangan)."""
    if not maximum:
        return 0.0
    return round(score / maximum * 100, 1)


def total_percentage(section_pcts: list[float]) -> float:
    """Umumiy foiz = seksiya foizlarining o'rtachasi (TASK PHASE 3.8)."""
    if not section_pcts:
        return 0.0
    return round(sum(section_pcts) / len(section_pcts), 1)
