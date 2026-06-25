const STORAGE_KEY = "youssam-quiz-board-v1";
const ADMIN_PASSWORD = "youssam";
const API_BASE = "/api";
const QUIZ_TITLES = {
  "학교 아이스브레이크 퀴즈": "수업 전 두뇌 깨우기 퀴즈",
  "마무리 퀴즈": "오늘 배운 로봇 마무리 퀴즈",
  "쇼콜라티에 마무리 퀴즈": "달콤한 쇼콜라티에 마무리 퀴즈",
};

const defaultState = {
  level: "초등학생",
  topic: "학교 아이스브레이크 퀴즈",
  quizzes: [
    {
      question: "우리 학교의 교목은 무엇일까요?",
      answer: "소나무",
    },
    {
      question: "우리 학교의 교화는 무엇일까요?",
      answer: "장미",
    },
    {
      question: "교장 선생님 성함은?",
      answer: "김정혜 교장선생님",
    },
    {
      question: "이상한 사람들이 많이 가는 곳은?",
      answer: "치과",
    },
    {
      question: "스스로 바닥을 돌아다니며 먼지를 빨아들이고 청소를 도와주는 기계는 무엇일까요?",
      answer: "로봇 청소기",
    },
    {
      question: "인간과 비슷한 형태를 가지고 걷기도 하고 말도 하며, 어떤 작업이나 조작을 자동으로 하는 기계 장치는 무엇일까요?",
      answer: "로봇(Robot)",
    },
  ],
};

const quizCount = document.querySelector("#quizCount");
const pageTitle = document.querySelector("#pageTitle");
const quizCard = document.querySelector("#quizCard");
const quizQuestion = document.querySelector("#quizQuestion");
const quizAnswer = document.querySelector("#quizAnswer");
const prevButton = document.querySelector("#prevButton");
const nextButton = document.querySelector("#nextButton");
const showButton = document.querySelector("#showButton");
const adminPanel = document.querySelector("#adminPanel");
const adminOpenButton = document.querySelector("#adminOpenButton");
const adminCloseButton = document.querySelector("#adminCloseButton");
const loginForm = document.querySelector("#loginForm");
const passwordInput = document.querySelector("#passwordInput");
const editorArea = document.querySelector("#editorArea");
const topicInput = document.querySelector("#topicInput");
const levelInput = document.querySelector("#levelInput");
const countInput = document.querySelector("#countInput");
const quizSetSelect = document.querySelector("#quizSetSelect");
const generateButton = document.querySelector("#generateButton");
const quizEditor = document.querySelector("#quizEditor");
const saveButton = document.querySelector("#saveButton");
const resetButton = document.querySelector("#resetButton");

let state = structuredClone(defaultState);
let currentIndex = 0;
let isRevealed = false;
let audioContext;
let quizSets = [];

function loadState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) return structuredClone(defaultState);

  try {
    const parsed = JSON.parse(saved);
    if (!Array.isArray(parsed.quizzes) || parsed.quizzes.length === 0) {
      return structuredClone(defaultState);
    }
    return parsed;
  } catch {
    return structuredClone(defaultState);
  }
}

async function loadInitialState() {
  try {
    const requestedSetId = getRequestedQuizSetId();
    const endpoint = requestedSetId ? `${API_BASE}/quiz-sets/${requestedSetId}` : `${API_BASE}/quiz-sets/active`;
    const activeSet = await requestJson(endpoint);
    state = normalizeState(activeSet);
  } catch {
    state = loadState();
  }
  render();
}

function getRequestedQuizSetId() {
  const params = new URLSearchParams(window.location.search);
  const quizParam = params.get("quiz") || params.get("set");
  if (quizParam === "2" || quizParam === "final" || quizParam === "finish") {
    return "2";
  }
  if (quizParam === "3" || quizParam === "chocolatier" || quizParam === "choco") {
    return "chocolatier";
  }
  if (window.location.pathname === "/final" || window.location.pathname === "/final/") {
    return "2";
  }
  if (window.location.pathname === "/chocolatier-final" || window.location.pathname === "/chocolatier-final/") {
    return "chocolatier";
  }
  return "";
}

function normalizeState(value) {
  if (!value || !Array.isArray(value.quizzes) || value.quizzes.length === 0) {
    return structuredClone(defaultState);
  }

  return {
    id: value.id,
    topic: value.topic || "",
    level: normalizeLevel(value.level),
    quizzes: value.quizzes.map((quiz) => ({
      question: String(quiz.question || "").trim(),
      answer: String(quiz.answer || "").trim(),
      answerHtml: String(quiz.answerHtml || "").trim(),
    })).filter((quiz) => quiz.question && quiz.answer),
  };
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`요청 실패: ${response.status}`);
  }

  return response.json();
}

