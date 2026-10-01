"""Vercel ASGI entrypoint for OpenVideoStudio.

Gradio exposes its server as a FastAPI-compatible application. Build that
application directly instead of calling demo.launch(), which is intended for
a long-running local process.
"""
from studio.app import demo
from gradio.routes import App as GradioApp

app = GradioApp.create_app(demo)
