"""History service for watch history operations."""

from dataclasses import dataclass
from datetime import date
from collections import defaultdict
from src.database.repositories import HistoryRepository, HistoryItem


@dataclass
class MonthHistory:
    month_name: str  # e.g., "Январь 2024"
    movies: list[HistoryItem]


@dataclass
class HistoryResult:
    months: list[MonthHistory]
    total_count: int
    average_rating: float
    is_empty: bool


# Russian month names
MONTH_NAMES = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

SHORT_MONTH_NAMES = {
    1: "янв",
    2: "фев",
    3: "мар",
    4: "апр",
    5: "мая",
    6: "июн",
    7: "июл",
    8: "авг",
    9: "сен",
    10: "окт",
    11: "ноя",
    12: "дек",
}


class HistoryService:
    """Business logic for history operations."""

    def __init__(self, history_repo: HistoryRepository):
        self.history_repo = history_repo

    def get_history(self) -> HistoryResult:
        """Get formatted watch history."""
        items = self.history_repo.get_all()

        if not items:
            return HistoryResult(months=[], total_count=0, average_rating=0.0, is_empty=True)

        # Group by month
        by_month: dict[tuple[int, int], list[HistoryItem]] = defaultdict(list)
        for item in items:
            key = (item.watched_at.year, item.watched_at.month)
            by_month[key].append(item)

        # Sort months descending
        sorted_keys = sorted(by_month.keys(), reverse=True)

        months = []
        for year, month in sorted_keys:
            month_name = f"{MONTH_NAMES[month]} {year}"
            months.append(MonthHistory(month_name=month_name, movies=by_month[(year, month)]))

        # Calculate stats
        total_count = len(items)
        average_rating = sum(item.rating for item in items) / total_count

        return HistoryResult(
            months=months,
            total_count=total_count,
            average_rating=round(average_rating, 1),
            is_empty=False,
        )

    @staticmethod
    def format_date(d: date) -> str:
        """Format date as '12 янв'."""
        return f"{d.day} {SHORT_MONTH_NAMES[d.month]}"