async function saveState(nextState) {
  state = nextState;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  try {
    const savedSet = await requestJson(`${API_BASE}/quiz-sets`, {
      method: "POST",
      body: JSON.stringify({
        topic: topicInput.value.trim() || state.topic || "직접 편집",
        level: state.level,
        quizzes: state.quizzes,
        isActive: true,
      }),
    });
    state = normalizeState(savedSet);
    await loadQuizSets();
  } catch (error) {
    alert("데이터베이스 저장에 실패했습니다. 서버를 실행했는지 확인해 주세요.");
    throw error;
  }
  currentIndex = 0;
  isRevealed = false;
  render();
}

function playTone(type) {
  audioContext ||= new AudioContext();
  const now = audioContext.currentTime;
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  const frequencies = type === "answer" ? [523.25, 659.25, 783.99] : [392, 493.88];

  oscillator.type = "sine";
  oscillator.frequency.setValueAtTime(frequencies[0], now);
  frequencies.forEach((frequency, index) => {
    oscillator.frequency.linearRampToValueAtTime(frequency, now + index * 0.07);
  });
  gain.gain.setValueAtTime(0.0001, now);
  gain.gain.exponentialRampToValueAtTime(0.22, now + 0.025);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.28);
  oscillator.connect(gain);
  gain.connect(audioContext.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.3);
}

function render() {
  const quiz = state.quizzes[currentIndex];
  pageTitle.textContent = QUIZ_TITLES[state.topic] || state.topic || "You쌤 퀴즈";
  quizCount.textContent = `${currentIndex + 1} / ${state.quizzes.length}`;
  quizQuestion.textContent = quiz.question;
  if (quiz.answerHtml) {
    quizAnswer.innerHTML = quiz.answerHtml;
  } else {
    quizAnswer.textContent = quiz.answer;
  }
  quizCard.classList.toggle("is-revealed", isRevealed);
  quizCard.classList.toggle("is-final-quiz", state.topic === "마무리 퀴즈" || state.topic === "쇼콜라티에 마무리 퀴즈");
  showButton.textContent = isRevealed ? "문제 보기" : "정답 보기";
}

function toggleAnswer() {
  isRevealed = !isRevealed;
  playTone(isRevealed ? "answer" : "move");
  render();
}

function moveQuiz(direction) {
  currentIndex = (currentIndex + direction + state.quizzes.length) % state.quizzes.length;
  isRevealed = false;
  playTone("move");
  render();
}

function openAdmin() {
  adminPanel.classList.add("is-open");
  adminPanel.setAttribute("aria-hidden", "false");
  passwordInput.focus();
}

function closeAdmin() {
  adminPanel.classList.remove("is-open");
  adminPanel.setAttribute("aria-hidden", "true");
}

function syncEditor() {
  levelInput.value = normalizeLevel(state.level);
  topicInput.value = state.topic || "";
  quizEditor.value = state.quizzes.map((quiz) => `${quiz.question} | ${quiz.answer}`).join("\n");
}

function normalizeLevel(level) {
  return level === "초등 고학년" ? "초등학생" : level || "초등학생";
}

async function loadQuizSets() {
  quizSets = await requestJson(`${API_BASE}/quiz-sets`);
  quizSetSelect.innerHTML = `<option value="">저장된 퀴즈를 선택하세요</option>`;
  quizSets.forEach((quizSet) => {
    const option = document.createElement("option");
    option.value = quizSet.id;
    option.textContent = `${quizSet.topic || "제목 없음"} · ${quizSet.level} · ${quizSet.quizCount}문항`;
    quizSetSelect.appendChild(option);
  });
  if (state.id) {
    quizSetSelect.value = String(state.id);
  }
}

async function loadQuizSet(id) {
  if (!id) return;
  const selectedSet = await requestJson(`${API_BASE}/quiz-sets/${id}`);
  state = normalizeState(selectedSet);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  currentIndex = 0;
  isRevealed = false;
  syncEditor();
  render();
  playTone("answer");
}

function parseEditor() {
  const quizzes = quizEditor.value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [question, ...answerParts] = line.split("|");
      return {
        question: question?.trim(),
        answer: answerParts.join("|").trim(),
      };
    })
    .filter((quiz) => quiz.question && quiz.answer);

  if (quizzes.length === 0) {
    throw new Error("문제와 정답을 한 줄 이상 입력해 주세요.");
  }

  return quizzes;
}

