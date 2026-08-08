import asyncio
import edge_tts
import pygame
import os
import tempfile


VOICE = "en-US-AriaNeural"


class Speaker:

    async def _generate(self, text, filename):
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(filename)

    def speak(self, text):

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.close()

        asyncio.run(self._generate(text, temp.name))

        pygame.mixer.init()

        pygame.mixer.music.load(temp.name)

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

        pygame.mixer.quit()

        os.remove(temp.name)