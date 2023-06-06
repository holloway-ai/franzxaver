from pathlib import Path
import re
import json
from typing import List
import Levenshtein as lev

re_tokens = re.compile(r"([~\w'-]+|[.,\?!])")


class Transcript:
    """Class to work with transcript files. Tokenize results of Whisper.
    tokens: list of tokens including punctuation and spaces
    segments: list of segments
    as_segment: returns segments associated with token number
    as_first_token: returns token index associated with segment number
    """

    def __init__(self, transcript):
        self.tokens = []
        self.as_segment = []
        self.as_first_token = {}
        self.segments = None
        if isinstance(transcript, Path):
            self.load(transcript)
        elif isinstance(transcript, str):
            self.load(Path(transcript))
        elif isinstance(transcript, dict):
            self.load_dict(transcript)
        else:
            raise TypeError("Transcript must be a path, a string or a dict")

    def load(self, path: Path):
        """Load a transcript from a path."""
        with path.open() as f:
            self.load_dict(json.load(f))

    def load_dict(self, transcript: dict):
        """Load a transcript from a dict."""
        self.tokens = []
        self.as_segment = []
        self.as_first_token = {}
        self.segments = transcript["segments"]
        for sed_n, seg in enumerate(self.segments):
            self.as_first_token[sed_n] = len(self.tokens)
            for token in re_tokens.split(seg["text"]):
                if token:
                    self.tokens.append(token)
                    self.as_segment.append(sed_n)
            self.tokens.append(" ")
            self.as_segment.append(sed_n)

    def __len__(self):
        return len(self.tokens)


class MarkdownResponse:
    """Class to work with markdown files. Tokenize results of LLM.
    tokens: list of tokens including punctuation and spaces
    as_paragraph: returns paragraph associated with token number
    is_header: returns True if token is a header
    """

    def __init__(self, markdown, skip_header=True):
        self.tokens = []
        self.as_paragraph = []
        self.is_header = []
        self.paragraphs = None
        if isinstance(markdown, Path):
            self.load(markdown, skip_header)
        elif isinstance(markdown, str):
            self.parse(markdown, skip_header)
        else:
            raise TypeError("Markdown must be a path or a string")

    def load(self, path: Path, skip_header: bool = True):
        """Load a markdown from a path."""
        with path.open() as f:
            self.parse(f.read(), skip_header=skip_header)

    def remove_header(self, markdown: str):
        """Remove header from markdown string."""
        if markdown.startswith("#"):
            return markdown
        first_paragraph_end = markdown.find("\n\n")
        if first_paragraph_end > 0:
            line = markdown[:first_paragraph_end].lower()
        else:
            line = markdown.lower()
        for marker in ["markdown", "result"]:
            if line.find(marker) > 0:
                return (
                    markdown[first_paragraph_end + 2 :]
                    if first_paragraph_end > 0
                    else ""
                )
        return markdown

    def parse(self, markdown, skip_header: bool = True):
        """Parse a markdown string."""
        self.tokens = []
        self.as_paragraph = []
        self.is_header = []
        self.paragraphs = []
        if skip_header:
            markdown = self.remove_header(markdown)
        for par_n, par in enumerate(markdown.split("\n\n")):
            is_header = par.startswith("#")
            self.paragraphs.append(par)
            for token in re_tokens.split(par):
                if token:
                    self.tokens.append(token)
                    self.as_paragraph.append(par_n)
                    self.is_header.append(is_header)

    def __len__(self):
        return len(self.tokens)

    def get_markdown_str(self, start: int = 0, end: int = -1):
        """Get markdown string from tokens."""
        result: List[str] = []
        if start < 0:
            start = len(self) + start
        if end < 0:
            end = len(self) + end
        last_paragraph = self.as_paragraph[start]
        for i in range(start, end+1):
            if self.as_paragraph[i] != last_paragraph:
                if result[-1] == " ":
                    result[-1] = "\n\n"
                # elif self.tokens[i] ==" " :
                #    result.append("\n\n")
                else:
                    result.append("\n\n")
                    result.append(self.tokens[i])
                last_paragraph = self.as_paragraph[i]
            else:
                result.append(self.tokens[i])

        return "".join(result)


