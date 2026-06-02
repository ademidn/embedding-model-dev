from pathlib import Path
import re

from loguru import logger


class TextCleaner:
    def __init__(self):
        pass

    def clean(self, text: str) -> str:
        """
        Apply safe cleaning rules.
        """

        # ---
        # Remove website footer
        # ---
        text = re.sub(
            r"www\.hukumonline\.com",
            "",
            text,
            flags=re.IGNORECASE
        )

        # ---
        # Remove page markers from extractor
        # ---
        text = re.sub(
            r"===== PAGE \d+ =====",
            "",
            text,
        )

        # ---
        # Remove page numbers
        # ---
        text = re.sub(
            r"-\s*\d+\s*-",
            "",
            text,
        )

        # ---
        # Remove common headers
        # PRESIDEN REPUBLIK INDONESIA
        # ---
        text = re.sub(
            r"PRESIDEN\s+REPUBLIK\s+INDONESIA",
            "",
            text,
            flags=re.IGNORECASE
        )

        # ---
        # Normalize spaces
        # ---
        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        # ---
        # Remove trailing spaces
        # ---
        lines = [line.strip() for line in text.splitlines()]

        text = "\n".join(lines)

        # ---
        # Max 2 blank lines
        # ---
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()
    
    def clean_file(self, input_path: str, output_path: str) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)

        logger.info(f"Cleaning: {input_path.name}")

        text = input_path.read_text(encoding="utf-8")

        cleaned_text = self.clean(text)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(cleaned_text, encoding="utf-8")

        logger.success(f"Saved: {output_path}")


if __name__ == "__main__":
    cleaner = TextCleaner()

    cleaner.clean_file(
        input_path="regulation/extracted/uu/uu_32_2009_pplh.txt",
        output_path="regulation/cleaned/uu/uu_32_2009_pplh_clean.txt"
    )