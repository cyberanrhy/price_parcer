class OneCProvider:
    def __init__(self, conn_string, login, password):
        self.conn_string = conn_string
        self.login = login
        self.password = password
        self._connection = None

    def _connect(self):
        if self._connection is not None:
            try:
                self._connection.ДанныеСтроки("SELECT 1")
                return self._connection
            except Exception:
                self._connection = None
        try:
            import win32com.client
            connector = win32com.client.Dispatch("V83.COMConnector")
            conn_str = f"File='{self.conn_string}';Usr='{self.login}';Pwd='{self.password}';"
            self._connection = connector.Connect(conn_str)
            return self._connection
        except Exception as e:
            self._connection = None
            raise Exception(f"Ошибка подключения к 1С: {e}")

    def get_price(self, article):
        try:
            connection = self._connect()
            query = """
            ВЫБРАТЬ
                Номенклатура.Артикул,
                Номенклатура.НаименованиеПолное КАК Наименование,
                ЦеныНоменклатуры.Цена КАК Цена
            ИЗ
                Справочник.Номенклатура КАК Номенклатура
                    ВНУТРЕННЕЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры КАК ЦеныНоменклатуры
                    ПО Номенклатура.Ссылка = ЦеныНоменклатуры.Номенклатура
            ГДЕ
                Номенклатура.Артикул = &Артикул
            """
            result = connection.Execute(query, {"Артикул": article})
            row = result.Выбрать()
            if row.Следующий():
                return {
                    "price": row.Цена,
                    "name": row.Наименование or "",
                    "article": article
                }
            return None
        except Exception as e:
            raise Exception(f"Ошибка запроса к 1С: {e}")

    def check_connection(self):
        try:
            conn = self._connect()
            return True, "Подключение к 1С установлено"
        except Exception as e:
            return False, str(e)
