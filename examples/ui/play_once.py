import argparse
import asyncio
import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.frames.frames import TTSTextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)

from pipecat_murf_tts.tts import MurfTTSService


def get_api_key() -> str:
    load_dotenv(override=True)
    api_key = os.getenv("MURF_API_KEY")
    if not api_key:
        raise RuntimeError("MURF_API_KEY is missing. Set it in .env or environment.")
    return api_key


async def main(text: str, voice: str, style: str):
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=False,
            audio_out_enabled=True,
        )
    )

    tts = MurfTTSService(
        api_key=get_api_key(),
        params=MurfTTSService.InputParams(
            voice_id=voice,
            style=style,
            sample_rate=44100,
            channel_type="MONO",
            format="PCM",
        ),
    )

    pipeline = Pipeline([
        tts,
        transport.output(),
    ])

    task = PipelineTask(pipeline)
    await task.queue_frames([
        TTSTextFrame(text, aggregated_by="sentence"),
    ])

    runner = PipelineRunner()
    await runner.run(task)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play one Murf TTS clip")
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", default="en-UK-ruby")
    parser.add_argument("--style", default="Conversational")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.text, args.voice, args.style))
    except Exception as e:
        logger.error(f"Playback error: {e}")
        raise
