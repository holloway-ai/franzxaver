import time
import openai
import os
import logging
import json
import datetime
from pathlib import Path
import re
import Levenshtein
from app.core.config import settings
from app.transcriber.alignment import Transcript, MarkdownResponse, Aligner

logger = logging.getLogger(__name__)


def next_block(transcript, start_index=0, limit=200):
    text = []
    words = 0
    seg_index = 0
    for i in range(start_index, len(transcript["segments"])):
        line = transcript["segments"][i]["text"]
        text.append(line)
        words += len(line.split(" "))
        if line[-1] in [".", "?", "!"]:
            seg_index = len(text)
        if words > limit:
            break
    else:
        seg_index = len(text)
        assert i == len(transcript["segments"]) - 1

    text = "".join(text[:seg_index])
    return text, start_index + seg_index


system_prompt = """You are a transcription assistant.
Your goal is to format the given text so that it can be read while keeping the original text unchanged.
Try to execute it as accurately as you can.
"""
first_prompt_template = """
You are a transcription assistant. Process the given text into Markdown format fully, without any changes to the text. 
Put two carriage returns between paragraphs that make sense and are no longer than 100 tokens.
Group paragraphs into sections by inserting meaningful headings in Markdown format (line starting with ##). 
"""
second_prompt_template = """
You are a transcription assistant.
You'll be given a previous formatted fragment as context and the next portion of text to process as new text. 
Process only new text into Markdown format fully, without any changes to the text.
New text should follow context, do not change that order. Do not change the order of text.
Put two carriage returns between paragraphs that make sense and are no longer than 100 tokens.
Group paragraphs into sections by inserting meaningful headings in Markdown format (line starting with ##). 
"""


def get_prompt(text, context=None):
    if context is None:
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": first_prompt_template},
            {"role": "assistant", "content": "Sure, I'd be happy to! What's the text?"},
            {"role": "user", "content": text},
            {
                "role": "assistant",
                "content": "Ok, I get it. In the next message, I'll send you text in markdown format.",
            },
            {"role": "user", "content": "I'm ready to see the result"},
        ]
    else:
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": first_prompt_template},
            {
                "role": "assistant",
                "content": "Sure, I'd be happy to! What's the context?",
            },
            {"role": "user", "content": context},
            {"role": "assistant", "content": "I've got context. What's the new text?"},
            {"role": "user", "content": text},
            {
                "role": "assistant",
                "content": "Ok, I get it. In the next message, I'll send you text in markdown format.",
            },
            {"role": "user", "content": "I'm ready to see the result"},
        ]

    return prompt


def process(
    system_prompt, user_prompt, model="gpt-3.5-turbo", temperature=0.0, attempts=5
):
    retry_time = 0  
    def handle_error(e):
        retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
        logger.warning("API error %s occurred.",e,exc_info=e)
        return retry_time
    
    for _ in range(attempts):
        try:

            if retry_time > 0:
                logger.warning("Retrying in %s seconds...",retry_time,exc_info=retry_time)
                time.sleep(retry_time)
                
            response = openai.ChatCompletion.create(
                model=model,
                messages=user_prompt,
                temperature=temperature,
                timeout=60,
                api_key=settings.OPENAI_API,
            )
            return response["choices"][0]["message"]["content"]
        
        except openai.error.Timeout as exception:
            retry_time = handle_error(exception)
        except openai.error.RateLimitError as exception:
            retry_time = handle_error(exception)
        except openai.error.APIError as exception:
            retry_time = handle_error(exception)
        except OSError as exception:
            retry_time = handle_error(exception)
        
    raise Exception("Failed to get response")


def get_test_transcript(file_name="transcript.json"):
    import json
    from pathlib import Path

    with Path(__file__).parent.joinpath(file_name).open() as f:
        transcript = json.load(f)
    return transcript


def get_test_markdown():
    from pathlib import Path

    with Path(__file__).parent.joinpath("formatted.md").open() as f:
        markdown = "".join(f.readlines())
    return markdown


def get_last_section(formatted_result):
    last_header = formatted_result.rfind("## ")

    return formatted_result[last_header:].strip()


