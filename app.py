from fastapi import FastAPI
import gradio as gr
from studio.app import demo

app = FastAPI(title="OpenVideoStudio")
gr.mount_gradio_app(app, demo, path="/")
