import datetime
from pathlib import Path
from urllib.request import urlopen
import pytest
import json
import re


def test_transcript_object():
    """Test if transcript object is created correctly."""
    from app.transcriber.alignment import Transcript  # pylint: disable=C0415

    test_transcript_path = Path("test_data/pydata/transcript.json")
    transcript_dict = json.load(test_transcript_path.open())

    transcript = Transcript(test_transcript_path)

    assert len(transcript) > 0
    assert transcript.tokens[-1][-1] == transcript_dict["segments"][-1]["text"][-1]
    assert transcript.tokens[0][0] == transcript_dict["segments"][0]["text"][0]
    assert transcript.as_segment[0] == 0
    assert transcript.as_first_token[0] == 0
    assert transcript.as_segment[-1] == len(transcript_dict["segments"]) - 1

    transcript_from_dict = Transcript(transcript_dict)

    assert transcript_from_dict.tokens == transcript.tokens
    assert transcript_from_dict.as_segment == transcript.as_segment
    assert transcript_from_dict.as_first_token == transcript.as_first_token


def test_markdown_object():
    """Test if markdown object is created correctly."""
    from app.transcriber.alignment import MarkdownResponse  # pylint: disable=C0415

    test_markdown_path = Path("test_data/pydata/result.md")
    markdown_str = test_markdown_path.open().read()

    markdown = MarkdownResponse(test_markdown_path)

    assert len(markdown) > 0
    assert markdown.tokens[-1][-1] == markdown_str[-1]
    assert markdown.tokens[0][0] == markdown_str[0]
    assert markdown.as_paragraph[0] == 0
    assert markdown.as_paragraph[-1] == len(markdown_str.split("\n\n")) - 1

    markdown_from_str = MarkdownResponse(markdown_str)

    assert markdown_from_str.tokens == markdown.tokens
    assert markdown_from_str.as_paragraph == markdown.as_paragraph
    assert markdown_from_str.is_header == markdown.is_header
    
def test_markdown_list():
    """Test if markdown object is created correctly."""
    from app.transcriber.alignment import MarkdownResponse  # pylint: disable=C0415

    markdown_str = "1. First-item pos\n  - level Second-item\n3. Third item"
    markdown = MarkdownResponse(markdown_str)
    assert markdown.tokens[0] == "1. ", markdown.tokens[0]
    assert markdown.tokens[4] == "\n  - ", markdown.tokens[4]
    


@pytest.mark.parametrize(
    "test_input,remove_header",
    [
        ("Great! Here's the text in markdown format:", True),
        ("Great! Here's the text in Markdown format:", True),
        ("Here's the text in Markdown format:", True),
        ("Here's the text in markdown format:", True),
        ("Great! Here's the text formatted in Markdown:", True),
        ("Here is the text in markdown format:", True),
        (
            "Great! Here's the text in Markdown format with headings and paragraphs separated by two carriage returns:",
            True,
        ),
        ("Sure, here's the text in markdown format:", True),
        ("## GPT-3 Tools", False),
        ("## Smart Lectures", False),
        ("Some random text for test it", False),
    ],
)
def test_markdown_object_skip_prompt(test_input, remove_header):
    """Test if header is removed from markdown string."""
    from app.transcriber.alignment import MarkdownResponse  # pylint: disable=C0415

    clean_str = "### Header of content\n\nParagraph 1\n\nParagraph 2 last"
    markdown_str = test_input + "\n\n" + clean_str
    formatted = MarkdownResponse(markdown_str)
    assert formatted.tokens[-1] == "last"
    assert clean_str.startswith("".join(formatted.tokens[:3])) == remove_header
    assert test_input.startswith("".join(formatted.tokens[:3])) != remove_header


synthetic_transcript_dict = {
    "segments": [
        {
            "text": "Replace with header. One, two: three, four. Five, six. Seven, eight. Nine, ten.",
            "start": 0.0,
            "end": 10.0,
        },
        {
            "text": "Eleven, twelve, thirteen, fourteen, fifteen! sixteen, seventeen! Eighteen, nineteen, twenty.",
            "start": 11.0,
            "end": 20.0,
        },
        {
            "text": "Twenty-one, twenty-two, twenty-three, twenty-four, twenty-five. Twenty-six, twenty-seven. Twenty-eight, twenty-nine, thirty,",
            "start": 21.0,
            "end": 30.0,
        },
        {
            "text": "Thirty-one: thirty-two, thirty-three, thirty-four, thirty-five! thirty-six! Thirty-seven, thirty-eight, thirty-nine, forty.",
            "start": 31.0,
            "end": 40.0,
        },
        {
            "text": "Forty-one, forty-two, forty-three, forty-four, forty-five. Replace with header. Forty-six, forty-seven, forty-eight, forty-nine, fifty.",
            "start": 41.0,
            "end": 50.0,
        },
    ]
}
synthetic_transcript_dict = {
    "segments": [
        {
            "text": "Replace with header. One, two, three four five. ",
            "start": 0.0,
            "end": 5.0,
        },
        {
            "text": " Six seven. Eight nine, Ten ",
            "start": 6.0,
            "end": 10.0,
        },
        {
            "text": " eleven, Twelve thirteen. Fourteen, fifteen!",
            "start": 11.0,
            "end": 15.0,
        },
        {
            "text": " Sixteen, seventeen! Eighteen, nineteen, twenty.",
            "start": 16.0,
            "end": 20.0,
        },
        {
            "text": " Twenty-one, twenty-two, ",
            "start": 21.0,
            "end": 22.0,
        },
        {
            "text": " twenty-three, twenty-four, twenty-five ",
            "start": 23.0,
            "end": 25.0,
        },
        {
            "text": " twenty-six, twenty-seven. Twenty-eight, twenty-nine, thirty,",
            "start": 26.0,
            "end": 30.0,
        },
        {
            "text": " Thirty-one: thirty-two thirty-three, thirty-four thirty-five, ",
            "start": 31.0,
            "end": 35.0,
        },
        {
            "text": " thirty-six thirty-seven, thirty-eight ",
            "start": 35.0,
            "end": 38.0,
        },
        {
            "text": " thirty-nine, forty ",
            "start": 39.0,
            "end": 40.0,
        },
        {
            "text": " forty-one forty-two. Forty-three forty-four! Forty-five. Replace with header. Forty-six, forty-seven, forty-eight, forty-nine, fifty.",
            "start": 41.0,
            "end": 50.0,
        },
    ]
}
replacements = [
    ("thirteen", "13"),
    ("nineteen", "19"),
    ("twenty-three", "23"),
    ("twenty-nine", "29"),
    ("thirty-three", "33"),
    ("thirty-nine", "39"),
    ("forty-three", "43"),
    ("forty-nine", "49"),
    ("Ten","**Ten**"),
    ("twenty-five","**twenty-five**"),
    ("forty","__forty__"),
    
]


