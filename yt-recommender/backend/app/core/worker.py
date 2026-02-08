import asyncio
from app.services.youtube import resolve_channel, fetch_latest_videos
from app.services.ai import analyse
from app.services.mongo_client import create_job, get_job, update_job
from uuid import uuid4
from app.services.email import send_email
from app.schemas.schemas import JobStatusResponse
from datetime import datetime, timezone
import asyncio
import logging

logger = logging.getLogger(__name__)

async def process_job(job_id: str):
    job = await get_job(job_id)
    if not job:
        return

    # Step 1: Resolve channel
    try:
        channel_id = await resolve_channel(job["channel_name"])
        await update_job(job_id, {
            "channel_id": channel_id,
            "status": "channel_resolved",
            "updated_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        await update_job(job_id, {"status": "failed", "error": str(e)})
        return

    # Step 2: Fetch videos
    try:
        videos = await fetch_latest_videos(channel_id)
        await update_job(job_id, {"videos": videos, "status": "videos_fetched"})
    except Exception as e:
        await update_job(job_id, {"status": "failed", "error": str(e)})
        return

    # Step 3: AI analysis
    try:
        job = await get_job(job_id)
        services = job.get("services", [])
        report = await analyse(videos, services=services)

        await update_job(job_id, {
            "ai_report": report,
            "status": "completed"
        })
    except Exception as e:
        await update_job(job_id, {"status": "failed", "error": str(e)})
        return

    # Step 4: Email (non-blocking, optional)
    
    try:
                email_summary = {}
                if isinstance(report, dict):
                    # Prefer the structured email summary if present
                    email_summary = report.get("email_summary") or {}

                email_body = (
                    "Your AI analysis report is ready 🎉\n\n"
                    "Please log in to your dashboard to view the full report.\n\n"
                    "— TubeIntelligence"
                )

                if email_summary:
                    headline = email_summary.get("headline", "")
                    teaser = email_summary.get("teaser", "")
                    key_insights = email_summary.get("key_insights", [])
                    cta = email_summary.get("cta", "")

                    if headline:
                        email_body += f"\n\n{headline}"
                    if teaser:
                        email_body += f"\n{teaser}"
                    if key_insights:
                        formatted_insights = "\n".join([f"- {item}" for item in key_insights[:3]])
                        email_body += f"\n\nKey insights:\n{formatted_insights}"
                    if cta:
                        email_body += f"\n\n{cta}"

                await asyncio.to_thread(
                    send_email,
                    to_email=job["email"],
                    subject="Your AI Analysis Report by TubeIntelligence is here!",
                    body=email_body
                )
    except Exception as e:
            print(f"Failed to send email: {e}")  # Log this properly in real apps
            logger.error("Failed to send email", exc_info=e)