def add_timestamps(formatted_result, transcript, seg_index=0):
    text_with_timestamps = []
    add_start_timestamp = True
    for par_i, par in enumerate(formatted_result.split("\n")):
        if par.startswith("#") or par == "":
            text_with_timestamps.append(par)
            add_start_timestamp = True
            continue
        line = []
        # find segments in the paragraph
        pos = 0
        while pos < len(par):
            seg = transcript["segments"][seg_index]
            seg_text = seg["text"].lstrip()
            # print (seg_text)
            while pos < len(par) and par[pos] == " ":
                pos += 1
            if pos >= len(par):
                continue
            # print (par[pos:])
            if not par[pos:].startswith(seg_text):  # unexpected result
                # model can slightly change the text to make it more readable
                seg_tokens = seg_text.split(" ")
                par_tokens = par[pos:].split(" ")
                par_tokens = par_tokens[: len(seg_tokens)]
                changes = Levenshtein.distance(seg_tokens, par_tokens)
                if changes / len(seg) > 0.2:  # that's too much
                    logger.warning(
                        f"Can't find segment {seg_index} in the paragraph {par_i} stopping at {pos}"
                    )
                    text_with_timestamps.append("".join(line))
                    return "\n".join(text_with_timestamps), seg_index
                logger.info(
                    f"Not exact match for segment {seg_index} in the paragraph {par_i} at {pos}. Changes: {changes}/nSeg: {' '.join(seg_tokens)}/nPar: {' '.join(par_tokens)}"
                )
                if seg_index < len(transcript["segments"]) - 1:
                    next_pos = par[pos:].find(
                        transcript["segments"][seg_index + 1]["text"]
                    )
                    if next_pos > 0:
                        seg_text = par[pos : pos + next_pos]
                        logger.info(
                            f"Found next segment at {next_pos} in the paragraph {par_i}"
                        )
                    else:
                        seg_end = " ".join(seg_tokens[-3:])
                        par_seg = " ".join(par_tokens)
                        par_seg_pos = min(len(par_seg) + pos + 10, len(par))
                        next_pos = par[pos:par_seg_pos].rfind(seg_end)
                        if next_pos > 0:
                            seg_text = par[pos : pos + next_pos]
                            logger.info(
                                f"Found end segment at {next_pos} in the paragraph {par_i}"
                            )
                        else:  # what else can we do? we can build alignment matrix, but it's too much
                            seg_text = " ".join(par_tokens)
                            logger.info(
                                f"Using same amount of words in the paragraph {par_i}"
                            )

                else:  # last segment
                    seg_text = " ".join(par_tokens)

            seg_index += 1
            pos += len(seg_text)
            span = f"{seg_text} {{~{seg['end']:.2f}}} "
            if add_start_timestamp:
                span = f"{{~{seg['start']:.2f}}} " + span
            add_start_timestamp = False
            line.append(span)

        text_with_timestamps.append("".join(line))
    return "\n".join(text_with_timestamps), seg_index


