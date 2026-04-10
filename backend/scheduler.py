from apscheduler.schedulers.background import BackgroundScheduler
from backend.agents.report_agent import generate_report
from datetime import datetime
import threading

scheduler = BackgroundScheduler()
pending = {}
lock = threading.Lock()

def start():
    scheduler.start()

def add_reminder(session_id: str, message: str, interval_minutes: int = 1):
    job_id = f"{session_id}_{datetime.now().timestamp()}"
    scheduler.add_job(
        func=_queue_reminder,
        trigger="interval",
        minutes=interval_minutes,
        id=job_id,
        args=[session_id, message]
    )

def _queue_reminder(session_id: str, message: str):
    with lock:
        print(f"DEBUG - queuing reminder for {session_id}: {message}")
        pending.setdefault(session_id, []).append(message)

def pop_reminders(session_id: str):
    with lock:
        msgs = pending.get(session_id, [])
        pending[session_id] = []
        return msgs
def schedule_weekly_report(session_id: str):
    scheduler.add_job(
        func=_run_weekly_report,
        trigger="interval",
        weeks=1,
        id=f"weekly_report_{session_id}",
        args=[session_id],
        replace_existing=True
    )

def _run_weekly_report(session_id: str):
    print(f"Generating weekly report for {session_id}")
    report = generate_report(session_id)
    _queue_reminder(session_id, f"Weekly health report: {report}")