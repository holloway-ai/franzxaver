import logging
import json
from pathlib import Path
import datetime
import os

import boto3
import ffmpeg

from scenedetect import SceneManager, open_video, ContentDetector
from scenedetect.scene_manager import save_images
from scenedetect.frame_timecode import FrameTimecode
from uuid import uuid4 as uuid

from app.core.config import settings


def extract_and_save_slides(path_to_video, dump_path):
    """
    Extracts slides from video and saves them to s3.
    Returns tuples (timestamp in seconds, image url).
    """

    threshold = 27.0
    frame_path = dump_path / "frames"
    session_id = str(uuid())
    base_url = "https://d8kx9lltbn9tr.cloudfront.net/"

    video = open_video(str(path_to_video))
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)  # ,callback=on_new_scene)
    scene_list = scene_manager.get_scene_list()

    image_filenames = save_images(
        scene_list[0:-1],
        video,
        num_images=1,
        image_name_template="$FRAME_NUMBER",
        image_extension="png",
        output_dir=str(frame_path),
    )
    results = []
    s3 = boto3.client("s3")
    for scene, images in image_filenames.items():
        for image in images:
            image_path = Path(image)
            timestamp = FrameTimecode(
                int(image_path.stem), video.frame_rate
            ).get_seconds()
            obj_name = f"joan/videos/{session_id}/slides/{image_path.name}"

            s3.upload_file(
                str(frame_path / image),
                "franzxaver",
                obj_name,
                ExtraArgs={"ContentType": "image/png"},
            )
            results.append((timestamp, f"{base_url}{obj_name}"))
    return results
