# apps/analyzer/formulas.py


def calculate_channel_metrics(posts_data: list, subscribers: int, price: float):
    """
    Рассчитывает агрегированные метрики (ER, CPV, CPM) на основе данных
    по всем постам за период, количества подписчиков и заданной цены.
    """
    if not posts_data:
        return {
            "avg_views": 0,
            "avg_reactions": 0,
            "total_views": 0,
            "total_reactions": 0,
            "er_percent": 0.0,
            "cpv": 0.0,
            "cpm": 0.0,
        }

    posts_count = len(posts_data)
    total_views = sum(p["views"] for p in posts_data)
    total_reactions = sum(p["reactions"] for p in posts_data)

    avg_views = total_views / posts_count if posts_count > 0 else 0
    avg_reactions = total_reactions / posts_count if posts_count > 0 else 0

    # ER = (Среднее число реакций на пост / Подписчики) * 100%
    er_percent = (avg_reactions / subscribers) * 100 if subscribers > 0 else 0.0

    # CPV = Цена / Среднее число просмотров на пост
    cpv = price / avg_views if avg_views > 0 else 0.0

    # CPM = (Цена / Среднее число просмотров на пост) * 1000
    cpm = cpv * 1000 if avg_views > 0 else 0.0

    return {
        "avg_views": round(avg_views),
        "avg_reactions": round(avg_reactions, 1),
        "total_views": total_views,
        "total_reactions": total_reactions,
        "er_percent": round(er_percent, 2),
        "cpv": round(cpv, 4),
        "cpm": round(cpm, 2),
    }
