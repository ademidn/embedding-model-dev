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

	def extract_text(self) -> str:
		"""
		Extract raw text from PDF without any cleaning.
		"""

		logger.info(f"Opening PDF: {self.pdf_path.name}")

		document = fitz.open(self.pdf_path)

		text_parts = []

		for page_num in tqdm(range(len(document)), desc="Extracting pages"):
			page = document.load_page(page_num)

			page_text = page.get_text()

			text_parts.append(
				f"\n\n===== PAGE {page_num + 1} =====\n\n"
			)

			text_parts.append(page_text)
		
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
	extractor = PDFextractor(
		pdf_path="regulation/raw/pp/pp_22_2021_pplh.pdf"
	)

	extractor.save_text(
		output_path="regulation/extracted/pp/pp_22_2021_pplh.txt"
	)