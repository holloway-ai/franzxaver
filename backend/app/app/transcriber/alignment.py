from pathlib import Path
import heapq
import bisect
import re
import json
from typing import List, Optional
import Levenshtein as lev
from indexedproperty import indexedproperty

r_bullet = r"\s*(?:[-\*\+]|\d+\.) "
r_word = r"[\w\'\-\*\~\_]+"
r_punctuation = r"[\.\,\?\!\:\;]"


class Transcript:
    """Class to work with transcript files. Tokenize results of Whisper.
    tokens: list of tokens including punctuation and spaces
    segments: list of segments
    as_segment: returns segments associated with token number
    as_first_token: returns token index associated with segment number
    """

    re_tokens = re.compile(f"({'|'.join([r_word, r_punctuation])})")

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
        self.as_first_token = []
        self.segments = transcript["segments"]
        for sed_n, seg in enumerate(self.segments):
            self.as_first_token.append(len(self.tokens))
            for token in Transcript.re_tokens.split(seg["text"].strip(" \n")):
                if token:
                    self.tokens.append(token)
                    self.as_segment.append(sed_n)
            self.tokens.append(" ")
            self.as_segment.append(sed_n)
        self.tokens.pop()

    def __len__(self):
        return len(self.tokens)

    @indexedproperty
    def begin(self, segment):
        return self.segments[segment]["start"]

    @indexedproperty
    def end(self, segment):
        return self.segments[segment]["end"]

    def __getitem__(self, key):
        return self.tokens[key]


class MarkdownResponse:
    """Class to work with markdown files. Tokenize results of LLM.
    tokens: list of tokens including punctuation and spaces
    as_paragraph: returns paragraph associated with token number
    is_header: returns True if token is a header
    """

    marker_paragraph = "\n"
    re_tokens = re.compile(f"({'|'.join([r_bullet, r_word, r_punctuation])})")
    re_bullet = re.compile(r_bullet)

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
        first_paragraph_end = markdown.find(self.marker_paragraph)
        if first_paragraph_end > 0:
            if first_paragraph_end <len(markdown)-1 and markdown[first_paragraph_end+1] == "\n":
                first_paragraph_end += 1
            line = markdown[:first_paragraph_end].lower()
        else:
            line = markdown.lower()
        for marker in ["markdown", "result"]:
            if line.find(marker) > 0:
                return (
                    markdown[first_paragraph_end + len(self.marker_paragraph) :]
                    if first_paragraph_end > 0
                    else ""
                )
        return markdown

    def _append_token(self, token, par_n, is_header):
        self.tokens.append(token)
        self.as_paragraph.append(par_n)
        self.is_header.append(is_header)

    def parse(self, markdown, skip_header: bool = True):
        """Parse a markdown string."""
        self.tokens = []
        self.as_paragraph = []
        self.is_header = []
        self.paragraphs = []
        if skip_header:
            markdown = self.remove_header(markdown)
        for par_n, par in enumerate(markdown.split(self.marker_paragraph)):
            is_header = par.startswith("#")
            self.paragraphs.append(len(self.tokens))
            assert par_n == len(self.paragraphs) - 1
            for token in self.re_tokens.split(par):
                if token:
                    self._append_token(token, par_n, is_header)
            self._append_token(" ", par_n, is_header)

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, key):
        return self.tokens[key]

    def get_markdown_str(self, start: int = 0, end: Optional[int] = None):
        """Get markdown string from tokens."""
        if start >= len(self):
            return ""
        result: List[str] = []
        if start < 0:
            start = len(self) + start
        if end is None:
            end = len(self)
        elif end < 0:
            end = len(self) + end
        last_paragraph = self.as_paragraph[start]
        for i in range(start, end):
            if self.as_paragraph[i] != last_paragraph:
                if result[-1] == " ":
                    result[-1] = self.marker_paragraph * (
                        self.as_paragraph[i] - last_paragraph
                    )
                else:
                    result.append(
                        self.marker_paragraph * (self.as_paragraph[i] - last_paragraph)
                    )
                last_paragraph = self.as_paragraph[i]

            result.append(self.tokens[i])

        return "".join(result)

    def find_nearest_cut(self, position: int, delta: int = 0):
        """Find nearest cut point to position."""
        ideal_cut = position  # nearest word by default
        candidates = []
        for pos in self.paragraphs:
            diff = abs(position - pos)
            if diff < delta:
                heapq.heappush(candidates, (diff, pos))
        for diff, paragraph_start in candidates:  # find nearest header
            if self.is_header[paragraph_start]:
                ideal_cut = paragraph_start
                break
        else:
            if candidates:  # find nearest paragraph
                ideal_cut = candidates[0][1]
            else:
                for i in range(delta):  # find nearest sentence
                    sentence_start = None
                    for pos in [position + i, position - i]:
                        if 0 <= pos < len(self) and self[pos] in [".", "!", "?"]:
                            sentence_start = pos + 1
                            if self[sentence_start] == " ":
                                sentence_start += 1
                            break
                    if sentence_start is not None:
                        ideal_cut = sentence_start
                        break
        return ideal_cut
    def find_long_paragraph_start(self, length: int):
        last_paragraph = 0
        for i, paragraph_start in enumerate(self.paragraphs):
            if paragraph_start - last_paragraph > length:
                return last_paragraph
            last_paragraph = paragraph_start
        return -1
        

    @indexedproperty
    def is_bullet_marker(self, position: int):
        """Returns True if token at position is bullet maker."""
        return self.re_bullet.match(self.tokens[position]) is not None


