from __future__ import annotations

import json
import mimetypes
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "quizzes.db"
HOST = "127.0.0.1"
PORT = 8000


DEFAULT_STATE = {
    "topic": "학교 아이스브레이크 퀴즈",
    "level": "초등학생",
    "quizzes": [
        {
            "question": "우리 학교의 교목은 무엇일까요?",
            "answer": "소나무",
        },
        {
            "question": "우리 학교의 교화는 무엇일까요?",
            "answer": "장미",
        },
        {
            "question": "교장 선생님 성함은?",
            "answer": "김정혜 교장선생님",
        },
        {
            "question": "이상한 사람들이 많이 가는 곳은?",
            "answer": "치과",
        },
        {
            "question": "스스로 바닥을 돌아다니며 먼지를 빨아들이고 청소를 도와주는 기계는 무엇일까요?",
            "answer": "로봇 청소기",
        },
        {
            "question": "인간과 비슷한 형태를 가지고 걷기도 하고 말도 하며, 어떤 작업이나 조작을 자동으로 하는 기계 장치는 무엇일까요?",
            "answer": "로봇(Robot)",
        },
    ],
}

FINAL_STATE = {
    "topic": "마무리 퀴즈",
    "level": "초등학생",
    "quizzes": [
        {
            "question": "로봇(Robot)의 어원은 '일한다', '노예'라는 뜻을 가진 체코어 (                           ) 에서 나온 말이다.",
            "answer": "로보타(robota)",
            "answerHtml": "로봇(Robot)의 어원은 '일한다', '노예'라는 뜻을 가진 체코어 (<span class=\"answer-highlight\">로보타(robota)</span>) 에서 나온 말이다.",
        },
        {
            "question": "(     )는 크고 작은 부품과 장치들을 연구·개발하고 하나의 로봇으로 조립하여 만드는 일을 합니다.",
            "answer": "로봇공학자",
            "answerHtml": "<span class=\"answer-highlight\">로봇공학자</span>는 크고 작은 부품과 장치들을 연구·개발하고 하나의 로봇으로 조립하여 만드는 일을 합니다.",
        },
        {
            "question": "로봇의 부품중 사람의 눈, 귀와 같이 외부의 정보를 감지하여 전달하는 것은?\n\n1. 구동장치\n2. 센서장치\n3. 전원장치\n4. 제어장치",
            "answer": "2번 센서장치",
        },
        {
            "question": "새로 생겨나는 로봇관련 직업이 아닌 것은?\n\n1. 실버로봇 서비스 기획자\n2. 로봇 윤리학자\n3. 로봇 감성인지 연구원\n4. 웨어러블 전문가\n5. 수동주행 자동차 개발자",
            "answer": "5번 수동주행 자동차 개발자",
        },
    ],
}

CHOCOLATIER_STATE = {
    "topic": "쇼콜라티에 마무리 퀴즈",
    "level": "초등학생",
    "quizzes": [
        {
            "question": "초콜릿을 혼합하고 장식해 세상에 하나뿐인 아름다운 예술작품을 만드는 '초콜릿 장인'을 부르는 멋진 이름은?\n\n1. 파티셰\n2. 쇼콜라티에\n3. 바리스타\n4. 조향사",
            "answer": "2번 쇼콜라티에",
            "answerHtml": "<span class=\"answer-highlight\">2번 쇼콜라티에</span>",
        },
        {
            "question": "(O/X 퀴즈) 초콜릿을 딱 맞는 온도로 조절해서 안정적인 결정으로 굳혀 윤기가 나게 만드는 마법 같은 작업의 이름은 '템퍼링'이다?",
            "answer": "O (맞습니다!)",
            "answerHtml": "<span class=\"answer-highlight\">O</span> (맞습니다!)",
        },
        {
            "question": "(단답형) 따뜻한 초콜릿은 차가운 책상에 올려두면 금방 '{??}' 버립니다. 그래서 재빨리 스프링클로 꾸며주어야 해요!",
            "answer": "굳어",
            "answerHtml": "따뜻한 초콜릿은 차가운 책상에 올려두면 금방 '<span class=\"answer-highlight\">굳어</span>' 버립니다.",
        },
        {
            "question": "(O/X 퀴즈) 훌륭한 쇼콜라티에가 되기 위해서는 작고 세밀한 것을 다루는 '정교함'과 오래 서서 일하는 '강한 체력과 인내심'이 필요하다?",
            "answer": "O (맞습니다!)",
            "answerHtml": "<span class=\"answer-highlight\">O</span> (맞습니다!)",
        },
    ],
}

