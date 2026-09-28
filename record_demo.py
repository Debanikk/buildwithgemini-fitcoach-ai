import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

APP_URL = "https://fitcoach-ai-frontend-374049757837.us-east1.run.app"
ARTIFACT_DIR = Path("/config/.gemini/antigravity/brain/7b067115-625a-41d0-b828-4a1788ce3fe6")
TEMP_VIDEO_DIR = Path("/tmp/video_record")

async def record_demo():
    if TEMP_VIDEO_DIR.exists():
        shutil.rmtree(TEMP_VIDEO_DIR)
    TEMP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(TEMP_VIDEO_DIR),
            record_video_size={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        print(f"Navigating to {APP_URL}...")
        await page.goto(APP_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Prompt 1: Core app strength (Exercise recommendation)
        prompt1 = "Recommend exercises for legs"
        print(f"Typing Prompt 1: '{prompt1}'...")
        await page.fill("#input", prompt1)
        await page.wait_for_timeout(800)
        await page.click("button.send-btn")

        # Wait for agent response
        print("Waiting for response to Prompt 1...")
        await page.wait_for_selector(".msg.agent .bubble:not(#typing-bubble)", timeout=45000)
        await page.wait_for_timeout(4000)

        # Prompt 2: Rich prompt with calculation tool call
        prompt2 = "Calculate my target heart rate zones for age 30 and resting HR 60"
        print(f"Typing Prompt 2: '{prompt2}'...")
        await page.fill("#input", prompt2)
        await page.wait_for_timeout(800)
        await page.click("button.send-btn")

        # Wait for second response
        print("Waiting for response to Prompt 2...")
        # Wait until there are at least 3 agent messages
        await page.wait_for_function("document.querySelectorAll('.msg.agent').length >= 3", timeout=45000)
        await page.wait_for_timeout(6000)

        print("Closing context to finalize video...")
        await context.close()
        await browser.close()

    # Find recorded video file
    video_files = list(TEMP_VIDEO_DIR.glob("*.webm"))
    if video_files:
        src_video = video_files[0]
        dest_video = ARTIFACT_DIR / "fitcoach_demo.webm"
        shutil.copy(src_video, dest_video)
        print(f"Demo video saved successfully to {dest_video}")
    else:
        print("Error: No recorded video file found.")

if __name__ == "__main__":
    asyncio.run(record_demo())
