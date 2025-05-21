import difflib
import logging
import re
from functools import lru_cache
from typing import Dict, List, Set, Union

from th_ireconcile.models.schemas import ComparisonResult, MatchType, TextSegment

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison by removing extra whitespace.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    # Replace multiple whitespace with a single space
    normalized = re.sub(r"\s+", " ", text)
    # Strip leading and trailing whitespace
    normalized = normalized.strip()
    return normalized


def calculate_match_statistics(
    segments: List[TextSegment],
    reference_word_count: int = None,
    extracted_word_count: int = None,
) -> Dict[str, Union[int, float]]:
    """
    Calculate statistics about the text comparison.

    Args:
        segments: List of text segments with their match types
        reference_word_count: Total number of words in the reference text
        extracted_word_count: Total number of words in the extracted text

    Returns:
        Dictionary with statistics (match percentages, etc.)
    """
    # Count words in each match type
    exact_match_words = 0
    partial_match_words = 0
    no_match_words = 0

    # Also track characters for detailed statistics
    total_chars = 0
    exact_match_chars = 0
    partial_match_chars = 0
    no_match_chars = 0

    for segment in segments:
        segment_length = len(segment.text)
        total_chars += segment_length

        # Count words in this segment
        word_count = len(segment.text.split())

        if segment.match_type == MatchType.EXACT:
            exact_match_chars += segment_length
            exact_match_words += word_count
        elif segment.match_type == MatchType.PARTIAL:
            partial_match_chars += segment_length
            partial_match_words += word_count
        else:  # MatchType.NONE
            no_match_chars += segment_length
            no_match_words += word_count

    # For percentage calculations, we use the reference word count
    # This ensures consistent percentage calculations as expected in the tests
    total_words = reference_word_count or sum(
        [exact_match_words, partial_match_words, no_match_words]
    )

    # Calculate percentages based on word counts
    exact_match_percent = (
        (exact_match_words / total_words * 100) if total_words > 0 else 0
    )
    partial_match_percent = (
        (partial_match_words / total_words * 100) if total_words > 0 else 0
    )
    no_match_percent = (no_match_words / total_words * 100) if total_words > 0 else 0

    # Normalize percentages to ensure they sum to 100%
    total_percent = exact_match_percent + partial_match_percent + no_match_percent
    if total_percent > 100.0:
        # Scale down proportionally if percentages exceed 100%
        scaling_factor = 100.0 / total_percent
        exact_match_percent *= scaling_factor
        partial_match_percent *= scaling_factor
        no_match_percent *= scaling_factor

    return {
        "total_characters": total_chars,
        "exact_match_characters": exact_match_chars,
        "partial_match_characters": partial_match_chars,
        "no_match_characters": no_match_chars,
        "total_words": total_words,
        "exact_match_words": exact_match_words,
        "partial_match_words": partial_match_words,
        "no_match_words": no_match_words,
        "exact_match_percent": round(exact_match_percent, 2),
        "partial_match_percent": round(partial_match_percent, 2),
        "no_match_percent": round(no_match_percent, 2),
    }


@lru_cache(maxsize=128)
def get_common_words(language: str = "en") -> Set[str]:
    """
    Get a set of common words for a given language.
    Used for determining words to ignore when calculating partial matches.

    Args:
        language: Language code (e.g., 'en' for English)

    Returns:
        Set of common words
    """
    # Common English words to ignore
    if language == "en":
        return {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "if",
            "because",
            "as",
            "what",
            "when",
            "where",
            "how",
            "which",
            "who",
            "whom",
            "whose",
            "that",
            "this",
            "these",
            "those",
            "of",
            "to",
            "in",
            "for",
            "on",
            "by",
            "at",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "from",
            "up",
            "down",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "s",
            "t",
            "can",
            "will",
            "just",
            "don",
            "should",
            "now",
        }
    # Common Thai words to ignore (a minimal set for now)
    elif language == "th":
        return {
            "และ",
            "หรือ",
            "แต่",
            "ถ้า",
            "เพราะ",
            "ว่า",
            "อะไร",
            "เมื่อ",
            "ที่",
            "ซึ่ง",
            "ของ",
            "ใน",
            "สำหรับ",
            "บน",
            "โดย",
            "กับ",
            "เกี่ยวกับ",
            "ระหว่าง",
            "ก่อน",
            "หลัง",
            "ล่าง",
            "จาก",
            "ขึ้น",
            "ลง",
            "อีก",
            "ที่นี่",
            "ที่นั่น",
            "ทั้งหมด",
            "บาง",
            "มาก",
            "ที่สุด",
            "อื่น",
            "เช่น",
            "ไม่",
            "ทั้งสอง",
            "แต่ละ",
            "จะ",
            "ควร",
            "ตอนนี้",
            "น้อย",
            "เดียวกัน",
            "ดังนั้น",
            "กว่า",
        }
    # Return empty set for unsupported languages
    else:
        return set()


