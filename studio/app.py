"""Web entrypoint for the OpenVideoStudio Vercel deployment.

The complete GPU/local application remains in local_app.py. Vercel is used
for the browser UI only because the generation pipeline expects local Ollama,
ComfyUI, FFmpeg/NVENC, and a persistent filesystem.
"""
import gradio as gr
from fastapi import FastAPI

with gr.Blocks(title="OpenVideoStudio") as demo:
    gr.Markdown("# 🎬 OpenVideoStudio")
    gr.Markdown(
        "### Local-first AI video creation studio\n"
        "This Vercel deployment provides the web interface. The full generation "
        "engine runs on your local Windows/NVIDIA machine."
    )
    with gr.Tabs():
        with gr.Tab("AI Creation"):
            gr.Markdown(
                "Prompt → script → storyboard → review → keyframes → video → "
                "narration → subtitles → final edit."
            )
            gr.Markdown(
                "**Run the full engine locally:**\n"
                "1. Install the dependencies from the project installation guide.\n"
                "2. Start Ollama + ComfyUI.\n"
                "3. Run python local_app.py from the studio folder."
            )
        with gr.Tab("Media Remix"):
            gr.Markdown(
                "Select a local media folder, review the generated shot plan, "
                "then render the final video on your own machine."
            )
            gr.Markdown(
                "The Media Remix engine requires local files, FFmpeg/NVENC and "
                "the original desktop pipeline."
            )

app = FastAPI(title="OpenVideoStudio")
gr.mount_gradio_app(app, demo, path="/")