def update_synthetic_block(current_block, step):
    current_block = current_block.replace(
        "Replace with header. ", "\n\n## Replace with header\n"
    )
    current_block = current_block.replace("!", "\n\n## Next header\n")
    current_block = current_block.replace(".", ".\n\n")
    current_block = current_block.strip("\n ")
    bullets = current_block.find(":")+1
    if bullets > 0:
        end = re.search(r"[\.!?]", current_block[bullets:])
        end = end.end() if end else len(current_block)
        end += bullets
        current_block = (
            current_block[:bullets]
            + "\n\n-"
            + current_block[bullets:end].replace(",", "\n-")
            + "\n\n"
            + current_block[end:]
        )
    if step // 2 != 0:
        current_block = "Sure, here's the text in markdown format:\n\n" + current_block

    for text, replacement in replacements:
        current_block = current_block.replace(text, str(replacement))
    current_block = re.sub(r"\s*\n{2,}\s?", "\n\n", current_block)
    # current_block = current_block.replace("\n"*4, "\n"*2)
    return current_block


def test_alignment():
    from app.transcriber.alignment import (  # pylint: disable=C0415
        Transcript,
        MarkdownResponse,
        Aligner,
    )

    block_size = 40
    block_delta = 13
    context_size = 20
    only_text_context_size = 15

    transcript = Transcript(synthetic_transcript_dict)

    aligner = Aligner(
        transcript,
        block_size=block_size,
        block_delta=block_delta,
        context_size=context_size,
        only_text_context_size=only_text_context_size,
    )

    current_block = aligner.first_block()
    print(current_block)
    context_elements = current_block[-5:].strip()
    step = 0
    while current_block:
        print("=" * 20)
        print(current_block)
        initial_block = MarkdownResponse(current_block)
        assert len(initial_block) <= block_size + block_delta + 3
        assert len(initial_block) >= block_size - block_delta-3 or aligner.is_last_block()
        assert current_block.find(context_elements) >= 0

        current_block = update_synthetic_block(current_block, step)
        print(">" + "-" * 19)
        print(current_block)
        formatted = MarkdownResponse(current_block)
        context_elements = formatted.get_markdown_str(-3).strip()

        current_block = aligner.push(formatted)
        step += 1
    result = aligner.get_result()
    print(result)
    assert result.startswith("## Replace with header")
    assert result.find("fifty.") > 0

    word_count = 0
    missing_words = 0
    continue_missing = 0
    for segment in synthetic_transcript_dict["segments"]:
        for token in re.split(r"[^\w-]+", segment["text"]):
            if result.find(token) < 0:
                missing_words += 1
                continue_missing += 1
            else:
                continue_missing = 0
            assert continue_missing < 3
            word_count += 1
    assert missing_words / word_count < 0.21

    for par in result.split("\n\n"):
        if not par.startswith("#"):
            assert par.find("##") < 0, par
            assert par.find("markdown") < 0, par
            assert (
                not re.match(r"^(\s*(?:[-\*\+]|\d+\.) )?(\{~\d+(\.\d+)?\}).*(\{~\d+(\.\d+)?\})$", par,re.S) is None
            ), par


def test_long_text_alignment():
    from app.transcriber.alignment import (  # pylint: disable=C0415
        Transcript,
        MarkdownResponse,
        Aligner,
    )
    transcript_path = Path("test_data/long_text/transcript.json")
    transcript = Transcript(transcript_path)
    formatted_path = Path("test_data/long_text/0_0_834_result.md")
    formatted = MarkdownResponse(formatted_path)
    aligner = Aligner(
        transcript=transcript,
        block_size=1200,
        block_delta=400,
        context_size=400,
        only_text_context_size=200,
    )
    block =  aligner.first_block()
    #assert aligner.current_block_end == 834
    next_block = aligner.push(formatted)
    result = aligner.get_result()
    print(result)
    #assert result.startswith("## Replace with header")
    
    
    