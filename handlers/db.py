import os
import threading
from psycopg import connect
from psycopg import errors
from psycopg.rows import dict_row


_db_lock = threading.Lock()
_db_ready = False


def _database_url():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("Variável DATABASE_URL não definida")

    return database_url


def inicializar_banco():
    global _db_ready

    if _db_ready:
        return

    with _db_lock:
        if _db_ready:
            return

        with connect(_database_url()) as conexao:
            with conexao.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS gastos (
                            id BIGSERIAL PRIMARY KEY,
                            chat_id BIGINT NOT NULL,
                            valor NUMERIC(12,2) NOT NULL,
                            categoria TEXT NOT NULL,
                            data DATE NOT NULL,
                            criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    conexao.commit()
                except errors.UniqueViolation:
                    conexao.rollback()

            with conexao.cursor() as cursor:
                cursor.execute("SELECT to_regclass('public.gastos')")
                tabela = cursor.fetchone()

            if not tabela or not tabela[0]:
                raise RuntimeError("Tabela gastos não está disponível")

        _db_ready = True


def inserir_gasto(chat_id: int, valor: float, categoria: str, data: str):
    with connect(_database_url()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO gastos (chat_id, valor, categoria, data)
                VALUES (%s, %s, %s, %s)
                """,
                (chat_id, valor, categoria, data),
            )
        conexao.commit()


def listar_gastos_mes(chat_id: int, ano: int, mes: int):
    with connect(_database_url(), row_factory=dict_row) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, valor, categoria, TO_CHAR(data, 'DD/MM/YYYY') AS data
                FROM gastos
                WHERE chat_id = %s
                  AND EXTRACT(YEAR FROM data) = %s
                  AND EXTRACT(MONTH FROM data) = %s
                ORDER BY data ASC, id ASC
                """,
                (chat_id, ano, mes),
            )
            return cursor.fetchall()


def obter_ultimo_gasto_mes(chat_id: int, ano: int, mes: int):
    with connect(_database_url(), row_factory=dict_row) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, valor, categoria, TO_CHAR(data, 'DD/MM/YYYY') AS data
                FROM gastos
                WHERE chat_id = %s
                  AND EXTRACT(YEAR FROM data) = %s
                  AND EXTRACT(MONTH FROM data) = %s
                ORDER BY data DESC, id DESC
                LIMIT 1
                """,
                (chat_id, ano, mes),
            )
            return cursor.fetchone()


def excluir_ultimo_gasto_mes(chat_id: int, ano: int, mes: int):
    with connect(_database_url(), row_factory=dict_row) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM gastos
                WHERE id = (
                    SELECT id
                    FROM gastos
                    WHERE chat_id = %s
                      AND EXTRACT(YEAR FROM data) = %s
                      AND EXTRACT(MONTH FROM data) = %s
                    ORDER BY data DESC, id DESC
                    LIMIT 1
                )
                RETURNING id, valor, categoria, TO_CHAR(data, 'DD/MM/YYYY') AS data
                """,
                (chat_id, ano, mes),
            )
            registro = cursor.fetchone()
        conexao.commit()
        return registro