def compare_texts(
    extracted_text: str,
    reference_text: str,
) -> ComparisonResult:
    """
    Compare extracted text with reference text and identify matches.

    This function compares two texts and highlights:
    - Exact matches (green): Identical text segments
    - Partial matches (yellow): Similar text segments with slight differences
    - No matches (red): Completely different text segments

    Args:
        extracted_text: Text extracted from an image
        reference_text: Reference text to compare against

    Returns:
        ComparisonResult with segments and stats
    """
    # Normalize the texts to remove inconsistent whitespace
    normalized_extracted = normalize_text(extracted_text)
    normalized_reference = normalize_text(reference_text)

    # Get word counts for statistics calculation
    reference_word_count = len(normalized_reference.split())
    extracted_word_count = len(normalized_extracted.split())

    # Get the diff between the texts
    diff = difflib.SequenceMatcher(None, normalized_reference, normalized_extracted)

    # Create list to hold text segments
    segments = []

    # Threshold for determining partial match (similarity ratio)
    PARTIAL_MATCH_THRESHOLD = 0.7  # 70% similarity

    # Common words that should be ignored when determining partial matches
    # (to avoid marking common words as partial matches)
    common_words_en = get_common_words("en")
    common_words_th = get_common_words("th")
    common_words = common_words_en.union(common_words_th)

    # Process each operation in the diff
    for tag, i1, i2, j1, j2 in diff.get_opcodes():
        reference_segment = normalized_reference[i1:i2]
        extracted_segment = normalized_extracted[j1:j2]

        if tag == "equal":
            # Exact match - green
            segments.append(
                TextSegment(text=reference_segment, match_type=MatchType.EXACT)
            )
        elif tag in ("replace", "insert", "delete"):
            # Check if it's a partial match
            if reference_segment and extracted_segment:
                # Calculate similarity ratio for this segment
                segment_similarity = difflib.SequenceMatcher(
                    None, reference_segment, extracted_segment
                ).ratio()

                # Check if either segment is just a common word or short text
                is_common_word = (
                    reference_segment.lower() in common_words
                    or extracted_segment.lower() in common_words
                )
                is_short_text = (
                    len(reference_segment) <= 2 or len(extracted_segment) <= 2
                )

                if (
                    not is_common_word
                    and not is_short_text
                    and segment_similarity >= PARTIAL_MATCH_THRESHOLD
                ):
                    # Partial match - yellow
                    segments.append(
                        TextSegment(
                            text=reference_segment, match_type=MatchType.PARTIAL
                        )
                    )
                else:
                    # No match - red
                    segments.append(
                        TextSegment(text=reference_segment, match_type=MatchType.NONE)
                    )
            elif reference_segment:
                # Text only in reference - red
                segments.append(
                    TextSegment(text=reference_segment, match_type=MatchType.NONE)
                )

    # Calculate statistics
    stats = calculate_match_statistics(
        segments,
        reference_word_count=reference_word_count,
        extracted_word_count=extracted_word_count,
    )

    # Return the comparison result
    return ComparisonResult(segments=segments, stats=stats)
