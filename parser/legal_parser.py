from pathlib import Path
import re
from loguru import logger
from parser.schemas import Article


class LegalParser:

    CHAPTER_PATTERN = re.compile(
        r"^BAB\s+([IVXLCDM]+)\s*$",
        re.MULTILINE
    )

    ARTICLE_PATTERN = re.compile(
        r"^Pasal[ \t]+(\d+[A-Z]?)\s*$",
        re.MULTILINE
    )

    GENERAL_EXPLANATION_PATTERN = re.compile(
        r"PENJELASAN\s+ATAS",
        re.IGNORECASE
    )

    ARTICLE_EXPLANATION_PATTERN = re.compile(
        r"II\.\s*PASAL\s+DEMI\s+PASAL",
        re.IGNORECASE
    )

    def __init__(
            self,
            document_type: str,
            document_number: str,
            document_year: int,
            document_title: str,
    ):
        self.document_type = document_type
        self.document_number = document_number
        self.document_year = document_year
        self.document_title = document_title

        self.document_id = (
            f"{document_type.lower()}_{document_number}_{document_year}"
        )

    # Document Splitter

    def split_document(self, text: str):

        # Jika tidak ada bagian penjelasan
        general_match = (
            self.GENERAL_EXPLANATION_PATTERN.search(text)
        )

        if not general_match:
            return {
                "body": text,
                "general_explanation": None,
                "article_explanation": None,
            }
        
        # Jika hanya ada penjelasan umum
        body_text = text[:general_match.start()].strip()

        explanation_text = text[general_match.start():].strip()

        article_match = (
            self.ARTICLE_EXPLANATION_PATTERN.search(explanation_text)
        )

        if not article_match:
            return {
                "body": body_text,
                "general_explanation": explanation_text,
                "article_explanation": None,
            }
        
        # Jika ada penjelasan umum dan pasal demi pasal
        general_explanation = explanation_text[:article_match.start()].strip()

        article_explanation = explanation_text[article_match.start():].strip()

        return {
            "body": body_text,
            "general_explanation": general_explanation,
            "article_explanation": article_explanation,
        }

    # Chapter Extraction

    def extract_chapters(self, text: str):

        matches = list(self.CHAPTER_PATTERN.finditer(text))

        chapters = []

        for i, match in enumerate(matches):
            start = match.start()

            end = (
                matches[i + 1].start()
                if i < len(matches) - 1
                else len(text)
            )

            chapter_number = match.group(1)

            chapter_content = text[start:end]

            lines = chapter_content.splitlines()

            chapter_title = ""

            for line in lines[1:10]:
                line = line.strip()

                if (
                    line
                    and not line.startswith("Pasal")
                ):
                    chapter_title = line
                    break
            
            chapters.append(
                {
                    "number": chapter_number,
                    "title": chapter_title,
                    "content": chapter_content,
                }
            )

        return chapters
    
    # Article Extraction

    def extract_articles(
            self,
            chapter_number: str,
            chapter_title: str,
            chapter_content: str,
    ):
        matches = list(
            self.ARTICLE_PATTERN.finditer(chapter_content)
        )

        articles = []

        for i, match in enumerate(matches):
            start = match.start()

            end = (
                matches[i + 1].start()
                if i < len(matches) - 1
                else len(chapter_content)
            )

            article_text = chapter_content[start:end].strip()

            article_number = match.group(1)

            embedding_text = f"""
            Dokumen: {self.document_title}
            Bab {chapter_number}: {chapter_title}
            Pasal {article_number}
            {article_text}
            """.strip()

            article = Article(
                id=f"{self.document_id}_art_{article_number}",

                document_id=self.document_id,

                document_type=self.document_type,
                document_number=self.document_number,
                document_year=self.document_year,
                document_title=self.document_title,

                article_number=article_number,

                chapter_number=chapter_number,
                chapter_title=chapter_title,

                embedding_text=embedding_text,
                raw_text=article_text,
            )

            articles.append(article)
        
        return articles

    # Body Parser

    def parse_body(self, body_text: str):

        chapters = self.extract_chapters(body_text)

        articles = []

        for chapter in chapters:
            chapter_articles = (
                self.extract_articles(
                    chapter_number=chapter["number"],
                    chapter_title=chapter["title"],
                    chapter_content=chapter["content"],
                )
            )

            articles.extend(chapter_articles)

        return articles
    
    # Main Parser

    def parse(self, text: str):
        split_result = self.split_document(text)

        body_text = split_result["body"]

        general_explanation = split_result["general_explanation"]

        article_explanation = split_result["article_explanation"]

        articles = self.parse_body(body_text)

        logger.info(f"Parsed {len(articles)} articles")
        logger.info(f"General explanation found: {general_explanation is not None}")
        logger.info(f"Article explanation found: {article_explanation is not None}")

        return {
            "articles": articles,
            "general_explanation": general_explanation,
            "article_explanation": article_explanation,
        }