def test_add_timestamps():
    import re

    transcript = get_test_transcript()
    formatted_result = get_test_markdown()
    headers = [m.start() for m in re.finditer(r"##", formatted_result)]
    first_step_pos = headers[len(headers) // 2]

    def get_last_seg(text):
        last_line = text[-20:-1].rstrip("\n").split("\n")[-1]
        last_seg = [
            i
            for i, seg in enumerate(transcript["segments"])
            if seg["text"].endswith(last_line)
        ]
        assert len(last_seg) == 1
        return last_seg[0]

    last_seg = get_last_seg(formatted_result[:first_step_pos])

    text_with_timestamps1, seg_index = add_timestamps(
        formatted_result[:first_step_pos], transcript
    )
    assert seg_index == last_seg + 1
    last_seg = get_last_seg(formatted_result[first_step_pos:])
    text_with_timestamps2, seg_index = add_timestamps(
        formatted_result[first_step_pos:], transcript, seg_index
    )
    assert seg_index == last_seg + 1


def test_next_block():
    transcript = get_test_transcript()
    full_text = "".join([seg["text"] for seg in transcript["segments"]])
    blocks = []
    seg_index = 0
    while seg_index < len(transcript["segments"]):
        block, seg_index = next_block(transcript, seg_index)
        blocks.append(block)
    text = "".join(blocks)
    # j= 0
    # for i, block in enumerate(blocks):
    #     bloc_len = len(block)
    #     print (i, j, bloc_len)
    #     print (block)
    #     assert full_text[j:j+bloc_len] == block, f"{full_text[j:j+bloc_len]} \n {block}"
    #     j += bloc_len

    # print (text)
    # print (full_text)
    assert full_text == text, f"{full_text} \n {text}"


def test_format_transcription():
    import re

    transcript = get_test_transcript()
    markdown = get_test_markdown()
    formatted_res = ("##" + line for line in markdown.split("##")[1:])
    max_seg = [
        i
        for i, seg in enumerate(transcript["segments"])
        if seg["text"].endswith(markdown[-20:-1])
    ][0]

    result = ""  # mock process and get result
    clean_res = (
        re.sub(r"{~\d+.\d+}", "", result)
        .replace("  ", " ")
        .replace("\n ", "\n")
        .replace(" \n", "\n")
    )


def clean_header(formatted_result, context, next_line):
    model_intro = "Here's the text in markdown format:"

    def cut_by_context(content_pos):
        pos = content_pos - 1
        while pos >= 0 and formatted_result[pos] in [" ", "\n"]:
            pos -= 1
        if pos >= 0:
            prev_line_pos = max(formatted_result[:pos].rfind("\n"), 0)
            if formatted_result[pos] == "#":  # header
                return formatted_result[prev_line_pos:]
        return formatted_result[content_pos:]

    intro_pos = formatted_result.find(model_intro)
    if intro_pos > 0:
        logger.info(f"Removing model intro at {intro_pos}")
        formatted_result = formatted_result[intro_pos + len(model_intro) :].lstrip(
            "\n "
        )
    context_line = ""
    if context is not None:
        i = len(context) - 1
        while i >= 0 and context[i] in [" ", "\n"]:
            i -= 1
        i = max(context[:i].rfind("\n"), 0)
        context_line = context[i:].strip()

    context_end_pos = formatted_result.find(context_line) if context_line != "" else -1
    if context_end_pos > 0:
        context_end_pos = context_end_pos + len(context_line)

    next_line = next_line.strip()
    new_content_pos = formatted_result.find(next_line)

    if new_content_pos < 0:
        if context_end_pos > 0:
            logger.info(
                f"Can't find next line {next_line} removing results with context to pos {context_end_pos}"
            )
            return formatted_result[context_end_pos:].lstrip("\n ")
        logger.warning(
            f"Can't find next line {next_line} in the formatted result and no context"
        )
        return formatted_result
    else:
        if context_end_pos > 0 and context_end_pos <= new_content_pos:
            # TODO: we should find last full context in the result
            logger.info(f"removing results with context to pos  {context_end_pos}")
            return formatted_result[context_end_pos:].lstrip("\n ")
        # model inserted new content before context.. that wired but we can't do much
        logger.info(
            f"context at {context_end_pos} is after new text at {new_content_pos}"
        )
        # try to extend new content to include formatting
        return cut_by_context(new_content_pos)
    return formatted_result


def insert_slides(text, slides):
    if slides is None or len(slides) == 0 or len(text) == 0:
        return text
    re_block = re.compile(r"^\{~(?P<begin>\d+\.\d+)\}.*\{~(?P<end>\d+\.\d+)\} ?$")
    paragraphs = text.split("\n")
    current_slide = 0
    result = []
    for par in paragraphs:
        m = re_block.match(par)
        if m is not None:
            begin = float(m.group("begin"))
            end = float(m.group("end"))
            while current_slide < len(slides) and slides[current_slide][0] < end:
                result.append("")
                result.append(
                    f"![{{~{slides[current_slide][0]:.2f}}}]({slides[current_slide][1]})"
                )
                result.append("")
                current_slide += 1

        result.append(par)
    while current_slide < len(slides):
        result.append(
            f"![{{~{slides[current_slide][0]:.2f}}}]({slides[current_slide][1]})"
        )
        current_slide += 1

    return "\n".join(result)


def format_transcription(
    transcript_dict,
    progress_callback=None,
    step=0,
    total_steps=100,
    dump_path=None,
    slides=None,
):
    def dump_json(data, file_name):
        if dump_path is None:
            return
        dump_path.mkdir(parents=True, exist_ok=True)
        with (dump_path / file_name).open("w") as f:
            json.dump(data, f)

    def dump_text(text, file_name):
        if dump_path is None:
            return
        dump_path.mkdir(parents=True, exist_ok=True)
        with (dump_path / file_name).open("w") as f:
            f.write(text)

    dump_json(transcript_dict, "transcript.json")

    transcript = Transcript(transcript_dict)

    aligner = Aligner(
        transcript=transcript,
        block_size=1200,
        block_delta=400,
        context_size=400,
        context_size_delta=200,
    )

    stuck_count = 0

    progress_seg = (total_steps - step) / len(transcript)

    current_block = aligner.first_block()
    while current_block:
        # block_limit = {0: 200, 1: 100}.get(stuck_count, 50)
        state_prefix = f"{aligner.context_block_start}_{aligner.current_block_start}_{aligner.current_block_end}"
        dump_text(current_block, f"{state_prefix}_request.md")
        prompt = get_prompt(current_block)
        dump_json(prompt, f"{state_prefix}_prompt.json")
        # temperature = {3: 0.07}.get(stuck_count, 0.0)
        temperature = 0.0
        formatted_result = process(
            system_prompt=system_prompt,
            user_prompt=prompt,
            model="gpt-3.5-turbo",
            temperature=temperature,
        )

        dump_text(formatted_result, f"{state_prefix}_result.md")
        formatted = MarkdownResponse(formatted_result)
        current_block = aligner.push(formatted)

        if progress_callback is not None:
            end = current_block.find("\n")
            end = end if end > 0 else len(current_block)
            end = min(end, 20)
            progress_text = (
                current_block[:end].replace("\n", " ").replace("#", "").strip() + "..."
            )
            progress_callback(
                step=step + int(progress_seg * aligner.context_block_start),
                steps=total_steps,
                description="formatting: " + progress_text,
            )

    result = aligner.get_result()
    result = insert_slides(result, slides)
    dump_text(result, f"result.md")

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_next_block()
    test_add_timestamps()
    dump_path = Path(
        "session_data/{date:%Y-%m-%d_%H:%M:%S}".format(date=datetime.datetime.now())
    )
    res = format_transcription(
        transcript_dict=get_test_transcript("transcript_1.json"), dump_path=dump_path
    )
    print(res)
