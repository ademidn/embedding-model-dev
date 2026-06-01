from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Paragraph(BaseModel):
    paragraph_number: str
    text: str


class BaseLegalObject(BaseModel):
    id: str

    object_type: str

    document_type: str
    document_number: str
    document_year: int = Field(ge=1945, le=2100)

    document_title: str

    source_pages: List[int] = Field(default_factory=list)

    topic_tags: List[str] = Field(default_factory=list)

    embedding_text: str
    raw_text: str


class Definition(BaseLegalObject):
    object_type: Literal["definition"] = "definition"

    term: str

    article_number: str
    definition_number: str

    chapter_number: Optional[str] = None
    chapter_title: Optional[str] = None


class Article(BaseLegalObject):
    object_type: Literal["article"] = "article"

    article_number: str

    chapter_number: Optional[str] = None
    chapter_title: Optional[str] = None

    section_number: Optional[str] = None
    section_title: Optional[str] = None

    paragraphs: List[Paragraph] = Field(default_factory=list)


class Explenation(BaseLegalObject):
    object_type: Literal["explanation"] = "explanation"

    related_article: str


class AttachmentNarrative(BaseLegalObject):
    object_type: Literal["attachment_narrative"] = ("attachment_narrative")

    attachment_number: str
    attachment_title: str


class AttachmentTable(BaseLegalObject):
    object_type: Literal["attachment_table"] = ("attachment_table")

    attachment_number: str
    attachment_title: str

    table_markdown: str
    table_json: dict


class AttachmentDiagram(BaseLegalObject):
    object_type: Literal["attachment_diagram"] = ("attachment_diagram")

    attachment_number: str
    attachment_title: str
