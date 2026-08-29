"""
src/rag_engine/youtube_loader.py

YouTube Video and Media Ingestion engine for PragyanAI College Intelligence Hub.
Extracts transcripts, parses timestamped chapters for CoE Labs & Campus Walkthroughs,
and formats them as searchable LangChain Document chunks.
"""

import re
from typing import Any, Dict, List, Optional
from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeMediaLoader:
    """Fetches, parses, and chunks YouTube video transcripts for departmental tours."""

    @staticmethod
    def extract_video_id(url_or_id: str) -> Optional[str]:
        """Extracts standard 11-character YouTube video ID from various URL formats."""
        if len(url_or_id) == 11 and not ("/" in url_or_id or "?" in url_or_id):
            return url_or_id

        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
            r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
            r"(?:embed\/)([0-9A-Za-z_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        return None

    @classmethod
    def load_transcript(
        cls,
        youtube_url: str,
        college_code: str = "CAMPUS",
        title: str = "Campus Lab Tour",
    ) -> List[Document]:
        """Retrieves video captions with timestamps and segments them into 60-second chunks."""
        video_id = cls.extract_video_id(youtube_url)
        if not video_id:
            return []

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception:
            # Gracefully handle missing transcripts or disabled captions
            return []

        documents: List[Document] = []
        current_chunk_text = []
        chunk_start_time = 0.0

        for entry in transcript_list:
            text = entry.get("text", "").strip()
            start = entry.get("start", 0.0)

            if not current_chunk_text:
                chunk_start_time = start

            current_chunk_text.append(text)

            # Segment every ~60 seconds of video narration
            if (start - chunk_start_time) >= 60.0:
                full_text = " ".join(current_chunk_text)
                minutes = int(chunk_start_time // 60)
                seconds = int(chunk_start_time % 60)
                timestamp_str = f"{minutes:02d}:{seconds:02d}"

                documents.append(
                    Document(
                        page_content=f"[{timestamp_str}] {full_text}",
                        metadata={
                            "source": f"YouTube Video: {title}",
                            "url": f"https://www.youtube.com/watch?v={video_id}&t={int(chunk_start_time)}s",
                            "video_id": video_id,
                            "timestamp": timestamp_str,
                            "college_code": college_code,
                            "file_type": "Video Transcript",
                        },
                    )
                )
                current_chunk_text = []

        # Flush remaining transcript tail
        if current_chunk_text:
            full_text = " ".join(current_chunk_text)
            minutes = int(chunk_start_time // 60)
            seconds = int(chunk_start_time % 60)
            timestamp_str = f"{minutes:02d}:{seconds:02d}"

            documents.append(
                Document(
                    page_content=f"[{timestamp_str}] {full_text}",
                    metadata={
                        "source": f"YouTube Video: {title}",
                        "url": f"https://www.youtube.com/watch?v={video_id}&t={int(chunk_start_time)}s",
                        "video_id": video_id,
                        "timestamp": timestamp_str,
                        "college_code": college_code,
                        "file_type": "Video Transcript",
                    },
                )
            )

        return documents
