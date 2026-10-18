
import re
import string


def normalize_text(text):
    """Normalize text for reliable, case-insensitive comparisons."""
    if not text:
        return ""

    text = text.lower()
    text = text.translate(
        str.maketrans("", "", string.punctuation)
    )
    return " ".join(text.split())


def split_sentences(text):
    """Split contract text into individual sentences."""
    if not text or not text.strip():
        return []

    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def quote_is_verified(quote, agreement):
    """Return True only if the quoted text exists in the agreement."""
    if not quote or not agreement:
        return False

    normalized_quote = normalize_text(quote)
    normalized_agreement = normalize_text(agreement)

    if not normalized_quote:
        return False

    return normalized_quote in normalized_agreement


def find_explicit_exclusion(agreement, request):
    """
    Find a contract sentence explicitly excluding a requested feature.

    This is a simple rule-based check, not a legal interpretation.
    """
    if not agreement or not request or not request.strip():
        return ""

    sentences = split_sentences(agreement)

    exclusion_phrases = [
        "not included",
        "excluded",
        "out of scope",
        "not covered",
        "will not include",
        "does not include",
        "isn't included",
        "is not part of",
        "outside the scope",
    ]

    request_words = set(normalize_text(request).split())

    # Ignore generic request words that don't identify a feature.
    generic_words = {
        "please", "add", "include", "implement", "make",
        "build", "create", "need", "want", "the", "a",
        "an", "to", "for", "in", "on", "with", "and",
        "my", "this", "that", "feature", "support",
    }
    feature_words = request_words - generic_words

    if not feature_words:
        return ""

    for sentence in sentences:
        normalized_sentence = normalize_text(sentence)

        has_exclusion = any(
            phrase in normalized_sentence
            for phrase in exclusion_phrases
        )

        if not has_exclusion:
            continue

        sentence_words = set(normalized_sentence.split())

        if feature_words.intersection(sentence_words):
            return sentence

    return ""


def find_explicit_inclusion(agreement, request):
    """
    Find a contract sentence explicitly including a requested feature.

    This is a basic keyword matcher. Review the returned evidence
    before making a business decision.
    """
    if not agreement or not request or not request.strip():
        return ""

    sentences = split_sentences(agreement)

    inclusion_phrases = [
        "includes",
        "included",
        "will include",
        "will provide",
        "will deliver",
        "shall provide",
        "shall include",
        "is part of",
        "covered by",
    ]

    request_words = set(normalize_text(request).split())

    generic_words = {
        "please", "add", "include", "implement", "make",
        "build", "create", "need", "want", "the", "a",
        "an", "to", "for", "in", "on", "with", "and",
        "my", "this", "that", "feature", "support",
    }
    feature_words = request_words - generic_words

    if not feature_words:
        return ""

    for sentence in sentences:
        normalized_sentence = normalize_text(sentence)

        has_inclusion = any(
            phrase in normalized_sentence
            for phrase in inclusion_phrases
        )

        if not has_inclusion:
            continue

        # Avoid treating explicitly excluded items as included.
        exclusion_phrases = [
            "not included",
            "excluded",
            "out of scope",
            "not covered",
            "will not include",
            "does not include",
        ]

        if any(
            phrase in normalized_sentence
            for phrase in exclusion_phrases
        ):
            continue

        sentence_words = set(normalized_sentence.split())

        if feature_words.intersection(sentence_words):
            return sentence

    return ""
