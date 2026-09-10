from __future__ import annotations

from pathlib import Path

import numpy as np
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


class BingoBoardPdf:
    def __init__(self, board_name: str, has_free_space: bool):
        self.board_name = board_name
        self.has_free_space = has_free_space

    def render(
        self,
        board: np.ndarray,
        name: str,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pdf = canvas.Canvas(str(output_path), pagesize=A4)

        page_width, page_height = A4

        # Title
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawCentredString(
            page_width / 2,
            page_height - 80,
            self.board_name,
        )

        # Person's name
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(
            page_width / 2,
            page_height - 115,
            name,
        )

        # Board dimensions
        rows, cols = board.shape

        margin = 40
        top = page_height - 150
        board_width = page_width - 2 * margin
        board_height = board_width * rows / cols

        cell_width = board_width / cols
        cell_height = board_height / rows

        # Draw cells
        for row in range(rows):
            for col in range(cols):
                x = margin + col * cell_width
                y = top - (row + 1) * cell_height

                if self.has_free_space and row == rows // 2 and col == cols // 2:
                    pdf.setFillColor(colors.lightgrey)
                    pdf.rect(
                        x,
                        y,
                        cell_width,
                        cell_height,
                        fill=1,
                        stroke=1,
                    )
                    pdf.setFillColor(colors.black)
                else:
                    pdf.rect(
                        x,
                        y,
                        cell_width,
                        cell_height,
                        fill=0,
                        stroke=1,
                    )

                self._draw_cell_text(
                    pdf,
                    str(board[row, col]),
                    x,
                    y,
                    cell_width,
                    cell_height,
                )

        pdf.save()

    def _draw_cell_text(
        self,
        pdf: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        for font_size in (10, 9, 8, 7):
            style = ParagraphStyle(
                name="CellText",
                fontName="Helvetica",
                fontSize=font_size,
                leading=font_size * 1.2,
                alignment=TA_CENTER,
                textColor=colors.black,
            )

            paragraph = Paragraph(text, style)
            text_width, text_height = paragraph.wrap(
                width - 12,
                height - 12,
            )

            if text_height <= height - 12:
                break

        paragraph.drawOn(
            pdf,
            x + (width - text_width) / 2,
            y + (height - text_height) / 2,
        )
