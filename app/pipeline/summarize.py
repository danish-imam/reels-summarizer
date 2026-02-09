"""Summarize transcript. Uses free extractive summarization (sumy) by default."""

import logging

import nltk
from sumy.nlp.tokenizers import Tokenizer

logger = logging.getLogger(__name__)
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer

# Ensure NLTK sentence tokenizer is available (required for sumy)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def summarize_transcript(transcript: str) -> str:
    """Summarize transcript using free extractive summarization (LexRank)."""
    if not transcript or transcript.strip() == "[No speech detected]":
        logger.debug("Skipping summary: no speech detected")
        return "No speech to summarize."

    transcript = transcript.strip()
    words = transcript.split()
    if len(words) < 30:
        logger.debug("Transcript too short (%d words), returning as-is", len(words))
        return transcript

    try:
        parser = PlaintextParser.from_string(transcript, Tokenizer("english"))
        num_sentences = len(list(parser.document.sentences))
        if num_sentences < 3:
            logger.debug("Too few sentences (%d), returning as-is", num_sentences)
            return transcript

        # Use 5–7 sentences for long reels; cap at ~30% of document
        count = min(max(5, num_sentences // 3), num_sentences, 10)
        summarizer = LexRankSummarizer()
        sentences = summarizer(parser.document, sentences_count=count)
        summary = " ".join(str(s) for s in sentences)
        if summary and len(summary.split()) < len(words) * 0.9:
            logger.debug("Summary extracted (%d -> %d words)", len(words), len(summary.split()))
            return summary.strip()
        logger.debug("Summary too similar to transcript, returning original")
        return transcript
    except Exception as e:
        logger.warning("Summarization failed, returning transcript: %s", e)
        return transcript
