import os
import wave
import uuid
import pyaudio
import whisper
from pathlib import Path
from config import config, ROOT_DIR
from utils.logger import logger

AUDIO_CHUNK = 1024
class AudioManager :
    def __init__(self) :
        try :
            self.model = whisper.load_model("base")
            self.frames = []
            self.stream = None
            self.p = None
            self.is_recording = False
            logger.info("Whisper model load success.")
        except :
            logger.error("Whisper model load failed.")
            return False
    
    def start_recording(self) :
        if self.is_recording :
            logger.warning("Already recording.")
            return
        
        try :
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format = pyaudio.paInt16,
                                      channels = 1,
                                      rate = 16000,
                                      input = True,
                                      frames_per_buffer = AUDIO_CHUNK)
            self.is_recording = True
            self.frames = []
        except Exception as e :
            logger.error(f"Start recording failed: {e}")
            self.is_recording = False
        
    def process_stream(self) :
        if self.is_recording and self.stream :
            try :
                data = self.stream.read(AUDIO_CHUNK, exception_on_overflow = False)
                self.frames.append(data)
            except :
                pass
        else :
            logger.warning("Not recording.")
    
    def stop_recording(self) :
        if not self.is_recording :
            logger.warning("Not recording.")
            return

        self.is_recording = False
        
        try :
            if self.stream :
                self.stream.stop_stream()
                self.stream.close()
            if self.p :
                self.p.terminate()
            
            filepath = ROOT_DIR / f"{uuid.uuid4()}.wav"
            wf = wave.open(str(filepath), "wb")
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b"".join(self.frames))
            wf.close()
            
            return str(filepath)
        except Exception as e :
            logger.error(f"Stop recording failed: {e}")
            return None
    
    def transcribe(self, filepath: str) -> str | None :
        if not os.path.exists(filepath) :
            logger.warning(f"File not found: {filepath}")
            return None
        
        try :
            result = self.model.transcribe(filepath, language = "zh", fp16 = False)["text"].strip()
            logger.info(f"Transcribe success: {result}")
            return result
        except Exception as e :
            logger.error(f"Transcribe failed: {e}")
            return None

audio_manager = AudioManager()