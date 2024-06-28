import os
from typing import Iterator

from django.core.files.base import ContentFile
from elevenlabs import save
from elevenlabs.client import ElevenLabs

from telemetry.models import SoundClip


class TTS:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required. Set it in the environment or pass it to the constructor.")

        self.client = ElevenLabs(api_key=self.api_key)

    def generate_mp3(self, text, voice="Josh", model="eleven_monolingual_v1"):
        """
        Generate MP3 audio data from the given text using ElevenLabs API.

        :param text: The text to convert to speech
        :param voice: The voice to use for text-to-speech (default: "Josh")
        :param model: The model to use for text-to-speech (default: "eleven_monolingual_v1")
        :return: The generated audio data as bytes
        """
        format = "mp3_22050_32"
        audio = self.client.generate(text=text, voice=voice, model=model, output_format=format)
        return audio

    def create_sound_clip(self, text, voice="Josh", model="eleven_monolingual_v1"):
        """
        Create a SoundClip model instance with generated audio.

        :param text: The text to convert to speech
        :param voice: The voice to use for text-to-speech (default: "Josh")
        :param model: The model to use for text-to-speech (default: "eleven_monolingual_v1")
        :return: The created SoundClip instance
        """
        audio = self.client.generate(text=text, voice=voice, model=model)

        sound_clip = SoundClip(subtitle=text, voice=voice, model=model)

        if isinstance(audio, Iterator):
            audio = b"".join(audio)

        # Save the audio content to the FileField
        sound_clip.audio_file.save(f"{voice}_{text[:30]}.mp3", ContentFile(audio), save=False)
        sound_clip.save()

        return sound_clip


