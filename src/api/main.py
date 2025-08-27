import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from src.agent.weather_agent_lc import WeatherAgentLC
from src.utils.logger import setup_logger
from src.utils.metrics import MetricsCollector
from src.dashboard.dashboard import WeatherAgentDashboard
from pathlib import Path
import webbrowser

app = FastAPI(title="Weather Agent API", version="1.0.0")

logger = setup_logger("weather_api")
metrics = MetricsCollector()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем папку dashboard на /dashboard-static
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DASHBOARD_DIR = BASE_DIR / "dashboard"
DEFAULT_DASHBOARD_DIR.mkdir(exist_ok=True)
app.mount("/dashboard-static", StaticFiles(directory=str(DEFAULT_DASHBOARD_DIR)), name="dashboard_static")

class ChatRequest(BaseModel):
    session_id: str = Field(..., example="user1")  # Идентификатор сессии для памяти диалога
    message: str = Field(..., example="What is the weather in Berlin?")

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    ts: float  # Временная метка ответа

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)  # Оценка от 1 до 5
    feedback_text: str = ""  # Дополнительный текст отзыва
    response_quality: str = "good"  # Качество ответа (good/bad)

class GenerateDashboardRequest(BaseModel):
    metrics_dir: str = Field("metrics", description="Directory with CSV metrics")
    output_dir: str = Field("dashboard", description="Output directory for generated dashboard")
    open_in_browser: bool = Field(False, description="Return 303 redirect to dashboard page if true")

@app.get("/health")
def health():
    # Проверка работоспособности API
    return {"status": "ok", "ts": time.time()}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    start_time = time.time()
    try:
        logger.info(f"[chat] session={req.session_id} message={req.message!r}")
        agent = WeatherAgentLC(session_id=req.session_id)
        reply = agent.ask(req.message)

        # Считаем время ответа и анализируем результат
        response_time = (time.time() - start_time) * 1000.0
        weather_found = ("City not found" not in reply) and ("Please specify" not in reply)
        city_extracted = agent._extract_city(req.message) if hasattr(agent, "_extract_city") else ""

        # Логируем запрос в метрики для анализа производительности
        metrics.log_request(
            session_id=req.session_id,
            message=req.message,
            response=reply,
            response_time_ms=response_time,
            city_extracted=city_extracted,
            weather_found=weather_found,
        )
        logger.info(f"[chat] done in {response_time:.2f}ms found={weather_found} city={city_extracted}")
        return ChatResponse(session_id=req.session_id, reply=reply, ts=time.time())

    except Exception as e:
        # При ошибке логируем её и возвращаем 500
        response_time = (time.time() - start_time) * 1000.0
        err = str(e)
        logger.error(f"[chat] ERROR {err}")
        metrics.log_error(
            session_id=req.session_id,
            error_type="chat_error",
            error_message=err,
            request_data={"message": req.message, "response_time_ms": response_time},
        )
        raise HTTPException(status_code=500, detail=err)

@app.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    try:
        logger.info(f"[feedback] session={req.session_id} rating={req.rating}")
        # Сохраняем отзыв пользователя для анализа качества ответов
        metrics.log_feedback(
            session_id=req.session_id,
            message=req.message,
            rating=req.rating,
            feedback_text=req.feedback_text,
            response_quality=req.response_quality,
        )
        return {"status": "success", "message": "Feedback recorded successfully"}
    except Exception as e:
        logger.error(f"[feedback] ERROR {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics():
    try:
        # Возвращаем сводку метрик для мониторинга
        summary = metrics.get_metrics_summary()
        return summary
    except Exception as e:
        logger.error(f"[metrics] ERROR {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dashboard/generate")
def generate_dashboard(req: GenerateDashboardRequest, request: Request):
    try:
        # Определяем пути к папкам с метриками и для вывода дашборда
        metrics_dir_path = (BASE_DIR / req.metrics_dir) if not Path(req.metrics_dir).is_absolute() else Path(req.metrics_dir)
        output_dir_path = (BASE_DIR / req.output_dir) if not Path(req.output_dir).is_absolute() else Path(req.output_dir)

        # Генерируем HTML-отчёт с графиками и статистикой
        dash = WeatherAgentDashboard(metrics_dir=str(metrics_dir_path), output_dir=str(output_dir_path))
        out_path = dash.generate_html_report()

        url_hint = None
        # Если дашборд генерируется в стандартную папку, формируем URL для открытия
        if output_dir_path.resolve() == DEFAULT_DASHBOARD_DIR.resolve():
            url_hint = "/dashboard-static/dashboard.html"
            
        if req.open_in_browser and url_hint:
            # Открываем дашборд в браузере пользователя 
            base = str(request.base_url).rstrip("/")
            full_url = f"{base}{url_hint}"
            try:
                webbrowser.open_new_tab(full_url)
            except Exception as _e:
                logger.warning(f"[dashboard.generate] webbrowser open failed: {_e}")
            return RedirectResponse(url=url_hint, status_code=303)

        # Возвращаем информацию о сгенерированном дашборде
        return JSONResponse({
            "status": "ok",
            "html_path": str(out_path),
            "open_url": url_hint or str(out_path),
        })
    except Exception as e:
        logger.error(f"[dashboard.generate] ERROR {e}")
        raise HTTPException(status_code=500, detail=str(e))
