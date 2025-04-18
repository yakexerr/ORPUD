from django.http import HttpResponse
import uuid
from django.db import connection # как я понял, чтоб брать из подключения к бд список запросов


def print_queries(queries):
    tag = uuid.uuid4()
    print(f"[{tag}] SQL PROFILER")
    total_time = 0.0
    total_queries = 0
    for counter, query in enumerate(queries, start=1):
        # здесь берём запрос, как-то форматируем и вроде сколько времени потрачено на запрос
        nice_sql = query["sql"].replace('"', "").replace(",", ", ")
        sql = "\033[1;31m[%s]\033[0m %s" % (query["time"], nice_sql)
        total_time = total_time + float(query["time"])

        # if counter <= 20:
        print(f"[{tag}] {sql}\n")
        total_queries = counter
    # общее время потраченное и кол-во запросов
    print(f"[{tag}] \033[1;32m[" f"TOTAL TIME: {total_time} seconds, QUERIES: {total_queries}" f"]\033[0m")



class SqlPrintingMiddleware(object): # импорт, чтобы выводить по типу return HttpResponse("NO!!!!!")
    """
    Middleware which prints out a list of all SQL queries done
    for each view that is processed.  This is only useful for debugging.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    # как я понял, то при помощи этого мы можем выводить sql-запросы и прочее (вот например принты) в консоль
    # то есть можем вернуть свой ответ при каком-то условии
    def __call__(self, request):
        response = self.get_response(request)
        # тут мы смотрим если в бд запросы, если есть то выполняет
        if len(connection.queries) > 0:
            print_queries(connection.queries)
        return response
