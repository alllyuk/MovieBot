"""Bot response message templates."""


class Messages:
    """All bot response templates."""

    WELCOME = """👋 Привет! Я помогу вам выбирать фильмы на вечер.

Как это работает:
1. Добавляйте фильмы: «хочу посмотреть [название]»
2. Когда захотите спросите: «что смотрим?»
3. После просмотра: «посмотрели [название], [оценка]/10»"""

    HELP = """📖 Команды:

• «хочу посмотреть [название]» — добавить фильм
• «мой список» — твои фильмы
• «наш список» — фильмы которые хотите оба
• «что смотрим?» — выбрать фильм на вечер
• «посмотрели [название], [оценка]» — отметить просмотр
• «история» — что смотрели за год
• «удали [название]» — убрать из списка"""

    UNKNOWN_COMMAND = "🤔 Не понял. Напиши /help чтобы увидеть доступные команды"
    EMPTY_MOVIE_NAME = "🎬 Какой фильм добавить? Напиши «хочу посмотреть [название]»"
    EMPTY_WISHLIST = "📋 Твой список пуст. Напиши «хочу посмотреть [название]» чтобы добавить фильм"
    EMPTY_INTERSECTION = "💑 Пока нет фильмов которые хотите оба"
    ALL_LISTS_EMPTY = "😅 Списки пусты! Добавьте фильмы командой «хочу посмотреть [название]»"
    EMPTY_HISTORY = "📚 История пуста. Самое время что-нибудь посмотреть! 🍿"
    ASK_RATING = "Как вам фильм? Оцените от 1 до 10"
    INVALID_RATING = "🤔 Оценка должна быть от 1 до 10"

    @staticmethod
    def movie_added(title: str) -> str:
        return f"✅ Добавил «{title}» в твой список"

    @staticmethod
    def movie_already_exists(title: str) -> str:
        return f"ℹ️ «{title}» уже есть в твоём списке"

    @staticmethod
    def movie_deleted(title: str) -> str:
        return f"🗑 Удалил «{title}» из твоего списка"

    @staticmethod
    def movie_not_found(title: str) -> str:
        return f"🤷 «{title}» нет в твоём списке"

    @staticmethod
    def movie_not_in_wishlist(title: str) -> str:
        return f"ℹ️ Фильма «{title}» нет в твоём списке"

    @staticmethod
    def format_my_list(movies: list[str]) -> str:
        if not movies:
            return Messages.EMPTY_WISHLIST
        lines = ["📋 Твой список:"]
        for i, movie in enumerate(movies, 1):
            lines.append(f"{i}. {movie}")
        return "\n".join(lines)

    @staticmethod
    def format_our_list(movies: list[str]) -> str:
        if not movies:
            return Messages.EMPTY_INTERSECTION
        lines = ["💑 Фильмы которые хотите оба:"]
        for i, movie in enumerate(movies, 1):
            lines.append(f"{i}. {movie}")
        return "\n".join(lines)

    @staticmethod
    def movie_selected_intersection(title: str) -> str:
        return f"🎬 Вы оба хотите посмотреть «{title}»! Отличный выбор на вечер"

    @staticmethod
    def movie_selected_random(title: str) -> str:
        return f"🎲 Пересечений нет, выбираю случайный: «{title}»"

    @staticmethod
    def movie_selected_from_other(title: str, other_name: str) -> str:
        return f"🎲 У {other_name} список пуст, выбираю из списка {other_name}: «{title}»"

    @staticmethod
    def movie_watched(title: str, rating: int) -> str:
        return f"✅ Отлично! «{title}» в архиве с оценкой {rating}/10"

    @staticmethod
    def movie_added_to_history(title: str, rating: int) -> str:
        return f"✅ Добавил «{title}» в архив с оценкой {rating}/10"
