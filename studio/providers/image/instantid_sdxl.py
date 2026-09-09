"""ImageProvider backed by ComfyUI + InstantID (identity-specialized
reference conditioning), as an alternative to ComfyUISDXLProvider's
img2img-only reference path.

The graph in providers/workflows/character_instantid_v1_api.json is a real
workflow exported from the ComfyUI web UI ("Export (API)"), verified with
real parameters: RealVisXL_V5.0_Lightning_fp16.safetensors checkpoint,
ip-adapter.bin InstantID model, instantid/diffusion_pytorch_model.safetensors
ControlNet, weight=0.8, cfg=4.5, ~1016x1016. Like comfyui_sdxl.py's graph,
this wiring is proven -- only touch the fixed values (checkpoint, sampler,
cfg, steps, InstantID weight) baked into the JSON template if a real test
proves it's necessary.

Unlike ComfyUISDXLProvider's reference_image_path (optional img2img),
InstantID's entire mechanism IS the reference image -- there is no
meaningful no-reference mode, so reference_image_path is required here and
generate_image raises if it's missing.

Licensing note: InstantID's "InstantIDFaceAnalysis" node (graph node "38")
loads an InsightFace model, the same non-commercial-research-only
dependency documented in docs/identity_providers_licensing.md. That
document's rules were written for providers/base.py's IdentityProvider
category (registered under PROVIDERS["identity"]); this class is an
ImageProvider instead, so it isn't covered by that registry-level gate.
Anyone wiring this into the default pipeline should apply the same rules
(opt-in only, never a default, no bundled weights) regardless of which
provider category it's registered under.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from providers._comfy_client import ComfyClient

_WORKFLOW_PATH = Path(__file__).resolve().parent.parent / "workflows" / "character_instantid_v1_api.json"


class InstantIDImageProvider:
    def __init__(self, client: Optional[ComfyClient] = None):
        self.client = client or ComfyClient()

    def generate_image(
        self, prompt: str, negative_prompt: str, width: int, height: int, seed: Optional[int] = None,
        reference_image_path: Optional[Path] = None, denoise: float = 1.0,
    ) -> Path:
        if reference_image_path is None:
            raise ValueError(
                "InstantIDImageProvider requires reference_image_path -- InstantID's "
                "entire conditioning mechanism is the reference face image, unlike "
                "ComfyUISDXLProvider's optional img2img reference_image_path"
            )
        # denoise has no analog in this graph: InstantID conditions identity via
        # the ApplyInstantID node's fixed `weight` (baked into the JSON template,
        # verified at 0.8), not by blending a starting latent like SDXL's img2img
        # path. Accepted here only so this class is a drop-in ImageProvider.

        seed = seed if seed is not None else 0
        graph = json.loads(_WORKFLOW_PATH.read_text(encoding="utf-8"))

        input_name = self.client.upload_input_image(reference_image_path)
        graph["13"]["inputs"]["image"] = input_name
        graph["39"]["inputs"]["text"] = prompt
        graph["40"]["inputs"]["text"] = negative_prompt
        graph["5"]["inputs"]["width"] = width
        graph["5"]["inputs"]["height"] = height
        graph["3"]["inputs"]["seed"] = seed

        # The exported workflow ends in a PreviewImage node ("15"), which
        # ComfyUI writes to its temp/ directory (type "temp") -- but
        # ComfyClient.output_path() only ever looks under output/. Swap it for
        # a SaveImage node with the same "images" input, matching
        # comfyui_sdxl.py's own SaveImage node, so the shared client can find
        # the result.
        graph["15"] = {
            "class_type": "SaveImage",
            "inputs": {"images": ["8", 0], "filename_prefix": "OpenVideoStudio/keyframe_instantid"},
        }

        if not self.client.is_available():
            raise RuntimeError("ComfyUI is not reachable at " + self.client.server)

        prompt_id = self.client.submit(graph, client_id_prefix="ovs-instantid")
        entry = self.client.wait_for_result(prompt_id, timeout_minutes=6.0)
        return self.client.output_path(entry, node_id="15", media_key="images")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate one test image via ComfyUI/InstantID")
    parser.add_argument("prompt")
    parser.add_argument("reference_image", type=Path)
    parser.add_argument("--negative", default="photograph, deformed, glitch, noisy, realistic, stock photo")
    parser.add_argument("--width", type=int, default=1016)
    parser.add_argument("--height", type=int, default=1016)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    provider = InstantIDImageProvider()
    path = provider.generate_image(
        args.prompt, args.negative, args.width, args.height, args.seed,
        reference_image_path=args.reference_image,
    )
    print(f"Generated: {path}")
