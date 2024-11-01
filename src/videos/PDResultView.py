import os
import tempfile

from gig import Ent
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip
from utils import Log

from app import App

log = Log("PDResultVideo")


class PDResultVideo:

    def __init__(
        self,
        election_type="Parliamentary",
        date="2020-08-05",
        active_ent_id="EC-01C",
    ):
        self.election_type = election_type
        self.date = date
        self.active_ent_id = active_ent_id

    @property
    def dir_path(self):
        dir_path = os.path.join(
            tempfile.gettempdir(),
            "lk_elections",
            f"{self.election_type.lower()}-{self.date}",
            f"pd-result-{self.active_ent_id}",
        )
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    @property
    def image_path(self):
        app = App(
            election_type=self.election_type,
            date=self.date,
            active_ent_id=self.active_ent_id,
        )
        image_path = app.download_screenshot("latest-result-pd")
        app.quit()
        return image_path

    @property
    def audio_text(self):
        pd_ent = Ent.from_id(self.active_ent_id)
        lines = [
            f"{self.year} Sri Lankan {self.election_type} Election",
            f"Result for {pd_ent.name}",
        ]
        text = " ".join(lines)
        return text

    @property
    def audio_path(self):
        audio_path = os.path.join(self.dir_path, "audio_text.mp3")
        if os.path.exists(audio_path):
            log.warning(f"File exists: {audio_path}")
            return audio_path

        gTTS(self.audio_text).save(audio_path)
        log.info(f"Wrote {audio_path}")
        return audio_path

    @property
    def year(self):
        return self.date.split("-")[0]

    def build(self):
        video_path = os.path.join(self.dir_path, "video.mp4")
        # if os.path.exists(video_path):
        #     log.warning(f"File exists: {video_path}")
        #     return

        audio_clip = AudioFileClip(self.audio_path)
        image_clip = ImageClip(self.image_path).set_duration(
            audio_clip.duration
        )
        os.startfile(self.image_path)

        video_clip = image_clip.set_audio(audio_clip)
        video_clip.write_videofile(
            video_path,
            fps=24,
        )
        log.info(f"Wrote {video_path}")

        os.startfile(video_path)


if __name__ == "__main__":
    PDResultVideo().build()