class NoTokensError(Exception):
    pass


def print_alignment(transform, transcript_words, markdown_words):
    for op in transform:
        print(f"{op[0]} [{op[1]}:{op[2]}]->[{op[3]}:{op[4]}]:")
        print(f"   |{'|'.join(transcript_words[op[1]:op[2]])}|")
        print(f"   |{'|'.join(markdown_words[op[3]:op[4]])}|")


def print_parts(prefix, str1, str2):
    if isinstance(str1, list):
        str1 = "".join(str1)
    if isinstance(str2, list):
        str2 = "".join(str2)
    print(prefix + str1.replace("\n", "\\n") + "‖" + str2.replace("\n", "\\n"))


class Aligner:
    """Align Transcription and Markdown responses of model.
    next_block: returns next block of text to format including context
    push_result: push result of formatting
    is_complete: returns True if all text has been formatted
    get_result: returns formatted text with markdown and timestamps
    """

    def __init__(
        self,
        transcript: Transcript,
        block_size: int = 2000 * 2,
        block_delta: int = 200,
        context_size: int = 600,
        only_text_context_size: int = 400,
    ) -> None:
        self.transcript = transcript
        self.block_size = block_size
        self.block_delta = block_delta
        self.context_size = context_size
        self.only_text_context_size = only_text_context_size
        self.context_block_start = 0
        self.current_block_start = 0
        self.current_block_end = 0
        self.context = ""
        self.current_context_size = 0
        self.result_tokens: List[str] = []

    def first_block(self):
        """Get first block of text to format."""
        assert self.current_block_start == 0
        return self.next_block()

    def next_block(self):
        """Get next block of text to format."""
        assert self.current_block_start == self.current_block_end
        context = self.context + "\n\n" if self.context else ""
        if self.current_block_start == len(self.transcript):
            return context

        if (
            len(self.transcript) - self.current_block_start
            < self.block_size + self.block_delta - self.current_context_size
        ):
            self.current_block_end = len(self.transcript)
            return context + "".join(self.transcript.tokens[self.current_block_start :])
        delta_begin = (
            self.current_block_start
            + self.block_size
            - self.block_delta
            - self.current_context_size
        )
        delta_end = (
            self.current_block_start
            + self.block_size
            + self.block_delta
            - self.current_context_size
        )
        delta_end = min(delta_end, len(self.transcript))
        delta_begin = max(delta_begin, 0)
        reserve_candidate_pos = None
        for i in range(delta_begin, delta_end):
            if self.transcript.tokens[i] in ["!", ".", "?"]:
                self.current_block_end = i + 1
                break
            if self.transcript.tokens[i] == ",":
                reserve_candidate_pos = i + 1
        else:
            self.current_block_end = (
                delta_end if reserve_candidate_pos is None else reserve_candidate_pos
            )
        return context + "".join(
            self.transcript.tokens[self.current_block_start : self.current_block_end]
        ).strip("\n ")

    def push(self, formatted: MarkdownResponse):
        """Push result of formatting."""
        if self.context_block_start == len(self.transcript):
            return ""
        assert self.current_block_start != self.current_block_end
        assert self.current_block_start >= self.context_block_start
        transform = lev.opcodes(
            self.transcript.tokens[self.context_block_start : self.current_block_end],
            formatted.tokens,
        )
        print_alignment(
            transform,
            self.transcript.tokens[self.context_block_start : self.current_block_end],
            formatted.tokens,
        )
        last_markdown_paragraph = 0
        last_transcript_segment = None
        last_transcript_pos = None
        last_markdown_pos = None
        last_is_header = False
        context_started = False
        context_markdown_pos = None
        context_result_pos = None
        result_tokens: List[str] = []

        for op, t_from, t_to, m_from, m_to in transform:
            if op != "delete":
                for i in range(0, m_to - m_from):
                    if op == "insert":
                        transcript_pos = t_from + self.context_block_start
                        new_transcript_segment = None
                    else:
                        transcript_pos = t_from + i + self.context_block_start
                        new_transcript_segment = self.transcript.as_segment[
                            transcript_pos
                        ]

                    markdown_pos = i + m_from
                    new_markdown_paragraph = formatted.as_paragraph[markdown_pos]
                    current_is_header = formatted.is_header[markdown_pos]

                    is_segment_change = (
                        new_transcript_segment != last_transcript_segment
                    )
                    is_new_paragraph = last_markdown_paragraph != new_markdown_paragraph
                    if not context_started:
                        limit = (
                            self.context_size
                            if current_is_header
                            else self.only_text_context_size
                        )

                        if is_new_paragraph and (limit > len(formatted) - markdown_pos):
                            context_started = True
                            context_markdown_pos = markdown_pos
                            context_result_pos = len(result_tokens)
                            context_transcript_pos = transcript_pos

                    if (
                        not last_transcript_segment is None
                        and (is_segment_change or is_new_paragraph)
                        and not last_is_header
                    ):
                        result_tokens.append(f"{{{last_transcript_segment}}}")
                    if is_new_paragraph:
                        result_tokens.append("\n\n")
                    if (
                        not new_transcript_segment is None
                        and (is_segment_change or is_new_paragraph)
                        and not current_is_header
                    ):
                        result_tokens.append(f"{{{new_transcript_segment}}}")
                    result_tokens.append(formatted.tokens[markdown_pos])
                    if op == "insert":
                        last_transcript_segment = None
                    last_transcript_segment = new_transcript_segment
                    last_markdown_paragraph = new_markdown_paragraph
                    last_is_header = current_is_header
                    last_markdown_pos = markdown_pos
                    if op in ["equal","delete"]:
                        last_transcript_pos = transcript_pos
            else:
                last_transcript_pos = t_to-1 + self.context_block_start
                new_transcript_segment = self.transcript.as_segment[
                            last_transcript_pos 
                        ]

        if last_transcript_segment is not None and not last_is_header:
            # TODO: that would be cut if we have context
            result_tokens.append(f"{{{last_transcript_segment}}}")
            last_transcript_segment = None

        if last_transcript_pos is not None:
            if self.current_block_start == last_transcript_pos + 1:
                raise NoTokensError("Stuck on the same block")
            self.current_block_start = last_transcript_pos + 1
            self.current_block_end = self.current_block_start
        else:
            raise NoTokensError("No tokens were pushed")

        if (
            (self.current_block_start != len(self.transcript))
            and context_started
            and context_transcript_pos is not None
            and context_markdown_pos is not None
        ):
            self.context = formatted.get_markdown_str(context_markdown_pos).strip(" \n")
            self.current_context_size = len(formatted) - context_markdown_pos - 1
            self.context_block_start = context_transcript_pos
            self.result_tokens.extend(result_tokens[:context_result_pos])
        else:
            self.result_tokens.extend(result_tokens)
            self.context_block_start = self.current_block_start
            self.context = ""
            self.current_context_size = 0

        print_parts("R>", self.result_tokens[-5:], self.context)
        if not context_markdown_pos is None:
            print_parts(
                "M>",
                formatted.get_markdown_str(context_markdown_pos - 5, context_markdown_pos),
                self.context,
            )
        print_parts(
            "C>",
            self.transcript.tokens[
                self.context_block_start - 5 : self.context_block_start
            ],
            self.transcript.tokens[
                self.context_block_start : self.context_block_start + 5
            ],
        )
        print_parts(
            "T>",
            self.transcript.tokens[
                self.current_block_start - 5 : self.current_block_start
            ],
            self.transcript.tokens[
                self.current_block_start : self.current_block_start + 5
            ],
        )

        return self.next_block()

    def get_result(self):
        """Get result of formatting."""
        return "".join(self.result_tokens)
    def is_last_block(self):
        """Check if the last block is reached."""
        return self.current_block_end == len(self.transcript)
