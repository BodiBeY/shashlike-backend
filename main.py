from fastapi import FastAPI, Query
import psycopg2

app = FastAPI()

# Твоя лінка до Supabase
DATABASE_URL = "postgresql://postgres.pnwavouezfkinuktyiuh:ax._dD)*-5$ZuPB@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"


@app.get("/get_stat")
def get_user_stat(username: str = Query(...)):
    # Прибираємо значок @, якщо адмін ввів юзернейм з ним
    clean_username = username.replace("@", "").strip()

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # SQL-запит: шукаємо стажера і беремо дані з двох таблиць
        query = """
            SELECT u.username, tr.score, tr.status 
            FROM users u
            LEFT JOIN test_results tr ON u.id = tr.user_id
            WHERE u.username = %s
            ORDER BY tr.finished_at DESC
            LIMIT 1;
        """
        cursor.execute(query, (clean_username,))
        user_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if user_data:
            # Якщо юзера знайшли — віддаємо SendPulse його дані в JSON
            return {
                "found": True,
                "username": user_data[0],
                "scores": str(user_data[1]) if user_data[1] is not None else "0",
                "status": user_data[2] if user_data[2] is not None else "Навчається"
            }
        else:
            # Якщо не знайшли
            return {
                "found": False,
                "scores": "0",
                "status": "Немає в базі"
            }

    except Exception as e:
        return {"found": False, "error": str(e)}


# Ендпоінт для отримання списку всіх тестів
@app.get("/get_quizzes")
def get_all_quizzes():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM quizzes;")
    quizzes = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"quizzes": [{"id": q[0], "title": q[1]} for q in quizzes]}

# Ендпоінт для отримання статистики по конкретному тесту
@app.get("/get_stat_by_quiz")
def get_stat_by_quiz(username: str, quiz_id: int):
    clean_username = username.replace("@", "").strip()
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Додаємо tr.quiz_id у SELECT
    query = """
        SELECT tr.score, tr.status, tr.quiz_id 
        FROM test_results tr
        JOIN users u ON u.id = tr.user_id
        WHERE u.username = %s AND tr.quiz_id = %s
        ORDER BY tr.finished_at DESC LIMIT 1;
    """
    cursor.execute(query, (clean_username, quiz_id))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result:
        # Тепер повертаємо і quiz_id
        return {
            "found": True, 
            "score": result[0], 
            "status": result[1], 
            "quiz_id": result[2]
        }
    return {"found": False, "score": 0, "status": "Немає даних", "quiz_id": quiz_id}


from pydantic import BaseModel

# Модель даних для прийняття результату
class TestResult(BaseModel):
    username: str
    quiz_id: int
    score: int
    status: str

@app.post("/save_result")
def save_result(data: TestResult):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 1. Знаходимо ID юзера за його username
    cursor.execute("SELECT id FROM users WHERE username = %s;", (data.username,))
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        # 2. Вставляємо результат у таблицю
        query = """
            INSERT INTO test_results (user_id, quiz_id, score, status, finished_at)
            VALUES (%s, %s, %s, %s, NOW());
        """
        cursor.execute(query, (user_id, data.quiz_id, data.score, data.status))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Результат збережено"}
    
    cursor.close()
    conn.close()
    return {"message": "Юзера не знайдено"}

@app.get("/get_quizzes_by_dept")
def get_quizzes_by_dept(dept_id: int):
    # Визначаємо змінну ПЕРЕД тим, як її повернути
    list_of_quizzes = [{"id": 1, "name": "Тест 1"}, {"id": 2, "name": "Тест 2"}]
    return list_of_quizzes
