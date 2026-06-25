from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


DEFAULT_SET = {
    "id": 1,
    "topic": "학교 아이스브레이크 퀴즈",
    "level": "초등학생",
    "isActive": True,
    "createdAt": "2026-06-24",
    "updatedAt": "2026-06-24",
    "quizzes": [
        {"question": "우리 학교의 교목은 무엇일까요?", "answer": "소나무"},
        {"question": "우리 학교의 교화는 무엇일까요?", "answer": "장미"},
        {"question": "교장 선생님 성함은?", "answer": "김정혜 교장선생님"},
        {"question": "이상한 사람들이 많이 가는 곳은?", "answer": "치과"},
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

FINAL_SET = {
    "id": 2,
    "topic": "마무리 퀴즈",
    "level": "초등학생",
    "isActive": False,
    "createdAt": "2026-06-24",
    "updatedAt": "2026-06-24",
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

CHOCOLATIER_SET = {
    "id": 3,
    "topic": "쇼콜라티에 마무리 퀴즈",
    "level": "초등학생",
    "isActive": False,
    "createdAt": "2026-06-25",
    "updatedAt": "2026-06-25",
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

QUIZ_SET_LIST = [DEFAULT_SET, FINAL_SET, CHOCOLATIER_SET]

QUIZ_SETS = {
    "1": DEFAULT_SET,
    "2": FINAL_SET,
    "3": CHOCOLATIER_SET,
    "chocolatier": CHOCOLATIER_SET,
    "choco": CHOCOLATIER_SET,
    "final": FINAL_SET,
}


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/api/quiz-sets/active", "/api/index.py/quiz-sets/active"}:
            self.send_json(DEFAULT_SET)
            return

        if path in {"/api/quiz-sets", "/api/index.py/quiz-sets"}:
            self.send_json(
                [
                    {
                        "id": quiz_set["id"],
                        "topic": quiz_set["topic"],
                        "level": quiz_set["level"],
                        "isActive": quiz_set["isActive"],
                        "createdAt": quiz_set["createdAt"],
                        "updatedAt": quiz_set["updatedAt"],
                        "quizCount": len(quiz_set["quizzes"]),
                    }
                    for quiz_set in QUIZ_SET_LIST
                ]
            )
            return

        if path.startswith("/api/quiz-sets/") or path.startswith("/api/index.py/quiz-sets/"):
            quiz_set_id = path.rsplit("/", 1)[-1]
            quiz_set = QUIZ_SETS.get(quiz_set_id)
            if quiz_set:
                self.send_json(quiz_set)
                return
            self.send_error(404, "Not found")
            return

        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in {"/api/quiz-sets", "/api/index.py/quiz-sets"}:
            self.send_error(404, "Not found")
            return

        payload = self.read_json()
        quizzes = [
            {
                "question": str(item.get("question", "")).strip(),
                "answer": str(item.get("answer", "")).strip(),
            }
            for item in payload.get("quizzes", [])
            if isinstance(item, dict)
        ]
        quizzes = [quiz for quiz in quizzes if quiz["question"] and quiz["answer"]]
        if not quizzes:
            self.send_json({"error": "at least one quiz is required"}, status=400)
            return

        self.send_json(
            {
                "id": "browser-session",
                "topic": str(payload.get("topic") or "직접 편집").strip(),
                "level": str(payload.get("level") or "초등학생").strip(),
                "isActive": True,
                "createdAt": "browser-session",
                "updatedAt": "browser-session",
                "quizzes": quizzes,
            },
            status=201,
        )

    def read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(raw_body or "{}")
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