class NoTokensError(Exception):
    pass


def print_alignment(transform, transcript_words, markdown_words):
    for op in transform:
        print(f"{op[0]} [{op[1]}:{op[2]}]->[{op[3]}:{op[4]}]:")
        from_str = "|".join(transcript_words[op[1] : op[2]]).replace("\n", "\\n")
        print(f"   |{from_str}|")
        to_str = "|".join(markdown_words[op[3] : op[4]]).replace("\n", "\\n")
        print(f"   |{to_str}|")


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
    re_timestamp = re.compile(r"\{~\d+(?:\.\d+)?\}")
    def __init__(
        self,
        transcript: Transcript,
        block_size: int = 2000 * 2,
        block_delta: int = 200,
        context_size: int = 600,
        context_size_delta: int = 200,
    ) -> None:
        assert block_size - block_delta > context_size + context_size_delta
        self.transcript = transcript
        self.block_size = block_size
        self.block_delta = block_delta
        self.context_size = context_size
        self.context_size_delta = context_size_delta
        self.context_block_start = 0
        self.current_block_start = 0
        self.current_block_end = 0
        self.context = ""
        self.current_context_size = 0
        self.result_tokens: List[str] = []
        self.debug = True

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
            return context + "".join(self.transcript[self.current_block_start :])
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

    def _align(self, formatted: MarkdownResponse):
        """Align current block and formatted text."""
        self.formatted = formatted
        self.transform = lev.opcodes(
            self.transcript.tokens[self.context_block_start : self.current_block_end],
            self.formatted.tokens,
        )
        self.log_alignment()

    def _adjust_current_block(self):
        """Adjust current block to formatted text
        - formatted text could be shorter than current block
        - formatted text could be longer than current block"
        """
        i = len(self.transform) - 1

        operation = self.transform[i][0]
        length = self.transform[i][2] - self.transform[i][1]
        if operation in ["equal", "replace"] and length < 3:
            i -= 1
            operation = self.transform[i][0]
            length = self.transform[i][2] - self.transform[i][1]
        if operation in ["delete", "insert"] and length > 1:
            i -= 1
            if i < 0:
                raise NoTokensError("No tokens to format")
            if operation == "insert":
                markdown_cutoff = self.transform[i][4]
                self._align(
                    MarkdownResponse(
                        self.formatted.get_markdown_str(0, markdown_cutoff)
                    )
                )
            else:
                self.current_block_end = self.transform[i][2] + self.context_block_start
                self._align(self.formatted)

    @property
    def _transform_transcript_end(self):
        return self.transform[-1][2] + self.context_block_start

    @property
    def _transform_markdown_end(self):
        return self.transform[-1][4]

    @indexedproperty
    def _transform_transcript2markdown(self, index):
        index = index - self.context_block_start
        assert index >= 0
        i = bisect.bisect_left(self.transform, index, key=lambda x: x[1])
        if i == len(self.transform):
            return self.transform[-1][3] + index - self.transform[-1][1]
        else:
            return self.transform[i][3] + index - self.transform[i][1]

    def push(self, formatted: MarkdownResponse):
        """Push result of formatting.
        1. Align current block and formatted text
        2. Adjust current block to formatted text
            - formatted text could be shorter than current block
            - formatted text could be longer than current block
        3. Identify context for next block and select working block
            - we do not need context for last block
            - better to start context with header
            - context size should be close to context_size
            - if we can not find context with header, we can start with paragraph
            - if we can not find context with paragraph, we can start with sentence
            - if we can not find context with sentence, we can start with word
        4. Add timestamps to working block
            - do not brake bullets in markdown (add timestamps after bullet markers)
            - do not brake markdown headers (no timestamps in headers)
            - do not brake markdown links (add timestamps after links)
            - do not brake markdown highlights (do not put timestamps between highlight marker and word)

        """

        def end(segment: int):
            return f"{{~{self.transcript.end[segment]:.2f}}}"

        def begin(segment: int):
            return f"{{~{self.transcript.begin[segment]:.2f}}}"

        if self.context_block_start == len(self.transcript):
            return ""
        assert self.current_block_start < self.current_block_end
        assert self.current_block_start >= self.context_block_start

        self._align(formatted)
        self._adjust_current_block()
        markdown_context_cut = (
            self._transform_markdown_end
            if self._transform_transcript_end >= len(self.transcript)
            else self.formatted.find_nearest_cut(
                len(self.formatted) - self.context_size, self.context_size_delta
            )
        )
        markdown_context_cut = max(
            markdown_context_cut,
            self._transform_transcript2markdown[self.context_block_start],
        )

        last_markdown_paragraph = 0
        last_transcript_segment = None
        last_transcript_pos = None
        last_is_header = False
        context_transcript_pos = None
        result_tokens: List[str] = []

        for op, t_from, t_to, m_from, m_to in self.transform:
            if context_transcript_pos is not None:
                break
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
                    if markdown_pos >= markdown_context_cut:
                        context_transcript_pos = transcript_pos
                        break
                    new_markdown_paragraph = formatted.as_paragraph[markdown_pos]
                    current_is_header = formatted.is_header[markdown_pos]
                    is_empty_token = formatted.tokens[markdown_pos] in [" ", "\n",""]
                    is_new_paragraph = last_markdown_paragraph != new_markdown_paragraph
                    is_bullet = self.formatted.is_bullet_marker[markdown_pos]

                    is_segment_change = (
                        new_transcript_segment != last_transcript_segment
                    )


                    if (
                        not last_transcript_segment is None
                        and (is_segment_change or is_new_paragraph or is_bullet)
                        and not last_is_header
                        and result_tokens
                    ):
                        spaces_tokens = []
                        while result_tokens and result_tokens[-1] in ["", " ", "\n"]:
                            spaces_tokens.append(result_tokens.pop())
                        if  self.re_timestamp.match(result_tokens[-1]):
                            result_tokens.pop()
                            result_tokens.extend(spaces_tokens)
                        else:
                            result_tokens.extend(spaces_tokens)
                            tokens = [result_tokens.pop(), end(last_transcript_segment)]
                            result_tokens.extend(
                                tokens[:: -1 if tokens[0] in [""," ", "\n"] else 1]
                            )

                    if is_new_paragraph:
                        if not (
                            len(result_tokens) > 2
                            and result_tokens[-1] == "\n"
                            and result_tokens[-2] == "\n"
                        ):
                            result_tokens.append("\n")

                    if (
                        not new_transcript_segment is None
                        and (is_segment_change or is_new_paragraph or is_bullet)
                        and not current_is_header
                    ):
                        tokens = [
                            formatted[markdown_pos],
                            begin(new_transcript_segment),
                        ]
                        result_tokens.extend(tokens[:: 1 if is_bullet else -1])
                    else:
                        result_tokens.append(formatted[markdown_pos])
                    if op == "insert":
                        last_transcript_segment = None
                    last_transcript_segment = new_transcript_segment
                    last_markdown_paragraph = new_markdown_paragraph
                    last_is_header = current_is_header
                    if op in ["equal", "replace"]:
                        last_transcript_pos = transcript_pos
            else:
                last_transcript_pos = t_to - 1 + self.context_block_start
                new_transcript_segment = self.transcript.as_segment[last_transcript_pos]

        if last_transcript_segment is not None and not last_is_header:
            result_tokens.append(end(last_transcript_segment))
            last_transcript_segment = None
        result_tokens.append("\n")  # check if we need this

        self.current_block_start = self._transform_transcript_end
        self.current_block_end = self.current_block_start

        self.context = formatted.get_markdown_str(markdown_context_cut).strip(" \n")
        self.current_context_size = len(self.formatted) - markdown_context_cut - 1
        self.context_block_start = (
            context_transcript_pos
            if not context_transcript_pos is None
            else self.current_block_start
        )

        self.result_tokens.extend(result_tokens)
        self.log_result(markdown_context_cut)

        return self.next_block()

    def log_alignment(self):
        if self.debug:
            print_alignment(
                self.transform,
                self.transcript.tokens[
                    self.context_block_start : self.current_block_end
                ],
                self.formatted.tokens,
            )

    def log_result(
        self,
        context_markdown_pos,
    ):
        if self.debug:
            print_parts("R>", self.result_tokens[-5:], self.context)
            if not context_markdown_pos is None:
                print_parts(
                    "M>",
                    self.formatted.get_markdown_str(
                        context_markdown_pos - 5, context_markdown_pos
                    ),
                    self.context,
                )
            print_parts(
                "C>",
                self.transcript[
                    self.context_block_start - 5 : self.context_block_start
                ],
                self.transcript[
                    self.context_block_start : self.context_block_start + 5
                ],
            )
            print_parts(
                "T>",
                self.transcript[
                    self.current_block_start - 5 : self.current_block_start
                ],
                self.transcript[
                    self.current_block_start : self.current_block_start + 5
                ],
            )

    def get_result(self):
        """Get result of formatting."""
        return "".join(self.result_tokens).strip(" \n")

    def is_last_block(self):
        """Check if the last block is reached."""
        return self.current_block_end == len(self.transcript)
