from pygame import draw
from pygame.gfxdraw import *
from pygame.surface import Surface

import numpy as np

from src.core.utils.constants import *


class Graphics:

    @staticmethod
    def pie(
            surface: Surface,
            x: float, y: float, r: float,
            start_angle: float, stop_angle: float,
            color=(255, 255, 255),
            stroke_weight: float = 1,
            stroke_color=(255, 255, 255),
            subdivision: int = 32
    ):
        if start_angle > stop_angle:
            stop_angle += (start_angle // (2 * np.pi)) * 2 * np.pi

        if start_angle == stop_angle:
            return

        rate = TWO_PI / subdivision

        outer_vertices = (*tuple(
            (x + r * np.cos(rad), y - r * np.sin(rad))
            for rad in np.arange(start_angle, stop_angle, rate)
        ), (x + r * np.cos(stop_angle), y - r * np.sin(stop_angle)))

        filled_polygon(
            surface,
            ((x, y), *outer_vertices),
            color
        )

        if stroke_weight == 1:
            draw.aalines(
                surface,
                stroke_color,
                False,
                outer_vertices
            )
        elif 1 < stroke_weight < r * 2:
            oradi = r + stroke_weight * 0.5
            outer_vertices = (*tuple(
                (x + oradi * np.cos(rad), y - oradi * np.sin(rad))
                for rad in np.arange(start_angle, stop_angle, rate)
            ), (x + oradi * np.cos(stop_angle), y - oradi * np.sin(stop_angle)))

            iradi = r - stroke_weight * 0.5
            inner_vertices = (*tuple(
                (x + iradi * np.cos(rad), y - iradi * np.sin(rad))
                for rad in np.arange(start_angle, stop_angle, rate)
            ), (x + iradi * np.cos(stop_angle), y - iradi * np.sin(stop_angle)))

            filled_polygon(
                surface,
                (*inner_vertices, *outer_vertices[::-1]),
                stroke_color
            )
            draw.aalines(
                surface,
                stroke_color,
                False,
                inner_vertices
            )

    @staticmethod
    def inverse_pie(
            surface: Surface,
            x: float, y: float,
            r: float, half_width: float,
            start_angle: float, stop_angle: float,
            color=(255, 255, 255),
            stroke_weight: float = 1,
            stroke_color=(255, 255, 255),
            subdivision: int = 32
    ):
        if start_angle > stop_angle:
            stop_angle += (start_angle // TWO_PI) * TWO_PI

        if start_angle == stop_angle or r >= half_width:
            return

        # Pie part
        rate = TWO_PI / subdivision

        outer_vertices = (*tuple(
            (x + r * np.cos(rad), y - r * np.sin(rad))
            for rad in np.arange(start_angle, stop_angle, rate)
        ), (x + r * np.cos(stop_angle), y - r * np.sin(stop_angle)))

        # Container part
        half_diag = np.sqrt(2) * half_width
        dx, dy = half_diag * np.cos(start_angle), half_diag * np.sin(start_angle)
        start_pos = (
            x + np.fmin(half_width, np.abs(dx)) * np.sign(dx),
            y - np.fmin(half_width, np.abs(dy)) * np.sign(dy)
        )
        dx, dy = half_diag * np.cos(stop_angle), half_diag * np.sin(stop_angle)
        stop_pos = (
            x + np.fmin(half_width, np.abs(dx)) * np.sign(dx),
            y - np.fmin(half_width, np.abs(dy)) * np.sign(dy)
        )

        rect = (
            (x + half_width, y - half_width),
            (x - half_width, y - half_width),
            (x - half_width, y + half_width),
            (x + half_width, y + half_width)
        )
        vertices = (start_pos, ) + tuple(
            rect[k % 4] for k in np.arange(
                np.ceil((start_angle - QUARTER_PI) / HALF_PI),
                np.ceil((stop_angle - QUARTER_PI) / HALF_PI),
                dtype=int
            )
        ) + (stop_pos, *outer_vertices[::-1])

        # Draw shape
        filled_polygon(
            surface,
            vertices,
            color
        )

        if stroke_weight == 1:
            draw.aalines(
                surface,
                stroke_color,
                False,
                outer_vertices
            )
        elif 1 < stroke_weight < r * 2:
            oradi = r + stroke_weight * 0.5
            outer_vertices = (*tuple(
                (x + oradi * np.cos(rad), y - oradi * np.sin(rad))
                for rad in np.arange(start_angle, stop_angle, rate)
            ), (x + oradi * np.cos(stop_angle), y - oradi * np.sin(stop_angle)))

            iradi = r - stroke_weight * 0.5
            inner_vertices = (*tuple(
                (x + iradi * np.cos(rad), y - iradi * np.sin(rad))
                for rad in np.arange(start_angle, stop_angle, rate)
            ), (x + iradi * np.cos(stop_angle), y - iradi * np.sin(stop_angle)))

            filled_polygon(
                surface,
                (*inner_vertices, *outer_vertices[::-1]),
                stroke_color
            )
            draw.aalines(
                surface,
                stroke_color,
                False,
                inner_vertices
            )

    @staticmethod
    def line(
            surface: Surface,
            start_pos: tuple[float, float],
            stop_pos: tuple[float, float],
            stroke_weight: float = 1,
            stroke_color=(255, 255, 255)
    ):
        if stroke_weight == 1:
            draw.aaline(surface, stroke_color, start_pos, stop_pos)
        elif stroke_weight > 1:
            angle = np.pi / 2 if stop_pos[0] == start_pos[0] else np.arctan((stop_pos[1] - start_pos[1]) / (stop_pos[0] - start_pos[0]))
            dx, dy = 0.5 * stroke_weight * np.sin(angle), -0.5 * stroke_weight * np.cos(angle)
            filled_polygon(surface, (
                (start_pos[0] - dx, start_pos[1] - dy),
                (start_pos[0] + dx, start_pos[1] + dy),
                (stop_pos[0] + dx, stop_pos[1] + dy),
                (stop_pos[0] - dx, stop_pos[1] - dy)
            ), stroke_color)

    @staticmethod
    def rect(
            surface: Surface,
            top_left: tuple[float, float],
            size: tuple[float, float],
            color=(255, 255, 255)
    ):
        filled_polygon(surface, (
            top_left,
            (top_left[0] + size[0], top_left[1]),
            (top_left[0] + size[0], top_left[1] + size[1]),
            (top_left[0], top_left[1] + size[1])
        ), color)
        # aapolygon(surface, (
        #     top_left,
        #     (top_left[0] + size[0], top_left[1]),
        #     (top_left[0] + size[0], top_left[1] + size[1]),
        #     (top_left[0], top_left[1] + size[1])
        # ), color)
