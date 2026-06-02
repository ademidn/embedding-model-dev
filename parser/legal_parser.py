from pathlib import Path
import re
from loguru import logger
from parser.schemas import Article


class LegalParser:

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
    
    CHAPTER_PATTERN = re.compile(
        r"^BAB\s+([IVXLCDM]+)\s*$",
        re.MULTILINE
    )

    ARTICLE_PATTERN = re.compile(
        r"^Pasal\s+(\d+[A-Z]?)\s*$",
        re.MULTILINE
    )


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
                id=f"uu_32_2009_pplh_art_{article_number}",

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


    def parse(self, text: str):

        chapters = self.extract_chapters(text)

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

        logger.info(f"Parsed {len(articles)} articles")

        return articles