BUILT_IN_SETS = [DEFAULT_STATE, FINAL_STATE, CHOCOLATIER_STATE]


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def normalize_level(level: object) -> str:
    value = str(level or "초등학생").strip()
    if value == "초등 고학년":
        return "초등학생"
    return value


def init_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS quiz_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                level TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_set_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                FOREIGN KEY (quiz_set_id) REFERENCES quiz_sets(id) ON DELETE CASCADE
            );
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM quiz_sets").fetchone()[0]
        ensure_answer_html_column(connection)
        connection.execute(
            "UPDATE quiz_sets SET level = '초등학생' WHERE level = '초등 고학년'"
        )
        if count == 0:
            create_quiz_set(connection, DEFAULT_STATE, is_active=True)
        seed_missing_built_in_sets(connection)


def ensure_answer_html_column(connection: sqlite3.Connection) -> None:
    columns = connection.execute("PRAGMA table_info(quizzes)").fetchall()
    if not any(column["name"] == "answer_html" for column in columns):
        connection.execute("ALTER TABLE quizzes ADD COLUMN answer_html TEXT DEFAULT ''")


def seed_missing_built_in_sets(connection: sqlite3.Connection) -> None:
    for payload in BUILT_IN_SETS:
        existing = connection.execute(
            "SELECT id FROM quiz_sets WHERE topic = ? LIMIT 1",
            (payload["topic"],),
        ).fetchone()
        if not existing:
            create_quiz_set(connection, payload, is_active=False)


def create_quiz_set(connection: sqlite3.Connection, payload: dict, is_active: bool) -> dict:
    topic = str(payload.get("topic") or "직접 편집").strip()
    level = normalize_level(payload.get("level"))
    quizzes = validate_quizzes(payload.get("quizzes"))

    if is_active:
        connection.execute("UPDATE quiz_sets SET is_active = 0")

    cursor = connection.execute(
        """
        INSERT INTO quiz_sets (topic, level, is_active, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (topic, level, 1 if is_active else 0),
    )
    quiz_set_id = cursor.lastrowid

    connection.executemany(
        """
        INSERT INTO quizzes (quiz_set_id, question, answer, answer_html, sort_order)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (quiz_set_id, quiz["question"], quiz["answer"], quiz.get("answerHtml", ""), index)
            for index, quiz in enumerate(quizzes, start=1)
        ],
    )
    connection.commit()
    return get_quiz_set(connection, quiz_set_id)


def validate_quizzes(raw_quizzes: object) -> list[dict]:
    if not isinstance(raw_quizzes, list):
        raise ValueError("quizzes must be a list")

    quizzes = []
    for item in raw_quizzes:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or "").strip()
        answer = str(item.get("answer") or "").strip()
        if question and answer:
            quizzes.append({
                "question": question,
                "answer": answer,
                "answerHtml": str(item.get("answerHtml") or "").strip(),
            })

    if not quizzes:
        raise ValueError("at least one quiz is required")

    return quizzes


