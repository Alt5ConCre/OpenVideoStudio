"""Tests for providers/image/instantid_sdxl.py's InstantID graph wiring.

InstantIDImageProvider builds its graph from a real ComfyUI-exported
workflow (providers/workflows/character_instantid_v1_api.json) instead of
constructing nodes inline like comfyui_sdxl.py -- these tests exist so a
regression in the dynamic-parameter node IDs, the PreviewImage->SaveImage
swap, or the required-reference-image check would be caught here instead
of only surfacing as a wrong path or a silently ignored parameter at
generation time."""
from __future__ import annotations

from pathlib import Path

import pytest

from providers.image.instantid_sdxl import InstantIDImageProvider


class _FakeComfyClient:
    def __init__(self):
        self.submitted_graph = None
        self.uploaded_path = None

    def is_available(self, timeout: float = 5.0) -> bool:
        return True

    def upload_input_image(self, local_path, dest_name=None) -> str:
        self.uploaded_path = local_path
        return "uploaded_ref.png"

    def submit(self, graph: dict, client_id_prefix: str = "openvideostudio") -> str:
        self.submitted_graph = graph
        return "fake-prompt-id"

    def wait_for_result(self, prompt_id: str, timeout_minutes: float = 6.0) -> dict:
        return {"outputs": {"15": {"images": [{"filename": "out.png", "subfolder": ""}]}}}

    def output_path(self, entry: dict, node_id: str, media_key: str = "images") -> Path:
        return Path("fake_output") / entry["outputs"][node_id][media_key][0]["filename"]


def test_generate_image_requires_reference_image_path():
    client = _FakeComfyClient()
    provider = InstantIDImageProvider(client=client)

    with pytest.raises(ValueError, match="requires reference_image_path"):
        provider.generate_image("a cat", "blurry", 1016, 1016)

    assert client.submitted_graph is None  # never even got to submitting


def test_generate_image_wires_dynamic_params_into_expected_nodes():
    client = _FakeComfyClient()
    provider = InstantIDImageProvider(client=client)
    ref = Path("some_reference.png")

    path = provider.generate_image("a hero", "ugly", 1016, 1016, seed=42, reference_image_path=ref)

    assert client.uploaded_path == ref
    graph = client.submitted_graph
    assert graph["39"]["inputs"]["text"] == "a hero"
    assert graph["40"]["inputs"]["text"] == "ugly"
    assert graph["5"]["inputs"]["width"] == 1016
    assert graph["5"]["inputs"]["height"] == 1016
    assert graph["3"]["inputs"]["seed"] == 42
    assert graph["13"]["inputs"]["image"] == "uploaded_ref.png"
    assert path == Path("fake_output") / "out.png"
    # untouched proven values from the exported workflow stay intact
    assert graph["4"]["inputs"]["ckpt_name"] == "RealVisXL_V5.0_Lightning_fp16.safetensors"
    assert graph["60"]["inputs"]["weight"] == 0.8


def test_generate_image_defaults_seed_to_zero_when_unset():
    client = _FakeComfyClient()
    provider = InstantIDImageProvider(client=client)

    provider.generate_image("a", "b", 1016, 1016, reference_image_path=Path("ref.png"))

    assert client.submitted_graph["3"]["inputs"]["seed"] == 0


def test_generate_image_replaces_preview_node_with_save_image():
    client = _FakeComfyClient()
    provider = InstantIDImageProvider(client=client)

    provider.generate_image("a", "b", 1016, 1016, reference_image_path=Path("ref.png"))

    node_15 = client.submitted_graph["15"]
    assert node_15["class_type"] == "SaveImage"
    assert node_15["class_type"] != "PreviewImage"
    assert node_15["inputs"]["images"] == ["8", 0]
    assert "filename_prefix" in node_15["inputs"]


def test_generate_image_reloads_graph_fresh_each_call_no_cross_call_pollution():
    client = _FakeComfyClient()
    provider = InstantIDImageProvider(client=client)

    provider.generate_image(
        "first prompt", "first negative", 512, 512, seed=1, reference_image_path=Path("ref1.png"),
    )
    first_graph = client.submitted_graph

    provider.generate_image(
        "second prompt", "second negative", 768, 768, seed=2, reference_image_path=Path("ref2.png"),
    )
    second_graph = client.submitted_graph

    # a new dict is loaded from the JSON template each call, not the same
    # instance mutated in place and reused
    assert first_graph is not second_graph
    assert first_graph["39"]["inputs"]["text"] == "first prompt"
    assert first_graph["5"]["inputs"]["width"] == 512
    assert first_graph["3"]["inputs"]["seed"] == 1
    assert second_graph["39"]["inputs"]["text"] == "second prompt"
    assert second_graph["5"]["inputs"]["width"] == 768
    assert second_graph["3"]["inputs"]["seed"] == 2
