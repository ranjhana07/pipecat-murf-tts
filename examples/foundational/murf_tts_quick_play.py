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
        raise RuntimeError(
            "MURF_API_KEY is missing. Set it in .env or environment."
        )
    return api_key


async def main():
    logger.info("Starting Murf TTS quick play")

    # Output-only local audio transport (no mic input needed)
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=False,
            audio_out_enabled=True,
        )
    )

    tts = MurfTTSService(
        api_key=get_api_key(),
        params=MurfTTSService.InputParams(
            voice_id="en-UK-ruby",
            style="Conversational",
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

    # Queue a line of text for synthesis
    await task.queue_frames([
        TTSTextFrame(
            "Hello! This is Murf TTS playing a short sample.",
            aggregated_by="sentence",
        )
    ])

    runner = PipelineRunner()
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