def list_quiz_sets(connection: sqlite3.Connection) -> list[dict]:
    rows = connection.execute(
        """
        SELECT qs.id, qs.topic, qs.level, qs.is_active, qs.created_at, qs.updated_at,
               COUNT(q.id) AS quiz_count
        FROM quiz_sets qs
        LEFT JOIN quizzes q ON q.quiz_set_id = qs.id
        GROUP BY qs.id
        ORDER BY qs.updated_at DESC, qs.id DESC
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "topic": row["topic"],
            "level": row["level"],
            "isActive": bool(row["is_active"]),
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "quizCount": row["quiz_count"],
        }
        for row in rows
    ]


def get_active_quiz_set(connection: sqlite3.Connection) -> dict:
    row = connection.execute(
        "SELECT id FROM quiz_sets WHERE is_active = 1 ORDER BY updated_at DESC, id DESC LIMIT 1"
    ).fetchone()
    if row:
        return get_quiz_set(connection, row["id"])

    first_row = connection.execute("SELECT id FROM quiz_sets ORDER BY id LIMIT 1").fetchone()
    if first_row:
        return get_quiz_set(connection, first_row["id"])

    return create_quiz_set(connection, DEFAULT_STATE, is_active=True)


def get_quiz_set_by_ref(connection: sqlite3.Connection, quiz_set_ref: str) -> dict:
    topic_by_slug = {
        "chocolatier": "쇼콜라티에 마무리 퀴즈",
        "choco": "쇼콜라티에 마무리 퀴즈",
        "final": "마무리 퀴즈",
    }
    if quiz_set_ref in topic_by_slug:
        row = connection.execute(
            "SELECT id FROM quiz_sets WHERE topic = ? ORDER BY id DESC LIMIT 1",
            (topic_by_slug[quiz_set_ref],),
        ).fetchone()
        if not row:
            raise KeyError("quiz set not found")
        return get_quiz_set(connection, row["id"])

    return get_quiz_set(connection, int(quiz_set_ref))


def get_quiz_set(connection: sqlite3.Connection, quiz_set_id: int) -> dict:
    quiz_set = connection.execute("SELECT * FROM quiz_sets WHERE id = ?", (quiz_set_id,)).fetchone()
    if not quiz_set:
        raise KeyError("quiz set not found")

    quiz_rows = connection.execute(
        """
        SELECT question, answer, answer_html
        FROM quizzes
        WHERE quiz_set_id = ?
        ORDER BY sort_order ASC, id ASC
        """,
        (quiz_set_id,),
    ).fetchall()
    return {
        "id": quiz_set["id"],
        "topic": quiz_set["topic"],
        "level": quiz_set["level"],
        "isActive": bool(quiz_set["is_active"]),
        "createdAt": quiz_set["created_at"],
        "updatedAt": quiz_set["updated_at"],
        "quizzes": [
            {"question": row["question"], "answer": row["answer"], "answerHtml": row["answer_html"] or ""}
            for row in quiz_rows
        ],
    }


class QuizRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        parsed_path = urlparse(path).path
        if parsed_path == "/":
            parsed_path = "/index.html"
        return str((ROOT_DIR / parsed_path.lstrip("/")).resolve())

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path).path
        try:
            if parsed_path == "/api/quiz-sets":
                with get_connection() as connection:
                    self.send_json(list_quiz_sets(connection))
                return
            if parsed_path == "/api/quiz-sets/active":
                with get_connection() as connection:
                    self.send_json(get_active_quiz_set(connection))
                return
            if parsed_path.startswith("/api/quiz-sets/"):
                quiz_set_ref = parsed_path.rsplit("/", 1)[-1]
                with get_connection() as connection:
                    self.send_json(get_quiz_set_by_ref(connection, quiz_set_ref))
                return
            super().do_GET()
        except (KeyError, ValueError):
            self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path).path
        try:
            if parsed_path == "/api/quiz-sets":
                payload = self.read_json()
                with get_connection() as connection:
                    quiz_set = create_quiz_set(connection, payload, bool(payload.get("isActive", True)))
                self.send_json(quiz_set, status=201)
                return
            self.send_error(404, "Not found")
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)

    def read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(raw_body or "{}")
        if not isinstance(payload, dict):
            raise ValueError("request body must be an object")
        return payload

    def send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def guess_type(self, path: str) -> str:
        if path.endswith(".js"):
            return "text/javascript"
        return mimetypes.guess_type(path)[0] or "application/octet-stream"


def main() -> None:
    init_database()
    server = ThreadingHTTPServer((HOST, PORT), QuizRequestHandler)
    print(f"You쌤 퀴즈 보드 실행 중: http://{HOST}:{PORT}")
    print(f"SQLite DB 위치: {DB_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    main()
