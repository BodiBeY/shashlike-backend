from fastapi import FastAPI, Query
import psycopg2

app = FastAPI()

# Твоя лінка до Supabase
DATABASE_URL = "postgresql://postgres.pnwavouezfkinuktyiuh:ax._dD*-5$ZuPB@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"


@app.get("/get_stat")
def get_user_stat(username: str = Query(...)):
    # Прибираємо значок @, якщо адмін ввів юзернейм з ним
    clean_username = username.replace("@", "").strip()

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # SQL-запит: шукаємо стажера за юзернеймом
        # УВАГА: Перевір, чи колонки з балами та статусом у тебе в Supabase
        # називаються саме 'scores' і 'status'. Якщо інакше — впиши свої назви!
        query = "SELECT username, scores, status FROM users WHERE username = %s;"
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