function generateQuizzes() {
  const topic = topicInput.value.trim() || "오늘의 수업";
  const level = levelInput.value;
  const count = Number(countInput.value);
  const templates = getTemplates(level);
  const quizzes = Array.from({ length: count }, (_, index) => {
    const template = templates[index % templates.length];
    return {
      question: template.question(topic, index + 1),
      answer: template.answer(topic),
    };
  });

  quizEditor.value = quizzes.map((quiz) => `${quiz.question} | ${quiz.answer}`).join("\n");
  playTone("answer");
}

function getTemplates(level) {
  if (level === "초등 저학년") {
    return [
      {
        question: (topic) => `${topic}에서 가장 중요한 낱말 하나를 고르면 무엇일까요?`,
        answer: (topic) => `${topic}의 핵심 낱말을 말하고, 왜 중요한지 한 문장으로 설명합니다.`,
      },
      {
        question: (topic) => `${topic}을 처음 배우는 친구에게 쉽게 설명하면 어떻게 말할까요?`,
        answer: (topic) => `${topic}을 쉬운 말과 예시로 설명합니다.`,
      },
      {
        question: (topic) => `${topic}과 관련된 안전 약속은 무엇일까요?`,
        answer: () => "주변을 살피고, 약속된 방법으로 행동하는 것입니다.",
      },
    ];
  }

  if (level === "중학생") {
    return [
      {
        question: (topic) => `${topic}이 우리 생활에 주는 장점과 주의할 점을 각각 하나씩 말해 보세요.`,
        answer: () => "장점과 한계를 함께 비교해 균형 있게 설명합니다.",
      },
      {
        question: (topic) => `${topic}을 문제 해결에 활용하려면 어떤 절차가 필요할까요?`,
        answer: () => "목표 설정, 자료 확인, 실행, 결과 점검의 순서가 필요합니다.",
      },
      {
        question: (topic) => `${topic}에 대해 사실과 의견을 구분해야 하는 이유는 무엇일까요?`,
        answer: () => "정확한 판단을 하고 잘못된 정보를 줄이기 위해서입니다.",
      },
    ];
  }

  return [
    {
      question: (topic) => `${topic}의 핵심 개념을 한 문장으로 설명하면 무엇일까요?`,
      answer: (topic) => `${topic}에서 꼭 기억해야 할 중심 생각을 간단히 말합니다.`,
    },
    {
      question: (topic) => `${topic}을 배울 때 실제 생활에서 떠올릴 수 있는 예시는 무엇일까요?`,
      answer: () => "학교, 집, 지역사회에서 볼 수 있는 구체적인 장면을 예로 듭니다.",
    },
    {
      question: (topic) => `${topic}을 잘 이해했는지 확인하려면 어떤 질문을 해볼 수 있을까요?`,
      answer: () => "왜 그런지, 어디에 쓰이는지, 다른 사례는 무엇인지 질문합니다.",
    },
  ];
}

quizCard.addEventListener("click", toggleAnswer);
showButton.addEventListener("click", toggleAnswer);
prevButton.addEventListener("click", () => moveQuiz(-1));
nextButton.addEventListener("click", () => moveQuiz(1));
adminOpenButton.addEventListener("click", openAdmin);
adminCloseButton.addEventListener("click", closeAdmin);
generateButton.addEventListener("click", generateQuizzes);
quizSetSelect.addEventListener("change", () => {
  loadQuizSet(quizSetSelect.value).catch(() => {
    alert("저장된 퀴즈를 불러오지 못했습니다.");
  });
});

loginForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (passwordInput.value !== ADMIN_PASSWORD) {
    playTone("move");
    passwordInput.select();
    return;
  }
  loginForm.hidden = true;
  editorArea.hidden = false;
  syncEditor();
  loadQuizSets().catch(() => {
    quizSetSelect.innerHTML = `<option value="">서버 연결 후 사용할 수 있습니다</option>`;
  });
  quizEditor.focus();
  playTone("answer");
});

saveButton.addEventListener("click", () => {
  try {
    saveState({
      topic: topicInput.value.trim(),
    level: normalizeLevel(levelInput.value),
      quizzes: parseEditor(),
    }).then(() => {
      closeAdmin();
      playTone("answer");
    }).catch(() => {});
  } catch (error) {
    alert(error.message);
  }
});

resetButton.addEventListener("click", () => {
  saveState(structuredClone(defaultState));
  syncEditor();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeAdmin();
  if (event.key === "ArrowLeft") moveQuiz(-1);
  if (event.key === "ArrowRight") moveQuiz(1);
  if (event.key === " " && !adminPanel.classList.contains("is-open")) {
    event.preventDefault();
    toggleAnswer();
  }
});

loadInitialState();
