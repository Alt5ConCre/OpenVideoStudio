"""Vercel entrypoint for OpenVideoStudio.

The actual UI lives in studio/app.py as a Gradio Blocks application.
Vercel's Python runtime requires a top-level ASGI/WSGI app, so we mount
the Gradio UI into FastAPI instead of treating studio/app.py as a raw
Vercel function.
"""
from fastapi import FastAPI
import gradio as gr

from studio.app import demo

app = FastAPI(title="OpenVideoStudio")
app = gr.mount_gradio_app(app, demo, path="/")
