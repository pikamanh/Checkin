from gtts import gTTS
from pydub import AudioSegment
import io
import pyaudio

vietnamese_names = ["Phan Minh Lộc"]

def play_audiosegment_with_pyaudio(audio_segment):
    """Phát AudioSegment bằng PyAudio"""
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(audio_segment.sample_width),
                    channels=audio_segment.channels,
                    rate=audio_segment.frame_rate,
                    output=True)

    # Gửi dữ liệu PCM (raw audio) tới thiết bị phát
    stream.write(audio_segment.raw_data)
    stream.stop_stream()
    stream.close()
    p.terminate()

def speak_dual_language(name, intro='Welcome', outro='and relatives to the ceremony to honor top 100 outstanding students - Spring 2025', intro_lang="en", name_lang="vi"):
    audio = AudioSegment.empty()

    # Intro
    tts_intro = gTTS(text=intro, lang=intro_lang)
    intro_io = io.BytesIO()
    tts_intro.write_to_fp(intro_io)
    intro_io.seek(0)
    audio += AudioSegment.from_mp3(intro_io)

    # Name
    tts_name = gTTS(text=name, lang=name_lang)
    name_io = io.BytesIO()
    tts_name.write_to_fp(name_io)
    name_io.seek(0)
    audio += AudioSegment.from_mp3(name_io)

    # Outro
    tts_outro = gTTS(text=outro, lang=intro_lang)
    outro_io = io.BytesIO()
    tts_outro.write_to_fp(outro_io)
    outro_io.seek(0)
    audio += AudioSegment.from_mp3(outro_io)

    play_audiosegment_with_pyaudio(audio)