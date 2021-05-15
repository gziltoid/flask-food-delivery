from babel import dates
from food_delivery import app


@app.template_filter("date_format_ru")
def date_format_ru(date):
    return dates.format_datetime(date, "dd MMMM YYYY", locale="ru_RU")
