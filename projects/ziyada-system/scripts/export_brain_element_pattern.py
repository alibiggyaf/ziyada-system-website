#!/usr/bin/env python3
"""Export "brain element pattern" assets.

Generates:
1. Combined brain element (ring + core) from multiple angles.
2. Separated elements (ring-only and core-only) from multiple angles.
3. Repeating pattern packs for stationery and social media use.

All exports are transparent and delivered as both PNG and SVG.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw


PURPLE = (139, 92, 246)
BLUE = (59, 130, 246)
OUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "brain-element-pattern"
W = 2400
H = 2400


@dataclass
class Line3D:
    a: np.ndarray
    b: np.ndarray
    color: Tuple[int, int, int]
    alpha: float
    width: float


def hex_color(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def with_alpha(rgb: Tuple[int, int, int], alpha: float) -> Tuple[int, int, int, int]:
    return (*rgb, int(max(0.0, min(1.0, alpha)) * 255))


def build_torus_knot_tube(
    p: int = 2,
    q: int = 3,
    ring_radius: float = 3.2,
    ring_thickness: float = 1.15,
    tube_radius: float = 0.62,
    t_steps: int = 320,
    phi_steps: int = 12,
) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, t_steps, endpoint=False)
    x = (ring_radius + ring_thickness * np.cos(q * t)) * np.cos(p * t)
    y = (ring_radius + ring_thickness * np.cos(q * t)) * np.sin(p * t)
    z = ring_thickness * np.sin(q * t)
    center = np.stack([x, y, z], axis=1)

    tangent = np.gradient(center, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1, keepdims=True)

    up = np.tile(np.array([0.0, 0.0, 1.0]), (t_steps, 1))
    normal = np.cross(up, tangent)
    tiny = np.linalg.norm(normal, axis=1) < 1e-6
    if np.any(tiny):
        fallback = np.tile(np.array([1.0, 0.0, 0.0]), (np.sum(tiny), 1))
        normal[tiny] = np.cross(fallback, tangent[tiny])
    normal /= np.linalg.norm(normal, axis=1, keepdims=True)

    binormal = np.cross(tangent, normal)
    binormal /= np.linalg.norm(binormal, axis=1, keepdims=True)

    phi = np.linspace(0, 2 * np.pi, phi_steps, endpoint=False)
    circle_local = np.stack([np.cos(phi), np.sin(phi)], axis=1)
    tube = np.zeros((t_steps, phi_steps, 3), dtype=float)
    for i in range(t_steps):
        tube[i, :, :] = (
            center[i]
            + tube_radius * circle_local[:, 0:1] * normal[i]
            + tube_radius * circle_local[:, 1:2] * binormal[i]
        )
    return tube


def build_core_sphere(radius: float = 2.05, u_steps: int = 44, v_steps: int = 28) -> np.ndarray:
    u = np.linspace(0, 2 * np.pi, u_steps, endpoint=False)
    v = np.linspace(0, np.pi, v_steps)
    uu, vv = np.meshgrid(u, v, indexing="xy")
    x = radius * np.cos(uu) * np.sin(vv)
    y = radius * np.sin(uu) * np.sin(vv)
    z = radius * np.cos(vv)
    return np.stack([x, y, z], axis=2)


def mesh_lines(mesh: np.ndarray, color: Tuple[int, int, int], alpha: float, width: float) -> List[Line3D]:
    rows, cols, _ = mesh.shape
    out: List[Line3D] = []

    for i in range(rows):
        pts = mesh[i]
        for j in range(cols):
            a = pts[j]
            b = pts[(j + 1) % cols]
            out.append(Line3D(a, b, color, alpha, width))

    for j in range(cols):
        for i in range(rows):
            a = mesh[i, j]
            b = mesh[(i + 1) % rows, j]
            out.append(Line3D(a, b, color, alpha * 0.9, width))

    return out


def offset_lines(lines: Iterable[Line3D], dx: float, dy: float, dz: float) -> List[Line3D]:
    out: List[Line3D] = []
    delta = np.array([dx, dy, dz], dtype=float)
    for ln in lines:
        out.append(Line3D(ln.a + delta, ln.b + delta, ln.color, ln.alpha, ln.width))
    return out


def rotation_matrix(elev_deg: float, azim_deg: float) -> np.ndarray:
    ex = np.deg2rad(elev_deg)
    ez = np.deg2rad(azim_deg)

    rx = np.array(
        [
            [1, 0, 0],
            [0, np.cos(ex), -np.sin(ex)],
            [0, np.sin(ex), np.cos(ex)],
        ]
    )
    rz = np.array(
        [
            [np.cos(ez), -np.sin(ez), 0],
            [np.sin(ez), np.cos(ez), 0],
            [0, 0, 1],
        ]
    )
    return rz @ rx


def project(p: np.ndarray, width: int, height: int, camera_distance: float = 15.0, focal: float = 2050.0) -> Tuple[float, float, float]:
    zc = p[2] + camera_distance
    zc = max(zc, 0.1)
    s = focal / zc
    x = width * 0.5 + p[0] * s
    y = height * 0.5 - p[1] * s
    return x, y, zc


def add_stars(
    draw_png: ImageDraw.ImageDraw,
    svg_parts: List[str],
    rng: np.random.Generator,
    rot: np.ndarray,
    width: int,
    height: int,
) -> None:
    stars = rng.uniform(-5.4, 5.4, size=(120, 3))
    for p in stars:
        pr = rot @ p
        x, y, zc = project(pr, width=width, height=height)
        if 0 <= x < width and 0 <= y < height:
            r = max(1.3, 3.0 / (zc * 0.16))
            a = int(64)
            draw_png.ellipse((x - r, y - r, x + r, y + r), fill=(*BLUE, a))
            svg_parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{hex_color(BLUE)}" fill-opacity="0.25" />'
            )


def render_scene(
    filename_base: str,
    elev: float,
    azim: float,
    lines: Iterable[Line3D],
    width: int = W,
    height: int = H,
    add_starfield: bool = True,
    focal: float = 2050.0,
    camera_distance: float = 15.0,
) -> None:
    rot = rotation_matrix(elev, azim)

    projected = []
    for ln in lines:
        a3 = rot @ ln.a
        b3 = rot @ ln.b
        ax, ay, az = project(a3, width=width, height=height, focal=focal, camera_distance=camera_distance)
        bx, by, bz = project(b3, width=width, height=height, focal=focal, camera_distance=camera_distance)
        depth = (az + bz) * 0.5
        projected.append((depth, ax, ay, bx, by, ln))

    projected.sort(key=lambda x: x[0], reverse=True)

    png = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(png, "RGBA")

    svg_parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    ]

    if add_starfield:
        rng = np.random.default_rng(11)
        add_stars(draw, svg_parts, rng, rot, width=width, height=height)

    for _, ax, ay, bx, by, ln in projected:
        rgba = with_alpha(ln.color, ln.alpha)
        draw.line((ax, ay, bx, by), fill=rgba, width=max(1, int(round(ln.width * 2.2))))

        svg_parts.append(
            (
                f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" y2="{by:.2f}" '
                f'stroke="{hex_color(ln.color)}" stroke-opacity="{ln.alpha:.3f}" '
                f'stroke-width="{ln.width:.2f}" stroke-linecap="round" />'
            )
        )

    svg_parts.append("</svg>")

    png_path = OUT_DIR / f"{filename_base}.png"
    svg_path = OUT_DIR / f"{filename_base}.svg"
    png.save(png_path)
    svg_path.write_text("\n".join(svg_parts), encoding="utf-8")


def create_pattern_grid(
    filename_base: str,
    motif_lines: Iterable[Line3D],
    elev: float,
    azim: float,
    canvas_w: int,
    canvas_h: int,
    tile_spacing: float,
    jitter: float,
    include_secondary: bool,
) -> None:
    """Build a repeating pattern by duplicating motif lines in a 3D grid then projecting."""
    instances: List[Line3D] = []
    nx = int(np.ceil(canvas_w / tile_spacing)) + 3
    ny = int(np.ceil(canvas_h / tile_spacing)) + 3

    center_x = (nx - 1) / 2.0
    center_y = (ny - 1) / 2.0

    # Convert pixel-like spacing into model units that project nicely.
    unit = 0.010
    spacing_u = tile_spacing * unit
    jitter_u = jitter * unit

    rng = np.random.default_rng(42)

    motif_lines = list(motif_lines)
    for ix in range(nx):
        for iy in range(ny):
            dx = (ix - center_x) * spacing_u
            dy = (iy - center_y) * spacing_u
            jx = rng.uniform(-jitter_u, jitter_u)
            jy = rng.uniform(-jitter_u, jitter_u)
            group = offset_lines(motif_lines, dx + jx, dy + jy, 0.0)
            instances.extend(group)

            if include_secondary and (ix + iy) % 2 == 0:
                instances.extend(offset_lines(motif_lines, dx + jx + spacing_u * 0.3, dy + jy + spacing_u * 0.25, -0.25))

    render_scene(
        filename_base=filename_base,
        elev=elev,
        azim=azim,
        lines=instances,
        width=canvas_w,
        height=canvas_h,
        add_starfield=False,
        focal=1780.0,
        camera_distance=17.0,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tube = build_torus_knot_tube()
    core = build_core_sphere()

    ring_lines = mesh_lines(tube, PURPLE, alpha=0.23, width=1.0)
    core_lines = mesh_lines(core, BLUE, alpha=0.30, width=0.9)
    combined_lines = ring_lines + core_lines

    angles: Dict[str, Tuple[float, float]] = {
        "front": (10, 34),
        "isometric": (27, 46),
        "left": (18, 112),
        "right": (18, -38),
        "top": (76, 20),
        "tilt": (38, 182),
    }

    for name, (elev, azim) in angles.items():
        # Full element.
        render_scene(
            filename_base=f"brain-element-pattern-{name}",
            elev=elev,
            azim=azim,
            lines=combined_lines,
            add_starfield=True,
        )

        # Separated outer ring and inner core for independent usage.
        render_scene(
            filename_base=f"brain-element-ring-{name}",
            elev=elev,
            azim=azim,
            lines=ring_lines,
            add_starfield=False,
        )
        render_scene(
            filename_base=f"brain-element-core-{name}",
            elev=elev,
            azim=azim,
            lines=core_lines,
            add_starfield=False,
        )

    # Pattern pack: seamless-ready repeating visuals for stationery/social use.
    create_pattern_grid(
        filename_base="brain-element-pattern-grid-square",
        motif_lines=ring_lines,
        elev=25,
        azim=40,
        canvas_w=2400,
        canvas_h=2400,
        tile_spacing=640,
        jitter=70,
        include_secondary=True,
    )
    create_pattern_grid(
        filename_base="brain-element-pattern-grid-portrait",
        motif_lines=combined_lines,
        elev=28,
        azim=52,
        canvas_w=2480,
        canvas_h=3508,
        tile_spacing=760,
        jitter=90,
        include_secondary=False,
    )
    create_pattern_grid(
        filename_base="brain-element-pattern-grid-social",
        motif_lines=combined_lines,
        elev=30,
        azim=35,
        canvas_w=1920,
        canvas_h=1080,
        tile_spacing=560,
        jitter=60,
        include_secondary=True,
    )
    create_pattern_grid(
        filename_base="brain-element-pattern-grid-vertical-social",
        motif_lines=ring_lines,
        elev=34,
        azim=20,
        canvas_w=1080,
        canvas_h=1920,
        tile_spacing=520,
        jitter=50,
        include_secondary=True,
    )

    print(f"Export complete: {OUT_DIR}")
    for file in sorted(OUT_DIR.glob("brain-element-*")):
        print(f"- {file.name}")


if __name__ == "__main__":
    main()
