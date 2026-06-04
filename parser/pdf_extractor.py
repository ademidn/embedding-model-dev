from pathlib import Path
import fitz
from loguru import logger
from tqdm import tqdm


class PDFExtractor:
	def __init__(self, pdf_path: str):
		self.pdf_path = Path(pdf_path)

		if not self.pdf_path.exists():
			raise FileNotFoundError(
				f"PDF file not found: {self.pdf_path}"
			)

	# Page preview detection
	# Block di pojok kanan bawah dianggap page preview dan dibuang
	# Threshold berbasis ratio halaman digunakan agar tidak tergantung ukuran PDF:
	# - x_ratio > 0.55: area kanan 
	# - y_ratio > 0.85: area bawah
	# Kedua kondisi harus terpenuhi sekaligus agar bisa dibuang
	
	def _is_page_preview(
			self,
			x0: float,
			y0: float,
			page_width: float,
			page_height: float,
	) -> bool:
		x_ratio = x0 / page_width
		y_ratio = y0 / page_height

		return x_ratio > 0.55 and y_ratio > 0.85

	def extract_text(self) -> str:
		"""
		Extract raw text dari PDF tanpa cleaning.
		Page preview blocks dikeluarkan.
		"""

		logger.info(f"Opening PDF: {self.pdf_path.name}")

		document = fitz.open(self.pdf_path)

		text_parts = []

		for page_num in tqdm(range(len(document)), desc="Extracting pages"):
			page = document.load_page(page_num)

			page_width = page.rect.width
			page_height = page.rect.height

			text_parts.append(
				f"\n\n===== PAGE {page_num + 1} =====\n\n"
			)

			blocks = page.get_text("blocks")

			# Sort by vertical position (top to bottom)
			blocks.sort(key=lambda b: b[1])

			for block in blocks:
				x0, y0, x1, y1, text, *_ = block

				if self._is_page_preview(x0, y0, page_width, page_height):
					logger.debug(
						f"Page {page_num + 1}: skipped preview block"
						f"x0={x0:.1f} y0={y0:.1f} | {repr(text[:40])}"
					)
					continue

				text_parts.append(text)
		
		document.close()

		return "".join(text_parts)

	def save_text(self, output_path: str) -> None:
		"""
		Extract and save text into txt file.
		"""

		output_path = Path(output_path)

		output_path.parent.mkdir(parents=True, exist_ok=True)

		text = self.extract_text()

		output_path.write_text(text, encoding="utf-8")

		logger.success(
			f"Text saved to: {output_path}"
		)


if __name__ == "__main__":
	extractor = PDFExtractor(
		pdf_path="regulation/raw/uu/uu_32_2009_pplh.pdf"
	)

	extractor.save_text(
		output_path="regulation/extracted/uu/uu_32_2009_pplh.txt"
	)