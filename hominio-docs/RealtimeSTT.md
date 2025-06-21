This file is a merged representation of the entire codebase, combined into a single document by Repomix.
The content has been processed where security check has been disabled.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Security check has been disabled - content may contain sensitive information
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.github/
  FUNDING.yml
example_app/
  install_cpu.bat
  install_gpu.bat
  README.MD
  start.bat
  ui_openai_voice_interface.py
example_browserclient/
  client.js
  index.html
  server.py
  start_server.bat
example_webserver/
  client.py
  server.py
  stt_server.py
RealtimeSTT/
  __init__.py
  audio_input.py
  audio_recorder_client.py
  audio_recorder.py
  safepipe.py
RealtimeSTT_server/
  index.html
  install_packages.py
  README.md
  stt_cli_client.py
  stt_server.py
tests/
  advanced_talk.py
  feed_audio.py
  install_packages.py
  minimalistic_talkbot.py
  openai_voice_interface.py
  openwakeword_test.py
  README.md
  realtime_loop_test.py
  realtimestt_chinese.py
  realtimestt_speechendpoint_binary_classified.py
  realtimestt_speechendpoint.py
  realtimestt_test_hotkeys_v2.py
  realtimestt_test_stereomix.py
  realtimestt_test.py
  recorder_client.py
  simple_test.py
  translator.py
  type_into_textbox.py
  vad_test.py
.dockerignore
docker-compose.yml
Dockerfile
install_with_gpu_support.bat
LICENSE
MANIFEST.in
README.md
requirements-gpu.txt
requirements.txt
setup.py
win_installgpu_virtual_env.bat
```

# Files

## File: .github/FUNDING.yml
````yaml
# These are supported funding model platforms

github: KoljaB
patreon: # Replace with a single Patreon username
open_collective: # Replace with a single Open Collective username
ko_fi: koljab
tidelift: # Replace with a single Tidelift platform-name/package-name e.g., npm/babel
community_bridge: # Replace with a single Community Bridge project-name e.g., cloud-foundry
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
lfx_crowdfunding: # Replace with a single LFX Crowdfunding project-name e.g., cloud-foundry
polar: # Replace with a single Polar username
buy_me_a_coffee: koljab
thanks_dev: # Replace with a single thanks.dev username
custom: # Replace with up to 4 custom sponsorship URLs e.g., ['link1', 'link2']
````

## File: example_app/install_cpu.bat
````
@echo off
cd /d %~dp0

REM Check if the venv directory exists
if not exist test_env\Scripts\python.exe (
    echo Creating VENV
    python -m venv test_env
) else (
    echo VENV already exists
)

echo Activating VENV
start cmd /k "call test_env\Scripts\activate.bat && pip install --upgrade RealtimeSTT==0.1.4 && pip install --upgrade RealtimeTTS==0.1.3 && pip install pysoundfile==0.9.0.post1 openai==0.27.8 keyboard==0.13.5 PyQt5==5.15.9 sounddevice==0.4.6 wavio==0.0.7"
````

## File: example_app/install_gpu.bat
````
@echo off
cd /d %~dp0

REM Check if the venv directory exists
if not exist test_env\Scripts\python.exe (
    echo Creating VENV
    python -m venv test_env
) else (
    echo VENV already exists
)

echo Activating VENV
start cmd /k "call test_env\Scripts\activate.bat && pip install --upgrade RealtimeSTT==0.1.4 && pip install --upgrade RealtimeTTS==0.1.3 && pip uninstall torch --yes && pip install torch==2.0.1+cu118 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118 && pip install pysoundfile==0.9.0.post1 openai==0.27.8 keyboard==0.13.5 PyQt5==5.15.9 sounddevice==0.4.6 wavio==0.0.7"
````

## File: example_app/README.MD
````markdown
# GPU Support with CUDA (recommended)

Steps for a **GPU-optimized** installation:

1. **Install NVIDIA CUDA Toolkit 11.8**:
    - Visit [NVIDIA CUDA Toolkit Archive](https://developer.nvidia.com/cuda-11-8-0-download-archive).
    - Select version 11.
    - Download and install the software.

2. **Install NVIDIA cuDNN 8.7.0 for CUDA 11.x**:
    - Visit [NVIDIA cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive).
    - Click on "Download cuDNN v8.7.0 (November 28th, 2022), for CUDA 11.x".
    - Download and install the software.

3. **Install ffmpeg**:

    You can download an installer for your OS from the [ffmpeg Website](https://ffmpeg.org/download.html).  
    
    Or use a package manager:

    - **On Ubuntu or Debian**:
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```

    - **On Arch Linux**:
        ```bash
        sudo pacman -S ffmpeg
        ```

    - **On MacOS using Homebrew** ([https://brew.sh/](https://brew.sh/)):
        ```bash
        brew install ffmpeg
        ```

    - **On Windows using Chocolatey** ([https://chocolatey.org/](https://chocolatey.org/)):
        ```bash
        choco install ffmpeg
        ```

    - **On Windows using Scoop** ([https://scoop.sh/](https://scoop.sh/)):
        ```bash
        scoop install ffmpeg
        ```    

4. **ElevenlabsEngine**
    - If you plan to use the `ElevenlabsEngine`, you need `mpv` is installed on your system for streaming mpeg audio

    - **macOS**:
    ```bash
    brew install mpv
    ```

    - **Linux and Windows**: Visit [mpv.io](https://mpv.io/) for installation instructions.

5. **Install PyTorch with CUDA support**:
    - run install_gpu.bat

6. **Configure script**
    - open ui_openai_voice_interface.py and configure your engine, set API keys, Azure service region, language etc
````

## File: example_app/start.bat
````
@echo off
cd /d %~dp0

REM Check if the venv directory exists
if not exist test_env\Scripts\python.exe (
    echo Creating VENV
    python -m venv test_env
) else (
    echo VENV already exists
)


:: OpenAI API Key  https://platform.openai.com/
set OPENAI_API_KEY=

:: Microsoft Azure API Key  https://portal.azure.com/
set AZURE_SPEECH_KEY=

:: Elevenlabs API Key  https://www.elevenlabs.io/Elevenlabs
set ELEVENLABS_API_KEY=


echo Activating VENV
start cmd /k "call test_env\Scripts\activate.bat && python ui_openai_voice_interface.py"
````

## File: example_app/ui_openai_voice_interface.py
````python
if __name__ == '__main__':

    from RealtimeTTS import TextToAudioStream, AzureEngine, ElevenlabsEngine, SystemEngine
    from RealtimeSTT import AudioToTextRecorder

    from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSignal, QThread
    from PyQt5.QtGui import QColor, QPainter, QFontMetrics, QFont, QMouseEvent
    from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMenu, QAction

    import os
    import openai
    import sys
    import time
    import sounddevice as sd
    import numpy as np
    import wavio
    import keyboard

    max_history_messages = 6
    return_to_wakewords_after_silence = 12
    start_with_wakeword = False
    start_engine = "Azure" # Azure, Elevenlabs
    recorder_model = "large-v2"
    language = "en"
    azure_speech_region = "eastus"
    openai_model = "gpt-3.5-turbo" # gpt-3.5-turbo, gpt-4, gpt-3.5-turbo-0613 / gpt-3.5-turbo-16k-0613 / gpt-4-0613 / gpt-4-32k-0613

    openai.api_key = os.environ.get("OPENAI_API_KEY")

    user_font_size = 22
    user_color = QColor(0, 188, 242) # turquoise

    assistant_font_size = 24
    assistant_color = QColor(239, 98, 166) # pink

    voice_azure = "en-GB-SoniaNeural"
    voice_system = "Zira"
    #voice_system = "Hazel"
    prompt = "Be concise, polite, and casual with a touch of sass. Aim for short, direct responses, as if we're talking."
    elevenlabs_model = "eleven_monolingual_v1"

    if language == "de":
        elevenlabs_model = "eleven_multilingual_v1"
        voice_system = "Katja"
        voice_azure = "de-DE-MajaNeural"
        prompt = 'Sei präzise, höflich und locker, mit einer Prise Schlagfertigkeit. Antworte kurz und direkt, als ob wir gerade sprechen.'
        
    print ("Click the top right corner to change the engine")
    print ("Press ESC to stop the current playback")

    system_prompt_message = {
        'role': 'system',
        'content': prompt
    }

    def generate_response(messages):
        """Generate assistant's response using OpenAI."""
        for chunk in openai.ChatCompletion.create(model=openai_model, messages=messages, stream=True, logit_bias={35309:-100, 36661:-100}):
            text_chunk = chunk["choices"][0]["delta"].get("content")
            if text_chunk:
                yield text_chunk

    history = []
    MAX_WINDOW_WIDTH = 1600
    MAX_WIDTH_ASSISTANT = 1200
    MAX_WIDTH_USER = 1500

    class AudioPlayer(QThread):
        def __init__(self, file_path):
            super(AudioPlayer, self).__init__()
            self.file_path = file_path

        def run(self):
            wav = wavio.read(self.file_path)
            sound = wav.data.astype(np.float32) / np.iinfo(np.int16).max  
            sd.play(sound, wav.rate)
            sd.wait()

    class TextRetrievalThread(QThread):
        textRetrieved = pyqtSignal(str)

        def __init__(self, recorder):
            super().__init__()
            self.recorder = recorder
            self.active = False  

        def run(self):
            while True:
                if self.active:  
                    text = self.recorder.text()
                    self.recorder.wake_word_activation_delay = return_to_wakewords_after_silence
                    self.textRetrieved.emit(text)
                    self.active = False
                time.sleep(0.1) 

        def activate(self):
            self.active = True 

    class TransparentWindow(QWidget):
        updateUI = pyqtSignal()
        clearAssistantTextSignal = pyqtSignal()
        clearUserTextSignal = pyqtSignal()

        def __init__(self):
            super().__init__()

            self.setGeometry(1, 1, 1, 1) 

            self.setWindowTitle("Transparent Window")
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

            self.big_symbol_font = QFont('Arial', 32)
            self.small_symbol_font = QFont('Arial', 17)
            self.user_font = QFont('Arial', user_font_size)
            self.assistant_font = QFont('Arial', assistant_font_size)      
            self.assistant_font.setItalic(True) 

            self.big_symbol_text = ""
            self.small_symbol_text = ""
            self.user_text = ""
            self.assistant_text = ""
            self.displayed_user_text = ""
            self.displayed_assistant_text = ""
            self.stream = None
            self.text_retrieval_thread = None

            self.user_text_timer = QTimer(self)
            self.assistant_text_timer = QTimer(self)
            self.user_text_timer.timeout.connect(self.clear_user_text)
            self.assistant_text_timer.timeout.connect(self.clear_assistant_text)

            self.clearUserTextSignal.connect(self.init_clear_user_text)
            self.clearAssistantTextSignal.connect(self.init_clear_assistant_text)
            self.user_text_opacity = 255 
            self.assistant_text_opacity = 255 
            self.updateUI.connect(self.update_self)
            self.audio_player = None

            self.run_fade_user = False
            self.run_fade_assistant = False

            self.menu = QMenu()
            self.menu.setStyleSheet("""
                QMenu {
                    background-color: black;
                    color: white;
                    border-radius: 10px;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
                """)

            self.elevenlabs_action = QAction("Elevenlabs", self)
            self.azure_action = QAction("Azure", self)
            self.system_action = QAction("System", self)
            self.quit_action = QAction("Quit", self)

            self.menu.addAction(self.elevenlabs_action)
            self.menu.addAction(self.azure_action)
            self.menu.addAction(self.system_action)
            self.menu.addSeparator() 
            self.menu.addAction(self.quit_action)

            self.elevenlabs_action.triggered.connect(lambda: self.select_engine("Elevenlabs"))
            self.azure_action.triggered.connect(lambda: self.select_engine("Azure"))
            self.system_action.triggered.connect(lambda: self.select_engine("System"))
            self.quit_action.triggered.connect(self.close_application)

        def mousePressEvent(self, event: QMouseEvent):
            if event.button() == Qt.LeftButton:
                if event.pos().x() >= self.width() - 100 and event.pos().y() <= 100:
                    self.menu.exec_(self.mapToGlobal(event.pos()))        

        def close_application(self):
            if self.recorder:
                self.recorder.shutdown()                    
            QApplication.quit()                

        def init(self):

            self.select_engine(start_engine)

            # recorder = AudioToTextRecorder(spinner=False, model="large-v2", language="de", on_recording_start=recording_start, silero_sensitivity=0.4, post_speech_silence_duration=0.4, min_length_of_recording=0.3, min_gap_between_recordings=0.01, realtime_preview_resolution = 0.01, realtime_preview = True, realtime_preview_model = "small", on_realtime_preview=text_detected)

            self.recorder = AudioToTextRecorder(
                model=recorder_model,
                language=language,
                wake_words="Jarvis",
                silero_use_onnx=False,
                spinner=True,
                silero_sensitivity=0.2,
                webrtc_sensitivity=3,
                on_recording_start=self.on_recording_start,
                on_vad_detect_start=self.on_vad_detect_start,
                on_wakeword_detection_start=self.on_wakeword_detection_start,
                on_transcription_start=self.on_transcription_start,
                post_speech_silence_duration=0.4, 
                min_length_of_recording=0.3, 
                min_gap_between_recordings=0.01, 
                enable_realtime_transcription = True,
                realtime_processing_pause = 0.01, 
                realtime_model_type = "tiny",
                on_realtime_transcription_stabilized=self.text_detected
            )
            if not start_with_wakeword:
                self.recorder.wake_word_activation_delay = return_to_wakewords_after_silence
                
            self.text_retrieval_thread = TextRetrievalThread(self.recorder)
            self.text_retrieval_thread.textRetrieved.connect(self.process_user_text)
            self.text_retrieval_thread.start()
            self.text_retrieval_thread.activate()

            keyboard.on_press_key('esc', self.on_escape)

        def closeEvent(self, event):
            if self.recorder:
                self.recorder.shutdown()            

        def select_engine(self, engine_name):
            if self.stream:
                self.stream.stop()
                self.stream = None

            engine = None

            if engine_name == "Azure":
                engine = AzureEngine(
                        os.environ.get("AZURE_SPEECH_KEY"),
                        os.environ.get("AZURE_SPEECH_REGION"),
                        voice_azure,
                        rate=24,
                        pitch=10,
                    )

            elif engine_name == "Elevenlabs":
                engine = ElevenlabsEngine(
                        os.environ.get("ELEVENLABS_API_KEY"),
                        model=elevenlabs_model
                    )
            else:
                engine = SystemEngine(
                    voice=voice_system,
                    #print_installed_voices=True
                )

            self.stream = TextToAudioStream(
                engine,
                on_character=self.on_character,
                on_text_stream_stop=self.on_text_stream_stop,
                on_text_stream_start=self.on_text_stream_start,
                on_audio_stream_stop=self.on_audio_stream_stop,
                log_characters=True
            )
            sys.stdout.write('\033[K')  # Clear to the end of line
            sys.stdout.write('\r')  # Move the cursor to the beginning of the line
            print (f"Using {engine_name} engine")


        def text_detected(self, text):
            self.run_fade_user = False
            if self.user_text_timer.isActive():
                self.user_text_timer.stop()
            self.user_text_opacity = 255 
            self.user_text = text
            self.updateUI.emit()

        def on_escape(self, e):
            if self.stream.is_playing():
                self.stream.stop()

        def showEvent(self, event: QEvent):
            super().showEvent(event)
            if event.type() == QEvent.Show:
                self.set_symbols("⌛", "🚀")
                QTimer.singleShot(1000, self.init) 

        def on_character(self, char):
            if self.stream:
                self.assistant_text += char
                self.updateUI.emit()

        def on_text_stream_stop(self):
            print("\"", end="", flush=True)
            if self.stream:
                assistant_response = self.stream.text()            
                self.assistant_text = assistant_response
                history.append({'role': 'assistant', 'content': assistant_response})

        def on_audio_stream_stop(self):
            self.set_symbols("🎙️", "⚪")

            if self.stream:
                self.clearAssistantTextSignal.emit()
                self.text_retrieval_thread.activate()

        def generate_answer(self):
            self.run_fade_assistant = False
            if self.assistant_text_timer.isActive():
                self.assistant_text_timer.stop()

            history.append({'role': 'user', 'content': self.user_text})
            self.remove_assistant_text()
            assistant_response = generate_response([system_prompt_message] + history[-max_history_messages:])
            self.stream.feed(assistant_response)
            self.stream.play_async(minimum_sentence_length=6,
                                buffer_threshold_seconds=2)

        def set_symbols(self, big_symbol, small_symbol):
            self.big_symbol_text = big_symbol
            self.small_symbol_text = small_symbol
            self.updateUI.emit()

        def on_text_stream_start(self):
            self.set_symbols("⌛", "👄")

        def process_user_text(self, user_text):
            user_text = user_text.strip()
            if user_text:
                self.run_fade_user = False
                if self.user_text_timer.isActive():
                    self.user_text_timer.stop()

                self.user_text_opacity = 255 
                self.user_text = user_text
                self.clearUserTextSignal.emit()
                print (f"Me: \"{user_text}\"\nAI: \"", end="", flush=True)
                self.set_symbols("⌛", "🧠")
                QTimer.singleShot(100, self.generate_answer)

        def on_transcription_start(self):
            self.set_symbols("⌛", "📝")

        def on_recording_start(self):
            self.text_storage = []
            self.ongoing_sentence = ""
            self.set_symbols("🎙️", "🔴")

        def on_vad_detect_start(self):
            if self.small_symbol_text == "💤" or self.small_symbol_text == "🚀":
                self.audio_player = AudioPlayer("active.wav")
                self.audio_player.start() 

            self.set_symbols("🎙️", "⚪")

        def on_wakeword_detection_start(self):
            self.audio_player = AudioPlayer("inactive.wav")
            self.audio_player.start()         

            self.set_symbols("", "💤")

        def init_clear_user_text(self):
            if self.user_text_timer.isActive():
                self.user_text_timer.stop()        
            self.user_text_timer.start(10000)

        def remove_user_text(self):
            self.user_text = ""
            self.user_text_opacity = 255 
            self.updateUI.emit()

        def fade_out_user_text(self):
            if not self.run_fade_user:
                return

            if self.user_text_opacity > 0:
                self.user_text_opacity -= 5 
                self.updateUI.emit()
                QTimer.singleShot(50, self.fade_out_user_text)
            else:
                self.run_fade_user = False
                self.remove_user_text()        

        def clear_user_text(self):
            self.user_text_timer.stop()

            if not self.user_text:
                return

            self.user_text_opacity = 255
            self.run_fade_user = True
            self.fade_out_user_text()

        def init_clear_assistant_text(self):
            if self.assistant_text_timer.isActive():
                self.assistant_text_timer.stop()        
            self.assistant_text_timer.start(10000)

        def remove_assistant_text(self):
            self.assistant_text = ""
            self.assistant_text_opacity = 255 
            self.updateUI.emit()

        def fade_out_assistant_text(self):
            if not self.run_fade_assistant:
                return
            
            if self.assistant_text_opacity > 0:
                self.assistant_text_opacity -= 5 
                self.updateUI.emit()
                QTimer.singleShot(50, self.fade_out_assistant_text)
            else:
                self.run_fade_assistant = False
                self.remove_assistant_text()        

        def clear_assistant_text(self):
            self.assistant_text_timer.stop()

            if not self.assistant_text:
                return

            self.assistant_text_opacity = 255
            self.run_fade_assistant = True
            self.fade_out_assistant_text()

        def update_self(self):

            self.blockSignals(True)
                    
            self.displayed_user_text, self.user_width = self.return_text_adjusted_to_width(self.user_text, self.user_font, MAX_WIDTH_USER)
            self.displayed_assistant_text, self.assistant_width = self.return_text_adjusted_to_width(self.assistant_text, self.assistant_font, MAX_WIDTH_ASSISTANT)       

            fm_symbol = QFontMetrics(self.big_symbol_font)
            self.symbol_width = fm_symbol.width(self.big_symbol_text) + 3
            self.symbol_height = fm_symbol.height() + 8

            self.total_width = MAX_WINDOW_WIDTH

            fm_user = QFontMetrics(self.user_font)
            user_text_lines = (self.displayed_user_text.count("\n") + 1)
            self.user_height = fm_user.height() * user_text_lines + 7

            fm_assistant = QFontMetrics(self.assistant_font)
            assistant_text_lines = (self.displayed_assistant_text.count("\n") + 1)
            self.assistant_height = fm_assistant.height() * assistant_text_lines + 18

            self.total_height = sum([self.symbol_height, self.user_height, self.assistant_height])

            desktop = QDesktopWidget()
            screen_rect = desktop.availableGeometry(desktop.primaryScreen())
            self.setGeometry(screen_rect.right() - self.total_width - 50, 0, self.total_width + 50, self.total_height + 50)

            self.blockSignals(False)

            self.update()

        def drawTextWithOutline(self, painter, x, y, width, height, alignment, text, textColor, outlineColor, outline_size):
            painter.setPen(outlineColor)
            for dx, dy in [(-outline_size, 0), (outline_size, 0), (0, -outline_size), (0, outline_size),
                        (-outline_size, -outline_size), (outline_size, -outline_size),
                        (-outline_size, outline_size), (outline_size, outline_size)]:
                painter.drawText(x + dx, y + dy, width, height, alignment, text)

            painter.setPen(textColor)
            painter.drawText(x, y, width, height, alignment, text)

        def paintEvent(self, event):
            painter = QPainter(self)

            offsetX = 4
            offsetY = 5
        
            painter.setPen(QColor(255, 255, 255))

            # Draw symbol
            painter.setFont(self.big_symbol_font)
            if self.big_symbol_text:
                painter.drawText(self.total_width - self.symbol_width + 5 + offsetX, offsetY, self.symbol_width, self.symbol_height, Qt.AlignRight | Qt.AlignTop, self.big_symbol_text)
                painter.setFont(self.small_symbol_font)
                painter.drawText(self.total_width - self.symbol_width + 17 + offsetX, offsetY + 10, self.symbol_width, self.symbol_height, Qt.AlignRight | Qt.AlignBottom, self.small_symbol_text)
            else:
                painter.setFont(self.small_symbol_font)
                painter.drawText(self.total_width - 43 + offsetX, offsetY + 2, 50, 50, Qt.AlignRight | Qt.AlignBottom, self.small_symbol_text)

            # Draw User Text
            painter.setFont(self.user_font)
            user_x = self.total_width - self.user_width - 45 + offsetX
            user_y = offsetY + 15
            user_color_with_opacity = QColor(user_color.red(), user_color.green(), user_color.blue(), self.user_text_opacity)
            outline_color_with_opacity = QColor(0, 0, 0, self.user_text_opacity)
            self.drawTextWithOutline(painter, user_x, user_y, self.user_width, self.user_height, Qt.AlignRight | Qt.AlignTop, self.displayed_user_text, user_color_with_opacity, outline_color_with_opacity, 2)

            # Draw Assistant Text
            painter.setFont(self.assistant_font)
            assistant_x = self.total_width - self.assistant_width - 5  + offsetX
            assistant_y = self.user_height + offsetY + 15
            assistant_color_with_opacity = QColor(assistant_color.red(), assistant_color.green(), assistant_color.blue(), self.assistant_text_opacity)
            outline_color_with_opacity = QColor(0, 0, 0, self.assistant_text_opacity)
            self.drawTextWithOutline(painter, assistant_x, assistant_y, self.assistant_width, self.assistant_height, Qt.AlignRight | Qt.AlignTop, self.displayed_assistant_text, assistant_color_with_opacity, outline_color_with_opacity, 2)

        def return_text_adjusted_to_width(self, text, font, max_width_allowed):
            """
            Line feeds are inserted so that the text width does never exceed max_width.
            Text is only broken up on whole words.
            """
            fm = QFontMetrics(font)
            words = text.split(' ')
            adjusted_text = ''
            current_line = ''
            max_width_used = 0
            
            for word in words:
                current_width = fm.width(current_line + word)
                if current_width <= max_width_allowed:
                    current_line += word + ' '
                else:
                    line_width = fm.width(current_line)
                    if line_width > max_width_used:
                        max_width_used = line_width
                    adjusted_text += current_line + '\n'
                    current_line = word + ' '
            
            line_width = fm.width(current_line)
            if line_width > max_width_used:
                max_width_used = line_width
            adjusted_text += current_line 
            return adjusted_text.rstrip(), max_width_used         

    app = QApplication(sys.argv)

    window = TransparentWindow()
    window.show()

    sys.exit(app.exec_())
````

## File: example_browserclient/client.js
````javascript
let socket = new WebSocket("ws://localhost:8001");
let displayDiv = document.getElementById('textDisplay');
let server_available = false;
let mic_available = false;
let fullSentences = [];

const serverCheckInterval = 5000; // Check every 5 seconds

function connectToServer() {
    socket = new WebSocket("ws://localhost:8001");

    socket.onopen = function(event) {
        server_available = true;
        start_msg();
    };

    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);

        if (data.type === 'realtime') {
            displayRealtimeText(data.text, displayDiv);
        } else if (data.type === 'fullSentence') {
            fullSentences.push(data.text);
            displayRealtimeText("", displayDiv); // Refresh display with new full sentence
        }
    };

    socket.onclose = function(event) {
        server_available = false;
    };
}

socket.onmessage = function(event) {
    let data = JSON.parse(event.data);

    if (data.type === 'realtime') {
        displayRealtimeText(data.text, displayDiv);
    } else if (data.type === 'fullSentence') {
        fullSentences.push(data.text);
        displayRealtimeText("", displayDiv); // Refresh display with new full sentence
    }
};

function displayRealtimeText(realtimeText, displayDiv) {
    let displayedText = fullSentences.map((sentence, index) => {
        let span = document.createElement('span');
        span.textContent = sentence + " ";
        span.className = index % 2 === 0 ? 'yellow' : 'cyan';
        return span.outerHTML;
    }).join('') + realtimeText;

    displayDiv.innerHTML = displayedText;
}

function start_msg() {
    if (!mic_available)
        displayRealtimeText("🎤  please allow microphone access  🎤", displayDiv);
    else if (!server_available)
        displayRealtimeText("🖥️  please start server  🖥️", displayDiv);
    else
        displayRealtimeText("👄  start speaking  👄", displayDiv);
};

// Check server availability periodically
setInterval(() => {
    if (!server_available) {
        connectToServer();
    }
}, serverCheckInterval);

start_msg()

socket.onopen = function(event) {
    server_available = true;
    start_msg()
};

// Request access to the microphone
navigator.mediaDevices.getUserMedia({ audio: true })
.then(stream => {
    let audioContext = new AudioContext();
    let source = audioContext.createMediaStreamSource(stream);
    let processor = audioContext.createScriptProcessor(256, 1, 1);

    source.connect(processor);
    processor.connect(audioContext.destination);
    mic_available = true;
    start_msg()

    processor.onaudioprocess = function(e) {
        let inputData = e.inputBuffer.getChannelData(0);
        let outputData = new Int16Array(inputData.length);

        // Convert to 16-bit PCM
        for (let i = 0; i < inputData.length; i++) {
            outputData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
        }

        // Send the 16-bit PCM data to the server

        if (socket.readyState === WebSocket.OPEN) {
            // Create a JSON string with metadata
            let metadata = JSON.stringify({ sampleRate: audioContext.sampleRate });
            // Convert metadata to a byte array
            let metadataBytes = new TextEncoder().encode(metadata);
            // Create a buffer for metadata length (4 bytes for 32-bit integer)
            let metadataLength = new ArrayBuffer(4);
            let metadataLengthView = new DataView(metadataLength);
            // Set the length of the metadata in the first 4 bytes
            metadataLengthView.setInt32(0, metadataBytes.byteLength, true); // true for little-endian
            // Combine metadata length, metadata, and audio data into a single message
            let combinedData = new Blob([metadataLength, metadataBytes, outputData.buffer]);
            socket.send(combinedData);
        }
    };
})
.catch(e => console.error(e));
````

## File: example_browserclient/index.html
````html
<!DOCTYPE html>
<html>
<head>
    <title>Audio Streamer</title>
    <meta charset="UTF-8">
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        html, body {
            height: 100%;
            margin: 0;
        }
        body {
            background-color: black;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .text-display {
            white-space: pre-wrap; /* Preserves spaces and line breaks */
            font-size: 16px;
        }
        .yellow {
            color: yellow;
        }
        .cyan {
            color: cyan;
        }
    </style>
</head>
<body>
    <div id="textDisplay" style="max-width: 800px; margin: auto;">
    <script src="client.js"></script>
</body>
</html>
````

## File: example_browserclient/server.py
````python
if __name__ == '__main__':
    print("Starting server, please wait...")
    from RealtimeSTT import AudioToTextRecorder
    import asyncio
    import websockets
    import threading
    import numpy as np
    from scipy.signal import resample
    import json
    import logging
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logging.getLogger('websockets').setLevel(logging.WARNING)

    is_running = True
    recorder = None
    recorder_ready = threading.Event()
    client_websocket = None
    main_loop = None  # This will hold our primary event loop

    async def send_to_client(message):
        global client_websocket
        if client_websocket:
            try:
                await client_websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                client_websocket = None
                print("Client disconnected")

    # Called from the recorder thread on stabilized realtime text.
    def text_detected(text):
        global main_loop
        if main_loop is not None:
            # Schedule the sending on the main event loop
            asyncio.run_coroutine_threadsafe(
                send_to_client(json.dumps({
                    'type': 'realtime',
                    'text': text
                })), main_loop)
        print(f"\r{text}", flush=True, end='')

    recorder_config = {
        'spinner': False,
        'use_microphone': False,
        'model': 'large-v2',
        'language': 'en',
        'silero_sensitivity': 0.4,
        'webrtc_sensitivity': 2,
        'post_speech_silence_duration': 0.7,
        'min_length_of_recording': 0,
        'min_gap_between_recordings': 0,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0,
        'realtime_model_type': 'tiny.en',
        'on_realtime_transcription_stabilized': text_detected,
    }

    def run_recorder():
        global recorder, main_loop, is_running
        print("Initializing RealtimeSTT...")
        recorder = AudioToTextRecorder(**recorder_config)
        print("RealtimeSTT initialized")
        recorder_ready.set()

        # Loop indefinitely checking for full sentence output.
        while is_running:
            try:
                full_sentence = recorder.text()
                if full_sentence:
                    if main_loop is not None:
                        asyncio.run_coroutine_threadsafe(
                            send_to_client(json.dumps({
                                'type': 'fullSentence',
                                'text': full_sentence
                            })), main_loop)
                    print(f"\rSentence: {full_sentence}")
            except Exception as e:
                print(f"Error in recorder thread: {e}")
                continue

    def decode_and_resample(audio_data, original_sample_rate, target_sample_rate):
        try:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            num_original_samples = len(audio_np)
            num_target_samples = int(num_original_samples * target_sample_rate / original_sample_rate)
            resampled_audio = resample(audio_np, num_target_samples)
            return resampled_audio.astype(np.int16).tobytes()
        except Exception as e:
            print(f"Error in resampling: {e}")
            return audio_data

    async def echo(websocket):
        global client_websocket
        print("Client connected")
        client_websocket = websocket

        try:
            async for message in websocket:
                if not recorder_ready.is_set():
                    print("Recorder not ready")
                    continue

                try:
                    # Read the metadata length (first 4 bytes)
                    metadata_length = int.from_bytes(message[:4], byteorder='little')
                    # Get the metadata JSON string
                    metadata_json = message[4:4+metadata_length].decode('utf-8')
                    metadata = json.loads(metadata_json)
                    sample_rate = metadata['sampleRate']
                    # Get the audio chunk following the metadata
                    chunk = message[4+metadata_length:]
                    resampled_chunk = decode_and_resample(chunk, sample_rate, 16000)
                    recorder.feed_audio(resampled_chunk)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            if client_websocket == websocket:
                client_websocket = None

    async def main():
        global main_loop
        main_loop = asyncio.get_running_loop()

        recorder_thread = threading.Thread(target=run_recorder)
        recorder_thread.daemon = True
        recorder_thread.start()
        recorder_ready.wait()

        print("Server started. Press Ctrl+C to stop the server.")
        async with websockets.serve(echo, "localhost", 8001):
            try:
                await asyncio.Future()  # run forever
            except asyncio.CancelledError:
                print("\nShutting down server...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        is_running = False
        recorder.stop()
        recorder.shutdown()
    finally:
        if recorder:
            del recorder
````

## File: example_browserclient/start_server.bat
````
@echo off
cd /d %~dp0
python server.py
cmd
````

## File: example_webserver/client.py
````python
from colorama import Fore, Style
import websockets
import colorama
import keyboard
import asyncio
import json
import os

colorama.init()

SEND_START_COMMAND = False
HOST = 'localhost:5025'
URI = f'ws://{HOST}'
RECONNECT_DELAY = 5  

full_sentences = []

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

def update_displayed_text(text = ""):
    sentences_with_style = [
        f"{Fore.YELLOW + sentence + Style.RESET_ALL if i % 2 == 0 else Fore.CYAN + sentence + Style.RESET_ALL} "
        for i, sentence in enumerate(full_sentences)
    ]
    text = "".join(sentences_with_style).strip() + " " + text if len(sentences_with_style) > 0 else text
    clear_console()
    print("CLIENT retrieved text:")
    print()
    print(text)

async def send_start_recording(websocket):
    command = {
        "type": "command",
        "content": "start-recording"
    }
    await websocket.send(json.dumps(command))

async def test_client():
    while True:
        try:
            async with websockets.connect(URI, ping_interval=None) as websocket:

                if SEND_START_COMMAND:
                    # New: Check for space bar press and send start-recording message
                    async def check_space_keypress():
                        while True:
                            if keyboard.is_pressed('space'):
                                print ("Space bar pressed. Sending start-recording message to server.")
                                await send_start_recording(websocket)
                                await asyncio.sleep(1) 
                            await asyncio.sleep(0.02)
                    
                    # Start a task to monitor the space keypress
                    print ("Press space bar to start recording.")
                    asyncio.create_task(check_space_keypress())
                
                while True:
                    message = await websocket.recv()
                    message_obj = json.loads(message)
                    
                    if message_obj["type"] == "realtime":
                        clear_console()
                        print (message_obj["content"])
                    elif message_obj["type"] == "full":
                        clear_console()
                        colored_message = Fore.YELLOW + message_obj["content"] + Style.RESET_ALL
                        print (colored_message)
                        print ()
                        if SEND_START_COMMAND:
                            print ("Press space bar to start recording.")
                        full_sentences.append(message_obj["content"])
                    elif message_obj["type"] == "record_start":
                        print ("recording started.")
                    elif message_obj["type"] == "vad_start":
                        print ("vad started.")
                    elif message_obj["type"] == "wakeword_start":
                        print ("wakeword started.")
                    elif message_obj["type"] == "transcript_start":
                        print ("transcript started.")

                    else:
                        print (f"Unknown message: {message_obj}")
                    
        except websockets.ConnectionClosed:
            print("Connection with server closed. Reconnecting in", RECONNECT_DELAY, "seconds...")
            await asyncio.sleep(RECONNECT_DELAY)
        except KeyboardInterrupt:
            print("Gracefully shutting down the client.")
            break
        except Exception as e:
            print(f"An error occurred: {e}. Reconnecting in", RECONNECT_DELAY, "seconds...")
            await asyncio.sleep(RECONNECT_DELAY)    

asyncio.run(test_client())
````

## File: example_webserver/server.py
````python
WAIT_FOR_START_COMMAND = False

if __name__ == '__main__':
    server = "0.0.0.0"
    port = 5025

    print (f"STT speech to text server")
    print (f"runs on http://{server}:{port}")
    print ()
    print ("starting")
    print ("└─ ... ", end='', flush=True)

    from RealtimeSTT import AudioToTextRecorder
    from colorama import Fore, Style
    import websockets
    import threading
    import colorama
    import asyncio
    import shutil
    import queue
    import json
    import time
    import os

    colorama.init()

    first_chunk = True
    full_sentences = []
    displayed_text = ""
    message_queue = queue.Queue() 
    start_recording_event = threading.Event()
    start_transcription_event = threading.Event()
    connected_clients = set()

    def clear_console():
        os.system('clear' if os.name == 'posix' else 'cls')

    async def handler(websocket, path):

        print ("\r└─ OK")
        if WAIT_FOR_START_COMMAND:
            print("waiting for start command")
            print ("└─ ... ", end='', flush=True)

        connected_clients.add(websocket)

        try:
            while True:
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "command" and data.get("content") == "start-recording":
                        print ("\r└─ OK")
                        start_recording_event.set() 

        except json.JSONDecodeError:
            print (Fore.RED + "STT Received an invalid JSON message." + Style.RESET_ALL)
        except websockets.ConnectionClosedError:
            print (Fore.RED + "connection closed unexpectedly by the client" + Style.RESET_ALL)
        except websockets.exceptions.ConnectionClosedOK:
            print("connection closed.")
        finally:

            print("client disconnected")
            connected_clients.remove(websocket)
            print ("waiting for clients")
            print ("└─ ... ", end='', flush=True)


    def add_message_to_queue(type: str, content):
        message = {
            "type": type,
            "content": content
        }
        message_queue.put(message)    

    def fill_cli_line(text):
        columns, _ = shutil.get_terminal_size()
        return text.ljust(columns)[-columns:]

    def text_detected(text):
        global displayed_text, first_chunk

        if text != displayed_text:
            first_chunk = False
            displayed_text = text
            add_message_to_queue("realtime", text)

            message = fill_cli_line(text)

            message ="└─ " + Fore.CYAN + message[:-3] + Style.RESET_ALL
            print(f"\r{message}", end='', flush=True)


    async def broadcast(message_obj):
        if connected_clients:
            for client in connected_clients:
                await client.send(json.dumps(message_obj))

    async def send_handler():
        while True:
            while not message_queue.empty():
                message = message_queue.get()
                await broadcast(message)
            await asyncio.sleep(0.02)

    def recording_started():
        add_message_to_queue("record_start", "")

    def vad_detect_started():
        add_message_to_queue("vad_start", "")

    def wakeword_detect_started():
        add_message_to_queue("wakeword_start", "")

    def transcription_started():
        add_message_to_queue("transcript_start", "")

    recorder_config = {
        'spinner': False,
        'model': 'small.en',
        'language': 'en',
        'silero_sensitivity': 0.01,
        'webrtc_sensitivity': 3,
        'silero_use_onnx': False,
        'post_speech_silence_duration': 1.2,
        'min_length_of_recording': 0.2,
        'min_gap_between_recordings': 0,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0,
        'realtime_model_type': 'tiny.en',
        'on_realtime_transcription_stabilized': text_detected,
        'on_recording_start' : recording_started,
        'on_vad_detect_start' : vad_detect_started,
        'on_wakeword_detection_start' : wakeword_detect_started,
        'on_transcription_start' : transcription_started,
    }

    recorder = AudioToTextRecorder(**recorder_config)

    def transcriber_thread():
        while True:
            start_transcription_event.wait()
            text = "└─ transcribing ... "
            text = fill_cli_line(text)
            print (f"\r{text}", end='', flush=True)
            sentence = recorder.transcribe()
            print (Style.RESET_ALL + "\r└─ " + Fore.YELLOW + sentence + Style.RESET_ALL)
            add_message_to_queue("full", sentence)
            start_transcription_event.clear()
            if WAIT_FOR_START_COMMAND:
                print("waiting for start command")
                print ("└─ ... ", end='', flush=True)

    def recorder_thread():
        global first_chunk
        while True:
            if not len(connected_clients) > 0:
                time.sleep(0.1)
                continue
            first_chunk = True
            if WAIT_FOR_START_COMMAND:
                start_recording_event.wait() 
            print("waiting for sentence")
            print ("└─ ... ", end='', flush=True)
            recorder.wait_audio()
            start_transcription_event.set()
            start_recording_event.clear()

    threading.Thread(target=recorder_thread, daemon=True).start()
    threading.Thread(target=transcriber_thread, daemon=True).start()

    start_server = websockets.serve(handler, server, port)
    loop = asyncio.get_event_loop()

    print ("\r└─ OK")
    print ("waiting for clients")
    print ("└─ ... ", end='', flush=True)

    loop.run_until_complete(start_server)
    loop.create_task(send_handler())
    loop.run_forever()
````

## File: example_webserver/stt_server.py
````python
end_of_sentence_detection_pause = 0.45
unknown_sentence_detection_pause = 0.7
mid_sentence_detection_pause = 2.0

from install_packages import check_and_install_packages

check_and_install_packages([
    {
        'module_name': 'RealtimeSTT',                 # Import module
        'attribute': 'AudioToTextRecorder',           # Specific class to check
        'install_name': 'RealtimeSTT',                # Package name for pip install
    },
    {
        'module_name': 'websockets',                  # Import module
        'install_name': 'websockets',                 # Package name for pip install
    },
    {
        'module_name': 'numpy',                       # Import module
        'install_name': 'numpy',                      # Package name for pip install
    },
    {
        'module_name': 'scipy.signal',                # Submodule of scipy
        'attribute': 'resample',                      # Specific function to check
        'install_name': 'scipy',                      # Package name for pip install
    }
])

print("Starting server, please wait...")

import asyncio
import threading
import json
import websockets
from RealtimeSTT import AudioToTextRecorder
import numpy as np
from scipy.signal import resample

recorder = None
recorder_ready = threading.Event()
client_websocket = None
prev_text = ""


async def send_to_client(message):
    global client_websocket
    if client_websocket and client_websocket.open:
        try:
            await client_websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("Client websocket is closed, resetting client_websocket")
            client_websocket = None
    else:
        print("No client connected or connection is closed.")
        client_websocket = None  # Ensure it resets

def preprocess_text(text):
    # Remove leading whitespaces
    text = text.lstrip()

    #  Remove starting ellipses if present
    if text.startswith("..."):
        text = text[3:]

    # Remove any leading whitespaces again after ellipses removal
    text = text.lstrip()

    # Uppercase the first letter
    if text:
        text = text[0].upper() + text[1:]
    
    return text

def text_detected(text):
    global prev_text

    text = preprocess_text(text)

    sentence_end_marks = ['.', '!', '?', '。'] 
    if text.endswith("..."):
        recorder.post_speech_silence_duration = mid_sentence_detection_pause
    elif text and text[-1] in sentence_end_marks and prev_text and prev_text[-1] in sentence_end_marks:
        recorder.post_speech_silence_duration = end_of_sentence_detection_pause
    else:
        recorder.post_speech_silence_duration = unknown_sentence_detection_pause

    prev_text = text

    try:
        asyncio.new_event_loop().run_until_complete(
            send_to_client(
                json.dumps({
                    'type': 'realtime',
                    'text': text
                })
            )
        )
    except Exception as e:
        print(f"Error in text_detected while sending to client: {e}")
    print(f"\r{text}", flush=True, end='')


# Recorder configuration
recorder_config = {
    'spinner': False,
    'use_microphone': False,
    'model': 'medium.en', # or large-v2 or deepdml/faster-whisper-large-v3-turbo-ct2 or ...
    'input_device_index': 1,
    'realtime_model_type': 'tiny.en', # or small.en or distil-small.en or ...
    'language': 'en',
    'silero_sensitivity': 0.05,
    'webrtc_sensitivity': 3,
    'post_speech_silence_duration': unknown_sentence_detection_pause,
    'min_length_of_recording': 1.1,        
    'min_gap_between_recordings': 0,                
    'enable_realtime_transcription': True,
    'realtime_processing_pause': 0.02,
    'on_realtime_transcription_update': text_detected,
    #'on_realtime_transcription_stabilized': text_detected,
    'silero_deactivity_detection': True,
    'early_transcription_on_silence': 0.2,
    'beam_size': 5,
    'beam_size_realtime': 3,
    'no_log_file': True,
    'initial_prompt': 'Add periods only for complete sentences. Use ellipsis (...) for unfinished thoughts or unclear endings. Examples: \n- Complete: "I went to the store."\n- Incomplete: "I think it was..."'
    #  'initial_prompt': "Only add a period at the end of a sentence if you are 100 percent certain that the speaker has finished their statement. If you're unsure or the sentence seems incomplete, leave the sentence open or use ellipses to reflect continuation. For example: 'I went to the...' or 'I think it was...'"
    # 'initial_prompt': "Use ellipses for incomplete sentences like: I went to the..."        
}

def _recorder_thread():
    global recorder, prev_text
    print("Initializing RealtimeSTT...")
    recorder = AudioToTextRecorder(**recorder_config)
    print("RealtimeSTT initialized")
    recorder_ready.set()
    
    def process_text(full_sentence):
        print(f"\rSentence1: {full_sentence}")
        full_sentence = preprocess_text(full_sentence)
        print(f"\rSentence2: {full_sentence}")
        prev_text = ""
        try:
            asyncio.new_event_loop().run_until_complete(
                send_to_client(
                    json.dumps({
                        'type': 'fullSentence',
                        'text': full_sentence
                    })
                )
            )
        except Exception as e:
            print(f"Error in _recorder_thread while sending to client: {e}")
        print(f"\rSentence3: {full_sentence}")

    while True:
        recorder.text(process_text)

def decode_and_resample(
        audio_data,
        original_sample_rate,
        target_sample_rate):

    # Decode 16-bit PCM data to numpy array
    audio_np = np.frombuffer(audio_data, dtype=np.int16)

    # Calculate the number of samples after resampling
    num_original_samples = len(audio_np)
    num_target_samples = int(num_original_samples * target_sample_rate /
                                original_sample_rate)

    # Resample the audio
    resampled_audio = resample(audio_np, num_target_samples)

    return resampled_audio.astype(np.int16).tobytes()

async def echo(websocket, path):
    print("Client connected")
    global client_websocket
    client_websocket = websocket
    recorder.post_speech_silence_duration = unknown_sentence_detection_pause
    try:
        async for message in websocket:
            if not recorder_ready.is_set():
                print("Recorder not ready")
                continue

            metadata_length = int.from_bytes(message[:4], byteorder='little')
            metadata_json = message[4:4+metadata_length].decode('utf-8')
            metadata = json.loads(metadata_json)
            sample_rate = metadata['sampleRate']
            chunk = message[4+metadata_length:]
            resampled_chunk = decode_and_resample(chunk, sample_rate, 16000)
            recorder.feed_audio(resampled_chunk)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected: {e}")
    finally:
        print("Resetting client_websocket after disconnect")
        client_websocket = None  # Reset websocket reference

def main():            
    start_server = websockets.serve(echo, "localhost", 8011)

    recorder_thread = threading.Thread(target=_recorder_thread)
    recorder_thread.start()
    recorder_ready.wait()

    print("Server started. Press Ctrl+C to stop the server.")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
````

## File: RealtimeSTT/__init__.py
````python
from .audio_recorder import AudioToTextRecorder
from .audio_recorder_client import AudioToTextRecorderClient
from .audio_input import AudioInput
````

## File: RealtimeSTT/audio_input.py
````python
from colorama import init, Fore, Style
from scipy.signal import butter, filtfilt, resample_poly
import pyaudio
import logging

DESIRED_RATE = 16000
CHUNK_SIZE = 1024
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1

class AudioInput:
    def __init__(
            self,
            input_device_index: int = None,
            debug_mode: bool = False,
            target_samplerate: int = DESIRED_RATE,
            chunk_size: int = CHUNK_SIZE,
            audio_format: int = AUDIO_FORMAT,
            channels: int = CHANNELS,
            resample_to_target: bool = True,
        ):

        self.input_device_index = input_device_index
        self.debug_mode = debug_mode
        self.audio_interface = None
        self.stream = None
        self.device_sample_rate = None
        self.target_samplerate = target_samplerate
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        self.channels = channels
        self.resample_to_target = resample_to_target

    def get_supported_sample_rates(self, device_index):
        """Test which standard sample rates are supported by the specified device."""
        standard_rates = [8000, 9600, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]
        supported_rates = []

        device_info = self.audio_interface.get_device_info_by_index(device_index)
        max_channels = device_info.get('maxInputChannels')  # Changed from maxOutputChannels

        for rate in standard_rates:
            try:
                if self.audio_interface.is_format_supported(
                    rate,
                    input_device=device_index,  # Changed to input_device
                    input_channels=max_channels,  # Changed to input_channels
                    input_format=self.audio_format,  # Changed to input_format
                ):
                    supported_rates.append(rate)
            except:
                continue
        return supported_rates

    def _get_best_sample_rate(self, actual_device_index, desired_rate):
        """Determines the best available sample rate for the device."""
        try:
            device_info = self.audio_interface.get_device_info_by_index(actual_device_index)
            supported_rates = self.get_supported_sample_rates(actual_device_index)

            if desired_rate in supported_rates:
                return desired_rate

            return max(supported_rates)

            # lower_rates = [r for r in supported_rates if r <= desired_rate]
            # if lower_rates:
            #     return max(lower_rates)

            # higher_rates = [r for r in supported_rates if r > desired_rate]
            # if higher_rates:
            #     return min(higher_rates)

            return int(device_info.get('defaultSampleRate', 44100))

        except Exception as e:
            logging.warning(f"Error determining sample rate: {e}")
            return 44100  # Safe fallback

    def list_devices(self):
        """List all available audio input devices with supported sample rates."""
        try:
            init()  # Initialize colorama
            self.audio_interface = pyaudio.PyAudio()
            device_count = self.audio_interface.get_device_count()

            print(f"Available audio input devices:")
            #print(f"{Fore.LIGHTBLUE_EX}Available audio input devices:{Style.RESET_ALL}")
            for i in range(device_count):
                device_info = self.audio_interface.get_device_info_by_index(i)
                device_name = device_info.get('name')
                max_input_channels = device_info.get('maxInputChannels', 0)

                if max_input_channels > 0:  # Only consider devices with input capabilities
                    supported_rates = self.get_supported_sample_rates(i)
                    print(f"{Fore.LIGHTGREEN_EX}Device {Style.RESET_ALL}{i}{Fore.LIGHTGREEN_EX}: {device_name}{Style.RESET_ALL}")
                    
                    # Format each rate in cyan
                    if supported_rates:
                        rates_formatted = ", ".join([f"{Fore.CYAN}{rate}{Style.RESET_ALL}" for rate in supported_rates])
                        print(f"  {Fore.YELLOW}Supported sample rates: {rates_formatted}{Style.RESET_ALL}")
                    else:
                        print(f"  {Fore.YELLOW}Supported sample rates: None{Style.RESET_ALL}")

        except Exception as e:
            print(f"Error listing devices: {e}")
        finally:
            if self.audio_interface:
                self.audio_interface.terminate()

    def setup(self):
        """Initialize audio interface and open stream"""
        try:
            self.audio_interface = pyaudio.PyAudio()

            if self.debug_mode:
                print(f"Input device index: {self.input_device_index}")
            actual_device_index = (self.input_device_index if self.input_device_index is not None 
                                else self.audio_interface.get_default_input_device_info()['index'])
            
            if self.debug_mode:
                print(f"Actual selected device index: {actual_device_index}")
            self.input_device_index = actual_device_index
            self.device_sample_rate = self._get_best_sample_rate(actual_device_index, self.target_samplerate)

            if self.debug_mode:
                print(f"Setting up audio on device {self.input_device_index} with sample rate {self.device_sample_rate}")

            try:
                self.stream = self.audio_interface.open(
                    format=self.audio_format,
                    channels=self.channels,
                    rate=self.device_sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    input_device_index=self.input_device_index,
                )
                if self.debug_mode:
                    print(f"Audio recording initialized successfully at {self.device_sample_rate} Hz")
                return True
            except Exception as e:
                print(f"Failed to initialize audio stream at {self.device_sample_rate} Hz: {e}")
                return False

        except Exception as e:
            print(f"Error initializing audio recording: {e}")
            if self.audio_interface:
                self.audio_interface.terminate()
            return False

    def lowpass_filter(self, signal, cutoff_freq, sample_rate):
        """
        Apply a low-pass Butterworth filter to prevent aliasing in the signal.

        Args:
            signal (np.ndarray): Input audio signal to filter
            cutoff_freq (float): Cutoff frequency in Hz
            sample_rate (float): Sampling rate of the input signal in Hz

        Returns:
            np.ndarray: Filtered audio signal

        Notes:
            - Uses a 5th order Butterworth filter
            - Applies zero-phase filtering using filtfilt
        """
        # Calculate the Nyquist frequency (half the sample rate)
        nyquist_rate = sample_rate / 2.0

        # Normalize cutoff frequency to Nyquist rate (required by butter())
        normal_cutoff = cutoff_freq / nyquist_rate

        # Design the Butterworth filter
        b, a = butter(5, normal_cutoff, btype='low', analog=False)

        # Apply zero-phase filtering (forward and backward)
        filtered_signal = filtfilt(b, a, signal)
        return filtered_signal

    def resample_audio(self, pcm_data, target_sample_rate, original_sample_rate):
        """
        Filter and resample audio data to a target sample rate.

        Args:
            pcm_data (np.ndarray): Input audio data
            target_sample_rate (int): Desired output sample rate in Hz
            original_sample_rate (int): Original sample rate of input in Hz

        Returns:
            np.ndarray: Resampled audio data

        Notes:
            - Applies anti-aliasing filter before resampling
            - Uses polyphase filtering for high-quality resampling
        """
        if target_sample_rate < original_sample_rate:
            # Downsampling with low-pass filter
            pcm_filtered = self.lowpass_filter(pcm_data, target_sample_rate / 2, original_sample_rate)
            resampled = resample_poly(pcm_filtered, target_sample_rate, original_sample_rate)
        else:
            # Upsampling without low-pass filter
            resampled = resample_poly(pcm_data, target_sample_rate, original_sample_rate)
        return resampled

    def read_chunk(self):
        """Read a chunk of audio data"""
        return self.stream.read(self.chunk_size, exception_on_overflow=False)

    def cleanup(self):
        """Clean up audio resources"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            if self.audio_interface:
                self.audio_interface.terminate()
                self.audio_interface = None
        except Exception as e:
            print(f"Error cleaning up audio resources: {e}")
````

## File: RealtimeSTT/audio_recorder_client.py
````python
log_outgoing_chunks = False
debug_mode = False

from typing import Iterable, List, Optional, Union
from urllib.parse import urlparse
from datetime import datetime
from websocket import WebSocketApp
from websocket import ABNF
import numpy as np
import subprocess
import threading
import platform
import logging
import struct
import base64
import wave
import json
import time
import sys
import os

# Import the AudioInput class
from .audio_input import AudioInput

DEFAULT_CONTROL_URL = "ws://127.0.0.1:8011"
DEFAULT_DATA_URL = "ws://127.0.0.1:8012"

INIT_MODEL_TRANSCRIPTION = "tiny"
INIT_MODEL_TRANSCRIPTION_REALTIME = "tiny"
INIT_REALTIME_PROCESSING_PAUSE = 0.2
INIT_REALTIME_INITIAL_PAUSE = 0.2
INIT_SILERO_SENSITIVITY = 0.4
INIT_WEBRTC_SENSITIVITY = 3
INIT_POST_SPEECH_SILENCE_DURATION = 0.6
INIT_MIN_LENGTH_OF_RECORDING = 0.5
INIT_MIN_GAP_BETWEEN_RECORDINGS = 0
INIT_WAKE_WORDS_SENSITIVITY = 0.6
INIT_PRE_RECORDING_BUFFER_DURATION = 1.0
INIT_WAKE_WORD_ACTIVATION_DELAY = 0.0
INIT_WAKE_WORD_TIMEOUT = 5.0
INIT_WAKE_WORD_BUFFER_DURATION = 0.1
ALLOWED_LATENCY_LIMIT = 100

BUFFER_SIZE = 512
SAMPLE_RATE = 16000

INIT_HANDLE_BUFFER_OVERFLOW = False
if platform.system() != 'Darwin':
    INIT_HANDLE_BUFFER_OVERFLOW = True

# Define ANSI color codes for terminal output
class bcolors:
    HEADER = '\033[95m'   # Magenta
    OKBLUE = '\033[94m'   # Blue
    OKCYAN = '\033[96m'   # Cyan
    OKGREEN = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    FAIL = '\033[91m'     # Red
    ENDC = '\033[0m'      # Reset to default
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def format_timestamp_ns(timestamp_ns: int) -> str:
    # Split into whole seconds and the nanosecond remainder
    seconds = timestamp_ns // 1_000_000_000
    remainder_ns = timestamp_ns % 1_000_000_000

    # Convert seconds part into a datetime object (local time)
    dt = datetime.fromtimestamp(seconds)

    # Format the main time as HH:MM:SS
    time_str = dt.strftime("%H:%M:%S")

    # For instance, if you want milliseconds, divide the remainder by 1e6 and format as 3-digit
    milliseconds = remainder_ns // 1_000_000
    formatted_timestamp = f"{time_str}.{milliseconds:03d}"

    return formatted_timestamp

class AudioToTextRecorderClient:
    """
    A class responsible for capturing audio from the microphone, detecting
    voice activity, and then transcribing the captured audio using the
    `faster_whisper` model.
    """

    def __init__(self,
                 model: str = INIT_MODEL_TRANSCRIPTION,
                 download_root: str = None, 
                 language: str = "",
                 compute_type: str = "default",
                 input_device_index: int = None,
                 gpu_device_index: Union[int, List[int]] = 0,
                 device: str = "cuda",
                 on_recording_start=None,
                 on_recording_stop=None,
                 on_transcription_start=None,
                 ensure_sentence_starting_uppercase=True,
                 ensure_sentence_ends_with_period=True,
                 use_microphone=True,
                 spinner=True,
                 level=logging.WARNING,
                 batch_size: int = 16,

                 # Realtime transcription parameters
                 enable_realtime_transcription=False,
                 use_main_model_for_realtime=False,
                 realtime_model_type=INIT_MODEL_TRANSCRIPTION_REALTIME,
                 realtime_processing_pause=INIT_REALTIME_PROCESSING_PAUSE,
                 init_realtime_after_seconds=INIT_REALTIME_INITIAL_PAUSE,
                 on_realtime_transcription_update=None,
                 on_realtime_transcription_stabilized=None,
                 realtime_batch_size: int = 16,

                 # Voice activation parameters
                 silero_sensitivity: float = INIT_SILERO_SENSITIVITY,
                 silero_use_onnx: bool = False,
                 silero_deactivity_detection: bool = False,
                 webrtc_sensitivity: int = INIT_WEBRTC_SENSITIVITY,
                 post_speech_silence_duration: float = (
                     INIT_POST_SPEECH_SILENCE_DURATION
                 ),
                 min_length_of_recording: float = (
                     INIT_MIN_LENGTH_OF_RECORDING
                 ),
                 min_gap_between_recordings: float = (
                     INIT_MIN_GAP_BETWEEN_RECORDINGS
                 ),
                 pre_recording_buffer_duration: float = (
                     INIT_PRE_RECORDING_BUFFER_DURATION
                 ),
                 on_vad_start=None,
                 on_vad_stop=None,
                 on_vad_detect_start=None,
                 on_vad_detect_stop=None,
                 on_turn_detection_start=None,
                 on_turn_detection_stop=None,

                 # Wake word parameters
                 wakeword_backend: str = "pvporcupine",
                 openwakeword_model_paths: str = None,
                 openwakeword_inference_framework: str = "onnx",
                 wake_words: str = "",
                 wake_words_sensitivity: float = INIT_WAKE_WORDS_SENSITIVITY,
                 wake_word_activation_delay: float = (
                    INIT_WAKE_WORD_ACTIVATION_DELAY
                 ),
                 wake_word_timeout: float = INIT_WAKE_WORD_TIMEOUT,
                 wake_word_buffer_duration: float = INIT_WAKE_WORD_BUFFER_DURATION,
                 on_wakeword_detected=None,
                 on_wakeword_timeout=None,
                 on_wakeword_detection_start=None,
                 on_wakeword_detection_end=None,
                 on_recorded_chunk=None,
                 debug_mode=False,
                 handle_buffer_overflow: bool = INIT_HANDLE_BUFFER_OVERFLOW,
                 beam_size: int = 5,
                 beam_size_realtime: int = 3,
                 buffer_size: int = BUFFER_SIZE,
                 sample_rate: int = SAMPLE_RATE,
                 initial_prompt: Optional[Union[str, Iterable[int]]] = None,
                 initial_prompt_realtime: Optional[Union[str, Iterable[int]]] = None,
                 suppress_tokens: Optional[List[int]] = [-1],
                 print_transcription_time: bool = False,
                 early_transcription_on_silence: int = 0,
                 allowed_latency_limit: int = ALLOWED_LATENCY_LIMIT,
                 no_log_file: bool = False,
                 use_extended_logging: bool = False,

                 # Server urls
                 control_url: str = DEFAULT_CONTROL_URL,
                 data_url: str = DEFAULT_DATA_URL,
                 autostart_server: bool = True,
                 output_wav_file: str = None,
                 faster_whisper_vad_filter: bool = False,
                 ):

        # Set instance variables from constructor parameters
        self.model = model
        self.language = language
        self.compute_type = compute_type
        self.input_device_index = input_device_index
        self.gpu_device_index = gpu_device_index
        self.device = device
        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        self.on_transcription_start = on_transcription_start
        self.ensure_sentence_starting_uppercase = ensure_sentence_starting_uppercase
        self.ensure_sentence_ends_with_period = ensure_sentence_ends_with_period
        self.use_microphone = use_microphone
        self.spinner = spinner
        self.level = level
        self.batch_size = batch_size
        self.init_realtime_after_seconds = init_realtime_after_seconds
        self.realtime_batch_size = realtime_batch_size

        # Real-time transcription parameters
        self.enable_realtime_transcription = enable_realtime_transcription
        self.use_main_model_for_realtime = use_main_model_for_realtime
        self.download_root = download_root
        self.realtime_model_type = realtime_model_type
        self.realtime_processing_pause = realtime_processing_pause
        self.on_realtime_transcription_update = on_realtime_transcription_update
        self.on_realtime_transcription_stabilized = on_realtime_transcription_stabilized

        # Voice activation parameters
        self.silero_sensitivity = silero_sensitivity
        self.silero_use_onnx = silero_use_onnx
        self.silero_deactivity_detection = silero_deactivity_detection
        self.webrtc_sensitivity = webrtc_sensitivity
        self.post_speech_silence_duration = post_speech_silence_duration
        self.min_length_of_recording = min_length_of_recording
        self.min_gap_between_recordings = min_gap_between_recordings
        self.pre_recording_buffer_duration = pre_recording_buffer_duration

        self.on_vad_start = on_vad_start
        self.on_vad_stop = on_vad_stop
        self.on_vad_detect_start = on_vad_detect_start
        self.on_vad_detect_stop = on_vad_detect_stop
        self.on_turn_detection_start = on_turn_detection_start
        self.on_turn_detection_stop = on_turn_detection_stop

        # Wake word parameters
        self.wakeword_backend = wakeword_backend
        self.openwakeword_model_paths = openwakeword_model_paths
        self.openwakeword_inference_framework = openwakeword_inference_framework
        self.wake_words = wake_words
        self.wake_words_sensitivity = wake_words_sensitivity
        self.wake_word_activation_delay = wake_word_activation_delay
        self.wake_word_timeout = wake_word_timeout
        self.wake_word_buffer_duration = wake_word_buffer_duration
        self.on_wakeword_detected = on_wakeword_detected
        self.on_wakeword_timeout = on_wakeword_timeout
        self.on_wakeword_detection_start = on_wakeword_detection_start
        self.on_wakeword_detection_end = on_wakeword_detection_end
        self.on_recorded_chunk = on_recorded_chunk
        self.debug_mode = debug_mode
        self.handle_buffer_overflow = handle_buffer_overflow
        self.beam_size = beam_size
        self.beam_size_realtime = beam_size_realtime
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.initial_prompt = initial_prompt
        self.initial_prompt_realtime = initial_prompt_realtime
        self.suppress_tokens = suppress_tokens
        self.print_transcription_time = print_transcription_time
        self.early_transcription_on_silence = early_transcription_on_silence
        self.allowed_latency_limit = allowed_latency_limit
        self.no_log_file = no_log_file
        self.use_extended_logging = use_extended_logging
        self.faster_whisper_vad_filter = faster_whisper_vad_filter

        # Server URLs
        self.control_url = control_url
        self.data_url = data_url
        self.autostart_server = autostart_server
        self.output_wav_file = output_wav_file

        # Instance variables
        self.muted = False
        self.recording_thread = None
        self.is_running = True
        self.connection_established = threading.Event()
        self.recording_start = threading.Event()
        self.final_text_ready = threading.Event()
        self.realtime_text = ""
        self.final_text = ""
        self._recording = False
        self.server_already_running = False
        self.wav_file = None

        self.request_counter = 0
        self.pending_requests = {}  # Map from request_id to threading.Event and value

        if self.debug_mode:
            print("Checking STT server")
        if not self.connect():
            print("Failed to connect to the server.", file=sys.stderr)
        else:
            if self.debug_mode:
                print("STT server is running and connected.")

        if self.use_microphone:
            self.start_recording()


        if self.server_already_running:
            if not self.connection_established.wait(timeout=10):
                print("Server connection not established within 10 seconds.")
            else:
                self.set_parameter("language", self.language)
                print(f"Language set to {self.language}")
                self.set_parameter("wake_word_activation_delay", self.wake_word_activation_delay)
                print(f"Wake word activation delay set to {self.wake_word_activation_delay}")

    def text(self, on_transcription_finished=None):
        self.realtime_text = ""
        self.submitted_realtime_text = ""
        self.final_text = ""
        self.final_text_ready.clear()

        self.recording_start.set()

        try:
            total_wait_time = 0
            wait_interval = 0.02  # Wait in small intervals, e.g., 100ms
            max_wait_time = 60  # Timeout after 60 seconds

            while total_wait_time < max_wait_time and self.is_running and self._recording:
                if self.final_text_ready.wait(timeout=wait_interval):
                    break  # Break if transcription is ready

                if not self.is_running or not self._recording:
                    break
                
                total_wait_time += wait_interval

                # Check if a manual interrupt has occurred
                if total_wait_time >= max_wait_time:
                    if self.debug_mode:
                        print("Timeout while waiting for text from the server.")
                    self.recording_start.clear()
                    if on_transcription_finished:
                        threading.Thread(target=on_transcription_finished, args=("",)).start()
                    return ""

            self.recording_start.clear()

            if not self.is_running or not self._recording:
                return ""

            if on_transcription_finished:
                threading.Thread(target=on_transcription_finished, args=(self.final_text,)).start()

            return self.final_text

        except KeyboardInterrupt:
            if self.debug_mode:
                print("KeyboardInterrupt in text(), exiting...")
            raise KeyboardInterrupt

        except Exception as e:
            print(f"Error in AudioToTextRecorderClient.text(): {e}")
            return ""

    def feed_audio(self, chunk, audio_meta_data, original_sample_rate=16000):
        # Start with the base metadata
        metadata = {"sampleRate": original_sample_rate}

        # Merge additional metadata if provided
        if audio_meta_data:
            server_sent_to_stt_ns = time.time_ns()
            audio_meta_data["server_sent_to_stt"] = server_sent_to_stt_ns
            metadata["server_sent_to_stt_formatted"] = format_timestamp_ns(server_sent_to_stt_ns)

            metadata.update(audio_meta_data)

        # Convert metadata to JSON and prepare the message
        metadata_json = json.dumps(metadata)
        metadata_length = len(metadata_json)
        message = struct.pack('<I', metadata_length) + metadata_json.encode('utf-8') + chunk

        # Send the message if the connection is running
        if self.is_running:
            self.data_ws.send(message, opcode=ABNF.OPCODE_BINARY)

    def set_microphone(self, microphone_on=True):
        """
        Set the microphone on or off.
        """
        self.muted = not microphone_on

    def abort(self):
        self.call_method("abort")

    def wakeup(self):
        self.call_method("wakeup")

    def clear_audio_queue(self):
        self.call_method("clear_audio_queue")

    def perform_final_transcription(self):
        self.call_method("perform_final_transcription")

    def stop(self):
        self.call_method("stop")

    def connect(self):
        if not self.ensure_server_running():
            print("Cannot start STT server. Exiting.")
            return False

        try:
            # Connect to control WebSocket
            self.control_ws = WebSocketApp(self.control_url,
                                                     on_message=self.on_control_message,
                                                     on_error=self.on_error,
                                                     on_close=self.on_close,
                                                     on_open=self.on_control_open)

            self.control_ws_thread = threading.Thread(target=self.control_ws.run_forever)
            self.control_ws_thread.daemon = False
            self.control_ws_thread.start()

            # Connect to data WebSocket
            self.data_ws = WebSocketApp(self.data_url,
                                                  on_message=self.on_data_message,
                                                  on_error=self.on_error,
                                                  on_close=self.on_close,
                                                  on_open=self.on_data_open)

            self.data_ws_thread = threading.Thread(target=self.data_ws.run_forever)
            self.data_ws_thread.daemon = False
            self.data_ws_thread.start()

            # Wait for the connections to be established
            if not self.connection_established.wait(timeout=10):
                print("Timeout while connecting to the server.")
                return False

            if self.debug_mode:
                print("WebSocket connections established successfully.")
            return True
        except Exception as e:
            print(f"Error while connecting to the server: {e}")
            return False

    def start_server(self):
        args = ['stt-server']

        # Map constructor parameters to server arguments
        if self.model:
            args += ['--model', self.model]
        if self.realtime_model_type:
            args += ['--realtime_model_type', self.realtime_model_type]
        if self.download_root:
            args += ['--root', self.download_root]
        if self.batch_size is not None:
            args += ['--batch', str(self.batch_size)]
        if self.realtime_batch_size is not None:
            args += ['--realtime_batch_size', str(self.realtime_batch_size)]
        if self.init_realtime_after_seconds is not None:
            args += ['--init_realtime_after_seconds', str(self.init_realtime_after_seconds)]
        if self.initial_prompt_realtime:
            sanitized_prompt = self.initial_prompt_realtime.replace("\n", "\\n")
            args += ['--initial_prompt_realtime', sanitized_prompt]

        # if self.compute_type:
        #     args += ['--compute_type', self.compute_type]
        # if self.input_device_index is not None:
        #     args += ['--input_device_index', str(self.input_device_index)]
        # if self.gpu_device_index is not None:
        #     args += ['--gpu_device_index', str(self.gpu_device_index)]
        # if self.device:
        #     args += ['--device', self.device]
        # if self.spinner:
        #     args.append('--spinner')  # flag, no need for True/False
        # if self.enable_realtime_transcription:
        #     args.append('--enable_realtime_transcription')  # flag, no need for True/False
        # if self.handle_buffer_overflow:
        #     args.append('--handle_buffer_overflow')  # flag, no need for True/False
        # if self.suppress_tokens:
        #     args += ['--suppress_tokens', str(self.suppress_tokens)]
        # if self.print_transcription_time:
        #     args.append('--print_transcription_time')  # flag, no need for True/False
        # if self.allowed_latency_limit is not None:
        #     args += ['--allowed_latency_limit', str(self.allowed_latency_limit)]
        # if self.no_log_file:
        #     args.append('--no_log_file')  # flag, no need for True
        if self.debug_mode:
            args.append('--debug')  # flag, no need for True/False
            
        if self.language:
            args += ['--language', self.language]
        if self.silero_sensitivity is not None:
            args += ['--silero_sensitivity', str(self.silero_sensitivity)]
        if self.silero_use_onnx:
            args.append('--silero_use_onnx')  # flag, no need for True/False
        if self.webrtc_sensitivity is not None:
            args += ['--webrtc_sensitivity', str(self.webrtc_sensitivity)]
        if self.min_length_of_recording is not None:
            args += ['--min_length_of_recording', str(self.min_length_of_recording)]
        if self.min_gap_between_recordings is not None:
            args += ['--min_gap_between_recordings', str(self.min_gap_between_recordings)]
        if self.realtime_processing_pause is not None:
            args += ['--realtime_processing_pause', str(self.realtime_processing_pause)]
        if self.early_transcription_on_silence is not None:
            args += ['--early_transcription_on_silence', str(self.early_transcription_on_silence)]
        if self.silero_deactivity_detection:
            args.append('--silero_deactivity_detection')  # flag, no need for True/False
        if self.beam_size is not None:
            args += ['--beam_size', str(self.beam_size)]
        if self.beam_size_realtime is not None:
            args += ['--beam_size_realtime', str(self.beam_size_realtime)]
        if self.wake_words is not None:
            args += ['--wake_words', str(self.wake_words)]
        if self.wake_words_sensitivity is not None:
            args += ['--wake_words_sensitivity', str(self.wake_words_sensitivity)]
        if self.wake_word_timeout is not None:
            args += ['--wake_word_timeout', str(self.wake_word_timeout)]
        if self.wake_word_activation_delay is not None:
            args += ['--wake_word_activation_delay', str(self.wake_word_activation_delay)]
        if self.wakeword_backend is not None:
            args += ['--wakeword_backend', str(self.wakeword_backend)]
        if self.openwakeword_model_paths:
            args += ['--openwakeword_model_paths', str(self.openwakeword_model_paths)]
        if self.openwakeword_inference_framework is not None:
            args += ['--openwakeword_inference_framework', str(self.openwakeword_inference_framework)]
        if self.wake_word_buffer_duration is not None:
            args += ['--wake_word_buffer_duration', str(self.wake_word_buffer_duration)]
        if self.use_main_model_for_realtime:
            args.append('--use_main_model_for_realtime')  # flag, no need for True/False
        if self.use_extended_logging:
            args.append('--use_extended_logging')  # flag, no need for True/False

        if self.control_url:
            parsed_control_url = urlparse(self.control_url)
            if parsed_control_url.port:
                args += ['--control_port', str(parsed_control_url.port)]
        if self.data_url:
            parsed_data_url = urlparse(self.data_url)
            if parsed_data_url.port:
                args += ['--data_port', str(parsed_data_url.port)]
        if self.initial_prompt:
            sanitized_prompt = self.initial_prompt.replace("\n", "\\n")
            args += ['--initial_prompt', sanitized_prompt]

        # Start the subprocess with the mapped arguments
        if os.name == 'nt':  # Windows
            cmd = 'start /min cmd /c ' + subprocess.list2cmdline(args)
            if debug_mode:
                print(f"Opening server with cli command: {cmd}")
            subprocess.Popen(cmd, shell=True)
        else:  # Unix-like systems
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        print("STT server start command issued. Please wait a moment for it to initialize.", file=sys.stderr)

    def is_server_running(self):
        try:
            # Attempt a proper WebSocket handshake to the control URL.
            from websocket import create_connection
            ws = create_connection(self.control_url, timeout=3)
            ws.close()
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"Server connectivity check failed: {e}")
            return False

    def ensure_server_running(self):
        if not self.is_server_running():
            if self.debug_mode:
                print("STT server is not running.", file=sys.stderr)
            if self.autostart_server:
                self.start_server()
                if self.debug_mode:
                    print("Waiting for STT server to start...", file=sys.stderr)
                for _ in range(20):  # Wait up to 20 seconds
                    if self.is_server_running():
                        if self.debug_mode:
                            print("STT server started successfully.", file=sys.stderr)
                        time.sleep(2)  # Give the server a moment to fully initialize
                        return True
                    time.sleep(1)
                print("Failed to start STT server.", file=sys.stderr)
                return False
            else:
                print("STT server is required. Please start it manually.", file=sys.stderr)
                return False
        
        else:
            self.server_already_running = True

        return True
    
    def list_devices(self):
        """List all available audio input devices."""
        audio = AudioInput(debug_mode=self.debug_mode)
        audio.list_devices()

    def start_recording(self):
        self.recording_thread = threading.Thread(target=self.record_and_send_audio)
        self.recording_thread.daemon = False
        self.recording_thread.start()

    def setup_audio(self):
        """Initialize audio input"""
        self.audio_input = AudioInput(
            input_device_index=self.input_device_index,
            debug_mode=self.debug_mode
        )
        return self.audio_input.setup()

    def record_and_send_audio(self):
        """Record and stream audio data"""
        self._recording = True

        try:
            if not self.setup_audio():
                raise Exception("Failed to set up audio recording.")

            # Initialize WAV file writer if output_wav_file is provided
            if self.output_wav_file and not self.wav_file:
                self.wav_file = wave.open(self.output_wav_file, 'wb')
                self.wav_file.setnchannels(1)
                self.wav_file.setsampwidth(2)
                self.wav_file.setframerate(self.audio_input.device_sample_rate)  # Use self.device_sample_rate


            if self.debug_mode:
                print("Recording and sending audio...")

            while self.is_running:
                if self.muted:
                    time.sleep(0.01)
                    continue

                try:
                    audio_data = self.audio_input.read_chunk()

                    if self.wav_file:
                        self.wav_file.writeframes(audio_data)

                    if self.on_recorded_chunk:
                        self.on_recorded_chunk(audio_data)

                    if self.muted:
                        continue

                    if self.recording_start.is_set():
                        metadata = {"sampleRate": self.audio_input.device_sample_rate}
                        metadata_json = json.dumps(metadata)
                        metadata_length = len(metadata_json)
                        message = struct.pack('<I', metadata_length) + metadata_json.encode('utf-8') + audio_data

                        if self.is_running:
                            if log_outgoing_chunks:
                                print(".", flush=True, end='')
                            self.data_ws.send(message, opcode=ABNF.OPCODE_BINARY)
                except KeyboardInterrupt:
                    if self.debug_mode:
                        print("KeyboardInterrupt in record_and_send_audio, exiting...")
                    break
                except Exception as e:
                    print(f"Error sending audio data: {e}")
                    break

        except Exception as e:
            print(f"Error in record_and_send_audio: {e}", file=sys.stderr)
        finally:
            self.cleanup_audio()
            self.final_text_ready.set() # fake final text to stop the text() method
            self.is_running = False
            self._recording = False

    def cleanup_audio(self):
        """Clean up audio resources"""
        if hasattr(self, 'audio_input'):
            self.audio_input.cleanup()

    def on_control_message(self, ws, message):
        try:
            data = json.loads(message)
            # Handle server response with status
            if 'status' in data:
                if data['status'] == 'success':
                    if 'parameter' in data and 'value' in data:
                        request_id = data.get('request_id')
                        if request_id is not None and request_id in self.pending_requests:
                            if self.debug_mode:
                                print(f"Parameter {data['parameter']} = {data['value']}")
                            self.pending_requests[request_id]['value'] = data['value']
                            self.pending_requests[request_id]['event'].set()
                elif data['status'] == 'error':
                    print(f"Server Error: {data.get('message', '')}")
            else:
                print(f"Unknown control message format: {data}")
        except json.JSONDecodeError:
            print(f"Received non-JSON control message: {message}")
        except Exception as e:
            print(f"Error processing control message: {e}")

    # Handle real-time transcription and full sentence updates
    def on_data_message(self, ws, message):
        try:
            data = json.loads(message)
            # Handle real-time transcription updates
            if data.get('type') == 'realtime':
                if data['text'] != self.realtime_text:
                    self.realtime_text = data['text']

                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    # print(f"Realtime text [{timestamp}]: {bcolors.OKCYAN}{self.realtime_text}{bcolors.ENDC}")

                    if self.on_realtime_transcription_update:
                        # Call the callback in a new thread to avoid blocking
                        threading.Thread(
                            target=self.on_realtime_transcription_update,
                            args=(self.realtime_text,)
                        ).start()

            # Handle full sentences
            elif data.get('type') == 'fullSentence':
                self.final_text = data['text']
                self.final_text_ready.set()

            elif data.get('type') == 'recording_start':
                if self.on_recording_start:
                    self.on_recording_start()
            elif data.get('type') == 'recording_stop':
                if self.on_recording_stop:
                    self.on_recording_stop()
            elif data.get('type') == 'transcription_start':
                audio_bytes_base64 = data.get('audio_bytes_base64')
                decoded_bytes = base64.b64decode(audio_bytes_base64)

                # Reconstruct the np.int16 array from the decoded bytes
                audio_array = np.frombuffer(decoded_bytes, dtype=np.int16)

                # If the original data was normalized, convert to np.float32 and normalize
                INT16_MAX_ABS_VALUE = 32768.0
                normalized_audio = audio_array.astype(np.float32) / INT16_MAX_ABS_VALUE

                if self.on_transcription_start:
                    self.on_transcription_start(normalized_audio)
            elif data.get('type') == 'vad_detect_start':
                if self.on_vad_detect_start:
                    self.on_vad_detect_start()
            elif data.get('type') == 'vad_detect_stop':
                if self.on_vad_detect_stop:
                    self.on_vad_detect_stop()
            elif data.get('type') == 'vad_start':
                if self.on_vad_start:
                    self.on_vad_start()
            elif data.get('type') == 'vad_stop':
                if self.on_vad_stop:
                    self.on_vad_stop()
            elif data.get('type') == 'start_turn_detection':
                if self.on_turn_detection_start:
                    self.on_turn_detection_start()
            elif data.get('type') == 'stop_turn_detection':
                if self.on_turn_detection_stop:
                    self.on_turn_detection_stop()
            elif data.get('type') == 'wakeword_detected':
                if self.on_wakeword_detected:
                    self.on_wakeword_detected()
            elif data.get('type') == 'wakeword_detection_start':
                if self.on_wakeword_detection_start:
                    self.on_wakeword_detection_start()
            elif data.get('type') == 'wakeword_detection_end':
                if self.on_wakeword_detection_end:
                    self.on_wakeword_detection_end()
            elif data.get('type') == 'recorded_chunk':
                pass

            else:
                print(f"Unknown data message format: {data}")

        except json.JSONDecodeError:
            print(f"Received non-JSON data message: {message}")
        except Exception as e:
            print(f"Error processing data message: {e}")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        if self.debug_mode:
            if ws == self.data_ws:
                print(f"Data WebSocket connection closed: {close_status_code} - {close_msg}")
            elif ws == self.control_ws:
                print(f"Control WebSocket connection closed: {close_status_code} - {close_msg}")
        
        self.is_running = False

    def on_control_open(self, ws):
        if self.debug_mode:
            print("Control WebSocket connection opened.")
        self.connection_established.set()

    def on_data_open(self, ws):
        if self.debug_mode:
            print("Data WebSocket connection opened.")

    def set_parameter(self, parameter, value):
        command = {
            "command": "set_parameter",
            "parameter": parameter,
            "value": value
        }
        self.control_ws.send(json.dumps(command))

    def get_parameter(self, parameter):
        # Generate a unique request_id
        request_id = self.request_counter
        self.request_counter += 1

        # Prepare the command with the request_id
        command = {
            "command": "get_parameter",
            "parameter": parameter,
            "request_id": request_id
        }

        # Create an event to wait for the response
        event = threading.Event()
        self.pending_requests[request_id] = {'event': event, 'value': None}

        # Send the command to the server
        self.control_ws.send(json.dumps(command))

        # Wait for the response or timeout after 5 seconds
        if event.wait(timeout=5):
            value = self.pending_requests[request_id]['value']
            # Clean up the pending request
            del self.pending_requests[request_id]
            return value
        else:
            print(f"Timeout waiting for get_parameter {parameter}")
            # Clean up the pending request
            del self.pending_requests[request_id]
            return None

    def call_method(self, method, args=None, kwargs=None):
        command = {
            "command": "call_method",
            "method": method,
            "args": args or [],
            "kwargs": kwargs or {}
        }
        self.control_ws.send(json.dumps(command))

    def shutdown(self):
        """Shutdown all resources"""
        self.is_running = False
        if self.control_ws:
            self.control_ws.close()
        if self.data_ws:
            self.data_ws.close()

        # Join threads
        if self.control_ws_thread:
            self.control_ws_thread.join()
        if self.data_ws_thread:
            self.data_ws_thread.join()
        if self.recording_thread:
            self.recording_thread.join()

        # Clean up audio
        self.cleanup_audio()

    def __enter__(self):
        """
        Method to setup the context manager protocol.

        This enables the instance to be used in a `with` statement, ensuring
        proper resource management. When the `with` block is entered, this
        method is automatically called.

        Returns:
            self: The current instance of the class.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Method to define behavior when the context manager protocol exits.

        This is called when exiting the `with` block and ensures that any
        necessary cleanup or resource release processes are executed, such as
        shutting down the system properly.

        Args:
            exc_type (Exception or None): The type of the exception that
              caused the context to be exited, if any.
            exc_value (Exception or None): The exception instance that caused
              the context to be exited, if any.
            traceback (Traceback or None): The traceback corresponding to the
              exception, if any.
        """
        self.shutdown()
````

## File: RealtimeSTT/audio_recorder.py
````python
"""

The AudioToTextRecorder class in the provided code facilitates
fast speech-to-text transcription.

The class employs the faster_whisper library to transcribe the recorded audio
into text using machine learning models, which can be run either on a GPU or
CPU. Voice activity detection (VAD) is built in, meaning the software can
automatically start or stop recording based on the presence or absence of
speech. It integrates wake word detection through the pvporcupine library,
allowing the software to initiate recording when a specific word or phrase
is spoken. The system provides real-time feedback and can be further
customized.

Features:
- Voice Activity Detection: Automatically starts/stops recording when speech
  is detected or when speech ends.
- Wake Word Detection: Starts recording when a specified wake word (or words)
  is detected.
- Event Callbacks: Customizable callbacks for when recording starts
  or finishes.
- Fast Transcription: Returns the transcribed text from the audio as fast
  as possible.

Author: Kolja Beigel

"""

from faster_whisper import WhisperModel, BatchedInferencePipeline
from typing import Iterable, List, Optional, Union
from openwakeword.model import Model
import torch.multiprocessing as mp
from scipy.signal import resample
import signal as system_signal
from ctypes import c_bool
from scipy import signal
from .safepipe import SafePipe
import soundfile as sf
import faster_whisper
import openwakeword
import collections
import numpy as np
import pvporcupine
import traceback
import threading
import webrtcvad
import datetime
import platform
import logging
import struct
import base64
import queue
import torch
import halo
import time
import copy
import os
import re
import gc

# Named logger for this module.
logger = logging.getLogger("realtimestt")
logger.propagate = False

# Set OpenMP runtime duplicate library handling to OK (Use only for development!)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

INIT_MODEL_TRANSCRIPTION = "tiny"
INIT_MODEL_TRANSCRIPTION_REALTIME = "tiny"
INIT_REALTIME_PROCESSING_PAUSE = 0.2
INIT_REALTIME_INITIAL_PAUSE = 0.2
INIT_SILERO_SENSITIVITY = 0.4
INIT_WEBRTC_SENSITIVITY = 3
INIT_POST_SPEECH_SILENCE_DURATION = 0.6
INIT_MIN_LENGTH_OF_RECORDING = 0.5
INIT_MIN_GAP_BETWEEN_RECORDINGS = 0
INIT_WAKE_WORDS_SENSITIVITY = 0.6
INIT_PRE_RECORDING_BUFFER_DURATION = 1.0
INIT_WAKE_WORD_ACTIVATION_DELAY = 0.0
INIT_WAKE_WORD_TIMEOUT = 5.0
INIT_WAKE_WORD_BUFFER_DURATION = 0.1
ALLOWED_LATENCY_LIMIT = 100

TIME_SLEEP = 0.02
SAMPLE_RATE = 16000
BUFFER_SIZE = 512
INT16_MAX_ABS_VALUE = 32768.0

INIT_HANDLE_BUFFER_OVERFLOW = False
if platform.system() != 'Darwin':
    INIT_HANDLE_BUFFER_OVERFLOW = True


class TranscriptionWorker:
    def __init__(self, conn, stdout_pipe, model_path, download_root, compute_type, gpu_device_index, device,
                 ready_event, shutdown_event, interrupt_stop_event, beam_size, initial_prompt, suppress_tokens,
                 batch_size, faster_whisper_vad_filter, normalize_audio):
        self.conn = conn
        self.stdout_pipe = stdout_pipe
        self.model_path = model_path
        self.download_root = download_root
        self.compute_type = compute_type
        self.gpu_device_index = gpu_device_index
        self.device = device
        self.ready_event = ready_event
        self.shutdown_event = shutdown_event
        self.interrupt_stop_event = interrupt_stop_event
        self.beam_size = beam_size
        self.initial_prompt = initial_prompt
        self.suppress_tokens = suppress_tokens
        self.batch_size = batch_size
        self.faster_whisper_vad_filter = faster_whisper_vad_filter
        self.normalize_audio = normalize_audio
        self.queue = queue.Queue()

    def custom_print(self, *args, **kwargs):
        message = ' '.join(map(str, args))
        try:
            self.stdout_pipe.send(message)
        except (BrokenPipeError, EOFError, OSError):
            pass

    def poll_connection(self):
        while not self.shutdown_event.is_set():
            try:
                # Use a longer timeout to reduce polling frequency
                if self.conn.poll(0.01):  # Increased from 0.01 to 0.5 seconds
                    data = self.conn.recv()
                    self.queue.put(data)
                else:
                    # Sleep only if no data, but use a shorter sleep
                    time.sleep(TIME_SLEEP)
            except Exception as e:
                logging.error(f"Error receiving data from connection: {e}", exc_info=True)
                time.sleep(TIME_SLEEP)

    def run(self):
        if __name__ == "__main__":
             system_signal.signal(system_signal.SIGINT, system_signal.SIG_IGN)
             __builtins__['print'] = self.custom_print

        logging.info(f"Initializing faster_whisper main transcription model {self.model_path}")

        try:
            model = faster_whisper.WhisperModel(
                model_size_or_path=self.model_path,
                device=self.device,
                compute_type=self.compute_type,
                device_index=self.gpu_device_index,
                download_root=self.download_root,
            )
            # Create a short dummy audio array, for example 1 second of silence at 16 kHz
            if self.batch_size > 0:
                model = BatchedInferencePipeline(model=model)

            # Run a warm-up transcription
            current_dir = os.path.dirname(os.path.realpath(__file__))
            warmup_audio_path = os.path.join(
                current_dir, "warmup_audio.wav"
            )
            warmup_audio_data, _ = sf.read(warmup_audio_path, dtype="float32")
            segments, info = model.transcribe(warmup_audio_data, language="en", beam_size=1)
            model_warmup_transcription = " ".join(segment.text for segment in segments)
        except Exception as e:
            logging.exception(f"Error initializing main faster_whisper transcription model: {e}")
            raise

        self.ready_event.set()
        logging.debug("Faster_whisper main speech to text transcription model initialized successfully")

        # Start the polling thread
        polling_thread = threading.Thread(target=self.poll_connection)
        polling_thread.start()

        try:
            while not self.shutdown_event.is_set():
                try:
                    audio, language, use_prompt = self.queue.get(timeout=0.1)
                    try:
                        logging.debug(f"Transcribing audio with language {language}")
                        start_t = time.time()

                        # normalize audio to -0.95 dBFS
                        if audio is not None and audio .size > 0:
                            if self.normalize_audio:
                                peak = np.max(np.abs(audio))
                                if peak > 0:
                                    audio = (audio / peak) * 0.95
                        else:
                            logging.error("Received None audio for transcription")
                            self.conn.send(('error', "Received None audio for transcription"))
                            continue

                        prompt = None
                        if use_prompt:
                            prompt = self.initial_prompt if self.initial_prompt else None

                        if self.batch_size > 0:
                            segments, info = model.transcribe(
                                audio,
                                language=language if language else None,
                                beam_size=self.beam_size,
                                initial_prompt=prompt,
                                suppress_tokens=self.suppress_tokens,
                                batch_size=self.batch_size, 
                                vad_filter=self.faster_whisper_vad_filter
                            )
                        else:
                            segments, info = model.transcribe(
                                audio,
                                language=language if language else None,
                                beam_size=self.beam_size,
                                initial_prompt=prompt,
                                suppress_tokens=self.suppress_tokens,
                                vad_filter=self.faster_whisper_vad_filter
                            )
                        elapsed = time.time() - start_t
                        transcription = " ".join(seg.text for seg in segments).strip()
                        logging.debug(f"Final text detected with main model: {transcription} in {elapsed:.4f}s")
                        self.conn.send(('success', (transcription, info)))
                    except Exception as e:
                        logging.error(f"General error in transcription: {e}", exc_info=True)
                        self.conn.send(('error', str(e)))
                except queue.Empty:
                    continue
                except KeyboardInterrupt:
                    self.interrupt_stop_event.set()
                    logging.debug("Transcription worker process finished due to KeyboardInterrupt")
                    break
                except Exception as e:
                    logging.error(f"General error in processing queue item: {e}", exc_info=True)
        finally:
            __builtins__['print'] = print  # Restore the original print function
            self.conn.close()
            self.stdout_pipe.close()
            self.shutdown_event.set()  # Ensure the polling thread will stop
            polling_thread.join()  # Wait for the polling thread to finish


class bcolors:
    OKGREEN = '\033[92m'  # Green for active speech detection
    WARNING = '\033[93m'  # Yellow for silence detection
    ENDC = '\033[0m'      # Reset to default color


class AudioToTextRecorder:
    """
    A class responsible for capturing audio from the microphone, detecting
    voice activity, and then transcribing the captured audio using the
    `faster_whisper` model.
    """

    def __init__(self,
                 model: str = INIT_MODEL_TRANSCRIPTION,
                 download_root: str = None, 
                 language: str = "",
                 compute_type: str = "default",
                 input_device_index: int = None,
                 gpu_device_index: Union[int, List[int]] = 0,
                 device: str = "cuda",
                 on_recording_start=None,
                 on_recording_stop=None,
                 on_transcription_start=None,
                 ensure_sentence_starting_uppercase=True,
                 ensure_sentence_ends_with_period=True,
                 use_microphone=True,
                 spinner=True,
                 level=logging.WARNING,
                 batch_size: int = 16,

                 # Realtime transcription parameters
                 enable_realtime_transcription=False,
                 use_main_model_for_realtime=False,
                 realtime_model_type=INIT_MODEL_TRANSCRIPTION_REALTIME,
                 realtime_processing_pause=INIT_REALTIME_PROCESSING_PAUSE,
                 init_realtime_after_seconds=INIT_REALTIME_INITIAL_PAUSE,
                 on_realtime_transcription_update=None,
                 on_realtime_transcription_stabilized=None,
                 realtime_batch_size: int = 16,

                 # Voice activation parameters
                 silero_sensitivity: float = INIT_SILERO_SENSITIVITY,
                 silero_use_onnx: bool = False,
                 silero_deactivity_detection: bool = False,
                 webrtc_sensitivity: int = INIT_WEBRTC_SENSITIVITY,
                 post_speech_silence_duration: float = (
                     INIT_POST_SPEECH_SILENCE_DURATION
                 ),
                 min_length_of_recording: float = (
                     INIT_MIN_LENGTH_OF_RECORDING
                 ),
                 min_gap_between_recordings: float = (
                     INIT_MIN_GAP_BETWEEN_RECORDINGS
                 ),
                 pre_recording_buffer_duration: float = (
                     INIT_PRE_RECORDING_BUFFER_DURATION
                 ),
                 on_vad_start=None,
                 on_vad_stop=None,
                 on_vad_detect_start=None,
                 on_vad_detect_stop=None,
                 on_turn_detection_start=None,
                 on_turn_detection_stop=None,

                 # Wake word parameters
                 wakeword_backend: str = "",
                 openwakeword_model_paths: str = None,
                 openwakeword_inference_framework: str = "onnx",
                 wake_words: str = "",
                 wake_words_sensitivity: float = INIT_WAKE_WORDS_SENSITIVITY,
                 wake_word_activation_delay: float = (
                    INIT_WAKE_WORD_ACTIVATION_DELAY
                 ),
                 wake_word_timeout: float = INIT_WAKE_WORD_TIMEOUT,
                 wake_word_buffer_duration: float = INIT_WAKE_WORD_BUFFER_DURATION,
                 on_wakeword_detected=None,
                 on_wakeword_timeout=None,
                 on_wakeword_detection_start=None,
                 on_wakeword_detection_end=None,
                 on_recorded_chunk=None,
                 debug_mode=False,
                 handle_buffer_overflow: bool = INIT_HANDLE_BUFFER_OVERFLOW,
                 beam_size: int = 5,
                 beam_size_realtime: int = 3,
                 buffer_size: int = BUFFER_SIZE,
                 sample_rate: int = SAMPLE_RATE,
                 initial_prompt: Optional[Union[str, Iterable[int]]] = None,
                 initial_prompt_realtime: Optional[Union[str, Iterable[int]]] = None,
                 suppress_tokens: Optional[List[int]] = [-1],
                 print_transcription_time: bool = False,
                 early_transcription_on_silence: int = 0,
                 allowed_latency_limit: int = ALLOWED_LATENCY_LIMIT,
                 no_log_file: bool = False,
                 use_extended_logging: bool = False,
                 faster_whisper_vad_filter: bool = True,
                 normalize_audio: bool = False,
                 start_callback_in_new_thread: bool = False,
                 ):
        """
        Initializes an audio recorder and  transcription
        and wake word detection.

        Args:
        - model (str, default="tiny"): Specifies the size of the transcription
            model to use or the path to a converted model directory.
            Valid options are 'tiny', 'tiny.en', 'base', 'base.en',
            'small', 'small.en', 'medium', 'medium.en', 'large-v1',
            'large-v2'.
            If a specific size is provided, the model is downloaded
            from the Hugging Face Hub.
        - download_root (str, default=None): Specifies the root path were the Whisper models 
          are downloaded to. When empty, the default is used. 
        - language (str, default=""): Language code for speech-to-text engine.
            If not specified, the model will attempt to detect the language
            automatically.
        - compute_type (str, default="default"): Specifies the type of
            computation to be used for transcription.
            See https://opennmt.net/CTranslate2/quantization.html.
        - input_device_index (int, default=0): The index of the audio input
            device to use.
        - gpu_device_index (int, default=0): Device ID to use.
            The model can also be loaded on multiple GPUs by passing a list of
            IDs (e.g. [0, 1, 2, 3]). In that case, multiple transcriptions can
            run in parallel when transcribe() is called from multiple Python
            threads
        - device (str, default="cuda"): Device for model to use. Can either be 
            "cuda" or "cpu".
        - on_recording_start (callable, default=None): Callback function to be
            called when recording of audio to be transcripted starts.
        - on_recording_stop (callable, default=None): Callback function to be
            called when recording of audio to be transcripted stops.
        - on_transcription_start (callable, default=None): Callback function
            to be called when transcription of audio to text starts.
        - ensure_sentence_starting_uppercase (bool, default=True): Ensures
            that every sentence detected by the algorithm starts with an
            uppercase letter.
        - ensure_sentence_ends_with_period (bool, default=True): Ensures that
            every sentence that doesn't end with punctuation such as "?", "!"
            ends with a period
        - use_microphone (bool, default=True): Specifies whether to use the
            microphone as the audio input source. If set to False, the
            audio input source will be the audio data sent through the
            feed_audio() method.
        - spinner (bool, default=True): Show spinner animation with current
            state.
        - level (int, default=logging.WARNING): Logging level.
        - batch_size (int, default=16): Batch size for the main transcription
        - enable_realtime_transcription (bool, default=False): Enables or
            disables real-time transcription of audio. When set to True, the
            audio will be transcribed continuously as it is being recorded.
        - use_main_model_for_realtime (str, default=False):
            If True, use the main transcription model for both regular and
            real-time transcription. If False, use a separate model specified
            by realtime_model_type for real-time transcription.
            Using a single model can save memory and potentially improve
            performance, but may not be optimized for real-time processing.
            Using separate models allows for a smaller, faster model for
            real-time transcription while keeping a more accurate model for
            final transcription.
        - realtime_model_type (str, default="tiny"): Specifies the machine
            learning model to be used for real-time transcription. Valid
            options include 'tiny', 'tiny.en', 'base', 'base.en', 'small',
            'small.en', 'medium', 'medium.en', 'large-v1', 'large-v2'.
        - realtime_processing_pause (float, default=0.1): Specifies the time
            interval in seconds after a chunk of audio gets transcribed. Lower
            values will result in more "real-time" (frequent) transcription
            updates but may increase computational load.
        - init_realtime_after_seconds (float, default=0.2): Specifies the 
            initial waiting time after the recording was initiated before
            yielding the first realtime transcription
        - on_realtime_transcription_update = A callback function that is
            triggered whenever there's an update in the real-time
            transcription. The function is called with the newly transcribed
            text as its argument.
        - on_realtime_transcription_stabilized = A callback function that is
            triggered when the transcribed text stabilizes in quality. The
            stabilized text is generally more accurate but may arrive with a
            slight delay compared to the regular real-time updates.
        - realtime_batch_size (int, default=16): Batch size for the real-time
            transcription model.
        - silero_sensitivity (float, default=SILERO_SENSITIVITY): Sensitivity
            for the Silero Voice Activity Detection model ranging from 0
            (least sensitive) to 1 (most sensitive). Default is 0.5.
        - silero_use_onnx (bool, default=False): Enables usage of the
            pre-trained model from Silero in the ONNX (Open Neural Network
            Exchange) format instead of the PyTorch format. This is
            recommended for faster performance.
        - silero_deactivity_detection (bool, default=False): Enables the Silero
            model for end-of-speech detection. More robust against background
            noise. Utilizes additional GPU resources but improves accuracy in
            noisy environments. When False, uses the default WebRTC VAD,
            which is more sensitive but may continue recording longer due
            to background sounds.
        - webrtc_sensitivity (int, default=WEBRTC_SENSITIVITY): Sensitivity
            for the WebRTC Voice Activity Detection engine ranging from 0
            (least aggressive / most sensitive) to 3 (most aggressive,
            least sensitive). Default is 3.
        - post_speech_silence_duration (float, default=0.2): Duration in
            seconds of silence that must follow speech before the recording
            is considered to be completed. This ensures that any brief
            pauses during speech don't prematurely end the recording.
        - min_gap_between_recordings (float, default=1.0): Specifies the
            minimum time interval in seconds that should exist between the
            end of one recording session and the beginning of another to
            prevent rapid consecutive recordings.
        - min_length_of_recording (float, default=1.0): Specifies the minimum
            duration in seconds that a recording session should last to ensure
            meaningful audio capture, preventing excessively short or
            fragmented recordings.
        - pre_recording_buffer_duration (float, default=0.2): Duration in
            seconds for the audio buffer to maintain pre-roll audio
            (compensates speech activity detection latency)
        - on_vad_start (callable, default=None): Callback function to be called
            when the system detected the start of voice activity presence.
        - on_vad_stop (callable, default=None): Callback function to be called
            when the system detected the stop (end) of voice activity presence.
        - on_vad_detect_start (callable, default=None): Callback function to
            be called when the system listens for voice activity. This is not
            called when VAD actually happens (use on_vad_start for this), but
            when the system starts listening for it.
        - on_vad_detect_stop (callable, default=None): Callback function to be
            called when the system stops listening for voice activity. This is
            not called when VAD actually stops (use on_vad_stop for this), but
            when the system stops listening for it.
        - on_turn_detection_start (callable, default=None): Callback function
            to be called when the system starts to listen for a turn of speech.
        - on_turn_detection_stop (callable, default=None): Callback function to
            be called when the system stops listening for a turn of speech.
        - wakeword_backend (str, default=""): Specifies the backend library to
            use for wake word detection. Supported options include 'pvporcupine'
            for using the Porcupine wake word engine or 'oww' for using the
            OpenWakeWord engine.
        - wakeword_backend (str, default="pvporcupine"): Specifies the backend
            library to use for wake word detection. Supported options include
            'pvporcupine' for using the Porcupine wake word engine or 'oww' for
            using the OpenWakeWord engine.
        - openwakeword_model_paths (str, default=None): Comma-separated paths
            to model files for the openwakeword library. These paths point to
            custom models that can be used for wake word detection when the
            openwakeword library is selected as the wakeword_backend.
        - openwakeword_inference_framework (str, default="onnx"): Specifies
            the inference framework to use with the openwakeword library.
            Can be either 'onnx' for Open Neural Network Exchange format 
            or 'tflite' for TensorFlow Lite.
        - wake_words (str, default=""): Comma-separated string of wake words to
            initiate recording when using the 'pvporcupine' wakeword backend.
            Supported wake words include: 'alexa', 'americano', 'blueberry',
            'bumblebee', 'computer', 'grapefruits', 'grasshopper', 'hey google',
            'hey siri', 'jarvis', 'ok google', 'picovoice', 'porcupine',
            'terminator'. For the 'openwakeword' backend, wake words are
            automatically extracted from the provided model files, so specifying
            them here is not necessary.
        - wake_words_sensitivity (float, default=0.5): Sensitivity for wake
            word detection, ranging from 0 (least sensitive) to 1 (most
            sensitive). Default is 0.5.
        - wake_word_activation_delay (float, default=0): Duration in seconds
            after the start of monitoring before the system switches to wake
            word activation if no voice is initially detected. If set to
            zero, the system uses wake word activation immediately.
        - wake_word_timeout (float, default=5): Duration in seconds after a
            wake word is recognized. If no subsequent voice activity is
            detected within this window, the system transitions back to an
            inactive state, awaiting the next wake word or voice activation.
        - wake_word_buffer_duration (float, default=0.1): Duration in seconds
            to buffer audio data during wake word detection. This helps in
            cutting out the wake word from the recording buffer so it does not
            falsely get detected along with the following spoken text, ensuring
            cleaner and more accurate transcription start triggers.
            Increase this if parts of the wake word get detected as text.
        - on_wakeword_detected (callable, default=None): Callback function to
            be called when a wake word is detected.
        - on_wakeword_timeout (callable, default=None): Callback function to
            be called when the system goes back to an inactive state after when
            no speech was detected after wake word activation
        - on_wakeword_detection_start (callable, default=None): Callback
             function to be called when the system starts to listen for wake
             words
        - on_wakeword_detection_end (callable, default=None): Callback
            function to be called when the system stops to listen for
            wake words (e.g. because of timeout or wake word detected)
        - on_recorded_chunk (callable, default=None): Callback function to be
            called when a chunk of audio is recorded. The function is called
            with the recorded audio chunk as its argument.
        - debug_mode (bool, default=False): If set to True, the system will
            print additional debug information to the console.
        - handle_buffer_overflow (bool, default=True): If set to True, the system
            will log a warning when an input overflow occurs during recording and
            remove the data from the buffer.
        - beam_size (int, default=5): The beam size to use for beam search
            decoding.
        - beam_size_realtime (int, default=3): The beam size to use for beam
            search decoding in the real-time transcription model.
        - buffer_size (int, default=512): The buffer size to use for audio
            recording. Changing this may break functionality.
        - sample_rate (int, default=16000): The sample rate to use for audio
            recording. Changing this will very probably functionality (as the
            WebRTC VAD model is very sensitive towards the sample rate).
        - initial_prompt (str or iterable of int, default=None): Initial
            prompt to be fed to the main transcription model.
        - initial_prompt_realtime (str or iterable of int, default=None):
            Initial prompt to be fed to the real-time transcription model.
        - suppress_tokens (list of int, default=[-1]): Tokens to be suppressed
            from the transcription output.
        - print_transcription_time (bool, default=False): Logs processing time
            of main model transcription 
        - early_transcription_on_silence (int, default=0): If set, the
            system will transcribe audio faster when silence is detected.
            Transcription will start after the specified milliseconds, so 
            keep this value lower than post_speech_silence_duration. 
            Ideally around post_speech_silence_duration minus the estimated
            transcription time with the main model.
            If silence lasts longer than post_speech_silence_duration, the 
            recording is stopped, and the transcription is submitted. If 
            voice activity resumes within this period, the transcription 
            is discarded. Results in faster final transcriptions to the cost
            of additional GPU load due to some unnecessary final transcriptions.
        - allowed_latency_limit (int, default=100): Maximal amount of chunks
            that can be unprocessed in queue before discarding chunks.
        - no_log_file (bool, default=False): Skips writing of debug log file.
        - use_extended_logging (bool, default=False): Writes extensive
            log messages for the recording worker, that processes the audio
            chunks.
        - faster_whisper_vad_filter (bool, default=True): If set to True,
            the system will additionally use the VAD filter from the faster_whisper library
            for voice activity detection. This filter is more robust against
            background noise but requires additional GPU resources.
        - normalize_audio (bool, default=False): If set to True, the system will
            normalize the audio to a specific range before processing. This can
            help improve the quality of the transcription.
        - start_callback_in_new_thread (bool, default=False): If set to True,
            the callback functions will be executed in a
            new thread. This can help improve performance by allowing the
            callback to run concurrently with other operations.

        Raises:
            Exception: Errors related to initializing transcription
            model, wake word detection, or audio recording.
        """

        self.language = language
        self.compute_type = compute_type
        self.input_device_index = input_device_index
        self.gpu_device_index = gpu_device_index
        self.device = device
        self.wake_words = wake_words
        self.wake_word_activation_delay = wake_word_activation_delay
        self.wake_word_timeout = wake_word_timeout
        self.wake_word_buffer_duration = wake_word_buffer_duration
        self.ensure_sentence_starting_uppercase = (
            ensure_sentence_starting_uppercase
        )
        self.ensure_sentence_ends_with_period = (
            ensure_sentence_ends_with_period
        )
        self.use_microphone = mp.Value(c_bool, use_microphone)
        self.min_gap_between_recordings = min_gap_between_recordings
        self.min_length_of_recording = min_length_of_recording
        self.pre_recording_buffer_duration = pre_recording_buffer_duration
        self.post_speech_silence_duration = post_speech_silence_duration
        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        self.on_wakeword_detected = on_wakeword_detected
        self.on_wakeword_timeout = on_wakeword_timeout
        self.on_vad_start = on_vad_start
        self.on_vad_stop = on_vad_stop
        self.on_vad_detect_start = on_vad_detect_start
        self.on_vad_detect_stop = on_vad_detect_stop
        self.on_turn_detection_start = on_turn_detection_start
        self.on_turn_detection_stop = on_turn_detection_stop
        self.on_wakeword_detection_start = on_wakeword_detection_start
        self.on_wakeword_detection_end = on_wakeword_detection_end
        self.on_recorded_chunk = on_recorded_chunk
        self.on_transcription_start = on_transcription_start
        self.enable_realtime_transcription = enable_realtime_transcription
        self.use_main_model_for_realtime = use_main_model_for_realtime
        self.main_model_type = model
        if not download_root:
            download_root = None
        self.download_root = download_root
        self.realtime_model_type = realtime_model_type
        self.realtime_processing_pause = realtime_processing_pause
        self.init_realtime_after_seconds = init_realtime_after_seconds
        self.on_realtime_transcription_update = (
            on_realtime_transcription_update
        )
        self.on_realtime_transcription_stabilized = (
            on_realtime_transcription_stabilized
        )
        self.debug_mode = debug_mode
        self.handle_buffer_overflow = handle_buffer_overflow
        self.beam_size = beam_size
        self.beam_size_realtime = beam_size_realtime
        self.allowed_latency_limit = allowed_latency_limit
        self.batch_size = batch_size
        self.realtime_batch_size = realtime_batch_size

        self.level = level
        self.audio_queue = mp.Queue()
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.recording_start_time = 0
        self.recording_stop_time = 0
        self.last_recording_start_time = 0
        self.last_recording_stop_time = 0
        self.wake_word_detect_time = 0
        self.silero_check_time = 0
        self.silero_working = False
        self.speech_end_silence_start = 0
        self.silero_sensitivity = silero_sensitivity
        self.silero_deactivity_detection = silero_deactivity_detection
        self.listen_start = 0
        self.spinner = spinner
        self.halo = None
        self.state = "inactive"
        self.wakeword_detected = False
        self.text_storage = []
        self.realtime_stabilized_text = ""
        self.realtime_stabilized_safetext = ""
        self.is_webrtc_speech_active = False
        self.is_silero_speech_active = False
        self.recording_thread = None
        self.realtime_thread = None
        self.audio_interface = None
        self.audio = None
        self.stream = None
        self.start_recording_event = threading.Event()
        self.stop_recording_event = threading.Event()
        self.backdate_stop_seconds = 0.0
        self.backdate_resume_seconds = 0.0
        self.last_transcription_bytes = None
        self.last_transcription_bytes_b64 = None
        self.initial_prompt = initial_prompt
        self.initial_prompt_realtime = initial_prompt_realtime
        self.suppress_tokens = suppress_tokens
        self.use_wake_words = wake_words or wakeword_backend in {'oww', 'openwakeword', 'openwakewords'}
        self.detected_language = None
        self.detected_language_probability = 0
        self.detected_realtime_language = None
        self.detected_realtime_language_probability = 0
        self.transcription_lock = threading.Lock()
        self.shutdown_lock = threading.Lock()
        self.transcribe_count = 0
        self.print_transcription_time = print_transcription_time
        self.early_transcription_on_silence = early_transcription_on_silence
        self.use_extended_logging = use_extended_logging
        self.faster_whisper_vad_filter = faster_whisper_vad_filter
        self.normalize_audio = normalize_audio
        self.awaiting_speech_end = False
        self.start_callback_in_new_thread = start_callback_in_new_thread

        # ----------------------------------------------------------------------------
        # Named logger configuration
        # By default, let's set it up so it logs at 'level' to the console.
        # If you do NOT want this default configuration, remove the lines below
        # and manage your "realtimestt" logger from your application code.
        logger.setLevel(logging.DEBUG)  # We capture all, then filter via handlers

        log_format = "RealTimeSTT: %(name)s - %(levelname)s - %(message)s"
        file_log_format = "%(asctime)s.%(msecs)03d - " + log_format

        # Create and set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(logging.Formatter(log_format))

        logger.addHandler(console_handler)

        if not no_log_file:
            file_handler = logging.FileHandler('realtimesst.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(file_log_format, datefmt='%Y-%m-%d %H:%M:%S'))
            logger.addHandler(file_handler)
        # ----------------------------------------------------------------------------

        self.is_shut_down = False
        self.shutdown_event = mp.Event()
        
        try:
            # Only set the start method if it hasn't been set already
            if mp.get_start_method(allow_none=True) is None:
                mp.set_start_method("spawn")
        except RuntimeError as e:
            logger.info(f"Start method has already been set. Details: {e}")

        logger.info("Starting RealTimeSTT")

        if use_extended_logging:
            logger.info("RealtimeSTT was called with these parameters:")
            for param, value in locals().items():
                logger.info(f"{param}: {value}")

        self.interrupt_stop_event = mp.Event()
        self.was_interrupted = mp.Event()
        self.main_transcription_ready_event = mp.Event()

        self.parent_transcription_pipe, child_transcription_pipe = SafePipe()
        self.parent_stdout_pipe, child_stdout_pipe = SafePipe()

        # Set device for model
        self.device = "cuda" if self.device == "cuda" and torch.cuda.is_available() else "cpu"

        self.transcript_process = self._start_thread(
            target=AudioToTextRecorder._transcription_worker,
            args=(
                child_transcription_pipe,
                child_stdout_pipe,
                self.main_model_type,
                self.download_root,
                self.compute_type,
                self.gpu_device_index,
                self.device,
                self.main_transcription_ready_event,
                self.shutdown_event,
                self.interrupt_stop_event,
                self.beam_size,
                self.initial_prompt,
                self.suppress_tokens,
                self.batch_size,
                self.faster_whisper_vad_filter,
                self.normalize_audio,
            )
        )

        # Start audio data reading process
        if self.use_microphone.value:
            logger.info("Initializing audio recording"
                         " (creating pyAudio input stream,"
                         f" sample rate: {self.sample_rate}"
                         f" buffer size: {self.buffer_size}"
                         )
            self.reader_process = self._start_thread(
                target=AudioToTextRecorder._audio_data_worker,
                args=(
                    self.audio_queue,
                    self.sample_rate,
                    self.buffer_size,
                    self.input_device_index,
                    self.shutdown_event,
                    self.interrupt_stop_event,
                    self.use_microphone
                )
            )

        # Initialize the realtime transcription model
        if self.enable_realtime_transcription and not self.use_main_model_for_realtime:
            try:
                logger.info("Initializing faster_whisper realtime "
                             f"transcription model {self.realtime_model_type}, "
                             f"default device: {self.device}, "
                             f"compute type: {self.compute_type}, "
                             f"device index: {self.gpu_device_index}, "
                             f"download root: {self.download_root}"
                             )
                self.realtime_model_type = faster_whisper.WhisperModel(
                    model_size_or_path=self.realtime_model_type,
                    device=self.device,
                    compute_type=self.compute_type,
                    device_index=self.gpu_device_index,
                    download_root=self.download_root,
                )
                if self.realtime_batch_size > 0:
                    self.realtime_model_type = BatchedInferencePipeline(model=self.realtime_model_type)

                # Run a warm-up transcription
                current_dir = os.path.dirname(os.path.realpath(__file__))
                warmup_audio_path = os.path.join(
                    current_dir, "warmup_audio.wav"
                )
                warmup_audio_data, _ = sf.read(warmup_audio_path, dtype="float32")
                segments, info = self.realtime_model_type.transcribe(warmup_audio_data, language="en", beam_size=1)
                model_warmup_transcription = " ".join(segment.text for segment in segments)
            except Exception as e:
                logger.exception("Error initializing faster_whisper "
                                  f"realtime transcription model: {e}"
                                  )
                raise

            logger.debug("Faster_whisper realtime speech to text "
                          "transcription model initialized successfully")

        # Setup wake word detection
        if wake_words or wakeword_backend in {'oww', 'openwakeword', 'openwakewords', 'pvp', 'pvporcupine'}:
            self.wakeword_backend = wakeword_backend

            self.wake_words_list = [
                word.strip() for word in wake_words.lower().split(',')
            ]
            self.wake_words_sensitivity = wake_words_sensitivity
            self.wake_words_sensitivities = [
                float(wake_words_sensitivity)
                for _ in range(len(self.wake_words_list))
            ]

            if wake_words and self.wakeword_backend in {'pvp', 'pvporcupine'}:

                try:
                    self.porcupine = pvporcupine.create(
                        keywords=self.wake_words_list,
                        sensitivities=self.wake_words_sensitivities
                    )
                    self.buffer_size = self.porcupine.frame_length
                    self.sample_rate = self.porcupine.sample_rate

                except Exception as e:
                    logger.exception(
                        "Error initializing porcupine "
                        f"wake word detection engine: {e}. "
                        f"Wakewords: {self.wake_words_list}."
                    )
                    raise

                logger.debug(
                    "Porcupine wake word detection engine initialized successfully"
                )

            elif wake_words and self.wakeword_backend in {'oww', 'openwakeword', 'openwakewords'}:
                    
                openwakeword.utils.download_models()

                try:
                    if openwakeword_model_paths:
                        model_paths = openwakeword_model_paths.split(',')
                        self.owwModel = Model(
                            wakeword_models=model_paths,
                            inference_framework=openwakeword_inference_framework
                        )
                        logger.info(
                            "Successfully loaded wakeword model(s): "
                            f"{openwakeword_model_paths}"
                        )
                    else:
                        self.owwModel = Model(
                            inference_framework=openwakeword_inference_framework)
                    
                    self.oww_n_models = len(self.owwModel.models.keys())
                    if not self.oww_n_models:
                        logger.error(
                            "No wake word models loaded."
                        )

                    for model_key in self.owwModel.models.keys():
                        logger.info(
                            "Successfully loaded openwakeword model: "
                            f"{model_key}"
                        )

                except Exception as e:
                    logger.exception(
                        "Error initializing openwakeword "
                        f"wake word detection engine: {e}"
                    )
                    raise

                logger.debug(
                    "Open wake word detection engine initialized successfully"
                )
            
            else:
                logger.exception(f"Wakeword engine {self.wakeword_backend} unknown/unsupported or wake_words not specified. Please specify one of: pvporcupine, openwakeword.")


        # Setup voice activity detection model WebRTC
        try:
            logger.info("Initializing WebRTC voice with "
                         f"Sensitivity {webrtc_sensitivity}"
                         )
            self.webrtc_vad_model = webrtcvad.Vad()
            self.webrtc_vad_model.set_mode(webrtc_sensitivity)

        except Exception as e:
            logger.exception("Error initializing WebRTC voice "
                              f"activity detection engine: {e}"
                              )
            raise

        logger.debug("WebRTC VAD voice activity detection "
                      "engine initialized successfully"
                      )

        # Setup voice activity detection model Silero VAD
        try:
            self.silero_vad_model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                verbose=False,
                onnx=silero_use_onnx
            )

        except Exception as e:
            logger.exception(f"Error initializing Silero VAD "
                              f"voice activity detection engine: {e}"
                              )
            raise

        logger.debug("Silero VAD voice activity detection "
                      "engine initialized successfully"
                      )

        self.audio_buffer = collections.deque(
            maxlen=int((self.sample_rate // self.buffer_size) *
                       self.pre_recording_buffer_duration)
        )
        self.last_words_buffer = collections.deque(
            maxlen=int((self.sample_rate // self.buffer_size) *
                       0.3)
        )
        self.frames = []
        self.last_frames = []

        # Recording control flags
        self.is_recording = False
        self.is_running = True
        self.start_recording_on_voice_activity = False
        self.stop_recording_on_voice_deactivity = False

        # Start the recording worker thread
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.recording_thread.daemon = True
        self.recording_thread.start()

        # Start the realtime transcription worker thread
        self.realtime_thread = threading.Thread(target=self._realtime_worker)
        self.realtime_thread.daemon = True
        self.realtime_thread.start()
                   
        # Wait for transcription models to start
        logger.debug('Waiting for main transcription model to start')
        self.main_transcription_ready_event.wait()
        logger.debug('Main transcription model ready')

        self.stdout_thread = threading.Thread(target=self._read_stdout)
        self.stdout_thread.daemon = True
        self.stdout_thread.start()

        logger.debug('RealtimeSTT initialization completed successfully')
                   
    def _start_thread(self, target=None, args=()):
        """
        Implement a consistent threading model across the library.

        This method is used to start any thread in this library. It uses the
        standard threading. Thread for Linux and for all others uses the pytorch
        MultiProcessing library 'Process'.
        Args:
            target (callable object): is the callable object to be invoked by
              the run() method. Defaults to None, meaning nothing is called.
            args (tuple): is a list or tuple of arguments for the target
              invocation. Defaults to ().
        """
        if (platform.system() == 'Linux'):
            thread = threading.Thread(target=target, args=args)
            thread.deamon = True
            thread.start()
            return thread
        else:
            thread = mp.Process(target=target, args=args)
            thread.start()
            return thread

    def _read_stdout(self):
        while not self.shutdown_event.is_set():
            try:
                if self.parent_stdout_pipe.poll(0.1):
                    logger.debug("Receive from stdout pipe")
                    message = self.parent_stdout_pipe.recv()
                    logger.info(message)
            except (BrokenPipeError, EOFError, OSError):
                # The pipe probably has been closed, so we ignore the error
                pass
            except KeyboardInterrupt:  # handle manual interruption (Ctrl+C)
                logger.info("KeyboardInterrupt in read from stdout detected, exiting...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in read from stdout: {e}", exc_info=True)
                logger.error(traceback.format_exc())  # Log the full traceback here
                break 
            time.sleep(0.1)

    def _transcription_worker(*args, **kwargs):
        worker = TranscriptionWorker(*args, **kwargs)
        worker.run()

    def _run_callback(self, cb, *args, **kwargs):
        if self.start_callback_in_new_thread:
            # Run the callback in a new thread to avoid blocking the main thread
            threading.Thread(target=cb, args=args, kwargs=kwargs, daemon=True).start()
        else:
            # Run the callback in the main thread to avoid threading issues
            cb(*args, **kwargs)

    @staticmethod
    def _audio_data_worker(
        audio_queue,
        target_sample_rate,
        buffer_size,
        input_device_index,
        shutdown_event,
        interrupt_stop_event,
        use_microphone
    ):
        """
        Worker method that handles the audio recording process.

        This method runs in a separate process and is responsible for:
        - Setting up the audio input stream for recording at the highest possible sample rate.
        - Continuously reading audio data from the input stream, resampling if necessary,
        preprocessing the data, and placing complete chunks in a queue.
        - Handling errors during the recording process.
        - Gracefully terminating the recording process when a shutdown event is set.

        Args:
            audio_queue (queue.Queue): A queue where recorded audio data is placed.
            target_sample_rate (int): The desired sample rate for the output audio (for Silero VAD).
            buffer_size (int): The number of samples expected by the Silero VAD model.
            input_device_index (int): The index of the audio input device.
            shutdown_event (threading.Event): An event that, when set, signals this worker method to terminate.
            interrupt_stop_event (threading.Event): An event to signal keyboard interrupt.
            use_microphone (multiprocessing.Value): A shared value indicating whether to use the microphone.

        Raises:
            Exception: If there is an error while initializing the audio recording.
        """
        import pyaudio
        import numpy as np
        from scipy import signal

        if __name__ == '__main__':
            system_signal.signal(system_signal.SIGINT, system_signal.SIG_IGN)

        def get_highest_sample_rate(audio_interface, device_index):
            """Get the highest supported sample rate for the specified device."""
            try:
                device_info = audio_interface.get_device_info_by_index(device_index)
                logger.debug(f"Retrieving highest sample rate for device index {device_index}: {device_info}")
                max_rate = int(device_info['defaultSampleRate'])

                if 'supportedSampleRates' in device_info:
                    supported_rates = [int(rate) for rate in device_info['supportedSampleRates']]
                    if supported_rates:
                        max_rate = max(supported_rates)

                logger.debug(f"Highest supported sample rate for device index {device_index} is {max_rate}")
                return max_rate
            except Exception as e:
                logger.warning(f"Failed to get highest sample rate: {e}")
                return 48000  # Fallback to a common high sample rate

        def initialize_audio_stream(audio_interface, sample_rate, chunk_size):
            nonlocal input_device_index

            def validate_device(device_index):
                """Validate that the device exists and is actually available for input."""
                try:
                    device_info = audio_interface.get_device_info_by_index(device_index)
                    logger.debug(f"Validating device index {device_index} with info: {device_info}")
                    if not device_info.get('maxInputChannels', 0) > 0:
                        logger.debug("Device has no input channels, invalid for recording.")
                        return False

                    # Try to actually read from the device
                    test_stream = audio_interface.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=target_sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size,
                        input_device_index=device_index,
                        start=False  # Don't start the stream yet
                    )

                    test_stream.start_stream()
                    test_data = test_stream.read(chunk_size, exception_on_overflow=False)
                    test_stream.stop_stream()
                    test_stream.close()

                    if len(test_data) == 0:
                        logger.debug("Device produced no data, invalid for recording.")
                        return False

                    logger.debug(f"Device index {device_index} successfully validated.")
                    return True

                except Exception as e:
                    logger.debug(f"Device validation failed for index {device_index}: {e}")
                    return False

            """Initialize the audio stream with error handling."""
            while not shutdown_event.is_set():
                try:
                    # First, get a list of all available input devices
                    input_devices = []
                    device_count = audio_interface.get_device_count()
                    logger.debug(f"Found {device_count} total audio devices on the system.")
                    for i in range(device_count):
                        try:
                            device_info = audio_interface.get_device_info_by_index(i)
                            if device_info.get('maxInputChannels', 0) > 0:
                                input_devices.append(i)
                        except Exception as e:
                            logger.debug(f"Could not retrieve info for device index {i}: {e}")
                            continue

                    logger.debug(f"Available input devices with input channels: {input_devices}")
                    if not input_devices:
                        raise Exception("No input devices found")

                    # If input_device_index is None or invalid, try to find a working device
                    if input_device_index is None or input_device_index not in input_devices:
                        # First try the default device
                        try:
                            default_device = audio_interface.get_default_input_device_info()
                            logger.debug(f"Default device info: {default_device}")
                            if validate_device(default_device['index']):
                                input_device_index = default_device['index']
                                logger.debug(f"Default device {input_device_index} selected.")
                        except Exception:
                            # If default device fails, try other available input devices
                            logger.debug("Default device validation failed, checking other devices...")
                            for device_index in input_devices:
                                if validate_device(device_index):
                                    input_device_index = device_index
                                    logger.debug(f"Device {input_device_index} selected.")
                                    break
                            else:
                                raise Exception("No working input devices found")

                    # Validate the selected device one final time
                    if not validate_device(input_device_index):
                        raise Exception("Selected device validation failed")

                    # If we get here, we have a validated device
                    logger.debug(f"Opening stream with device index {input_device_index}, "
                                f"sample_rate={sample_rate}, chunk_size={chunk_size}")
                    stream = audio_interface.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size,
                        input_device_index=input_device_index,
                    )

                    logger.info(f"Microphone connected and validated (device index: {input_device_index}, "
                                f"sample rate: {sample_rate}, chunk size: {chunk_size})")
                    return stream

                except Exception as e:
                    logger.error(f"Microphone connection failed: {e}. Retrying...", exc_info=True)
                    input_device_index = None
                    time.sleep(3)  # Wait before retrying
                    continue

        def preprocess_audio(chunk, original_sample_rate, target_sample_rate):
            """Preprocess audio chunk similar to feed_audio method."""
            if isinstance(chunk, np.ndarray):
                # Handle stereo to mono conversion if necessary
                if chunk.ndim == 2:
                    chunk = np.mean(chunk, axis=1)

                # Resample to target_sample_rate if necessary
                if original_sample_rate != target_sample_rate:
                    logger.debug(f"Resampling from {original_sample_rate} Hz to {target_sample_rate} Hz.")
                    num_samples = int(len(chunk) * target_sample_rate / original_sample_rate)
                    chunk = signal.resample(chunk, num_samples)

                chunk = chunk.astype(np.int16)
            else:
                # If chunk is bytes, convert to numpy array
                chunk = np.frombuffer(chunk, dtype=np.int16)

                # Resample if necessary
                if original_sample_rate != target_sample_rate:
                    logger.debug(f"Resampling from {original_sample_rate} Hz to {target_sample_rate} Hz.")
                    num_samples = int(len(chunk) * target_sample_rate / original_sample_rate)
                    chunk = signal.resample(chunk, num_samples)
                    chunk = chunk.astype(np.int16)

            return chunk.tobytes()

        audio_interface = None
        stream = None
        device_sample_rate = None
        chunk_size = 1024  # Increased chunk size for better performance

        def setup_audio():  
            nonlocal audio_interface, stream, device_sample_rate, input_device_index
            try:
                if audio_interface is None:
                    logger.debug("Creating PyAudio interface...")
                    audio_interface = pyaudio.PyAudio()

                if input_device_index is None:
                    try:
                        default_device = audio_interface.get_default_input_device_info()
                        input_device_index = default_device['index']
                        logger.debug(f"No device index supplied; using default device {input_device_index}")
                    except OSError as e:
                        logger.debug(f"Default device retrieval failed: {e}")
                        input_device_index = None

                # We'll try 16000 Hz first, then the highest rate we detect, then fallback if needed
                sample_rates_to_try = [16000]
                if input_device_index is not None:
                    highest_rate = get_highest_sample_rate(audio_interface, input_device_index)
                    if highest_rate != 16000:
                        sample_rates_to_try.append(highest_rate)
                else:
                    sample_rates_to_try.append(48000)

                logger.debug(f"Sample rates to try for device {input_device_index}: {sample_rates_to_try}")

                for rate in sample_rates_to_try:
                    try:
                        device_sample_rate = rate
                        logger.debug(f"Attempting to initialize audio stream at {device_sample_rate} Hz.")
                        stream = initialize_audio_stream(audio_interface, device_sample_rate, chunk_size)
                        if stream is not None:
                            logger.debug(
                                f"Audio recording initialized successfully at {device_sample_rate} Hz, "
                                f"reading {chunk_size} frames at a time"
                            )
                            return True
                    except Exception as e:
                        logger.warning(f"Failed to initialize audio stream at {device_sample_rate} Hz: {e}")
                        continue

                # If we reach here, none of the sample rates worked
                raise Exception("Failed to initialize audio stream with all sample rates.")

            except Exception as e:
                logger.exception(f"Error initializing pyaudio audio recording: {e}")
                if audio_interface:
                    audio_interface.terminate()
                return False

        logger.debug(f"Starting audio data worker with target_sample_rate={target_sample_rate}, "
                    f"buffer_size={buffer_size}, input_device_index={input_device_index}")

        if not setup_audio():
            raise Exception("Failed to set up audio recording.")

        buffer = bytearray()
        silero_buffer_size = 2 * buffer_size  # Silero complains if too short

        time_since_last_buffer_message = 0

        try:
            while not shutdown_event.is_set():
                try:
                    data = stream.read(chunk_size, exception_on_overflow=False)

                    if use_microphone.value:
                        processed_data = preprocess_audio(data, device_sample_rate, target_sample_rate)
                        buffer += processed_data

                        # Check if the buffer has reached or exceeded the silero_buffer_size
                        while len(buffer) >= silero_buffer_size:
                            # Extract silero_buffer_size amount of data from the buffer
                            to_process = buffer[:silero_buffer_size]
                            buffer = buffer[silero_buffer_size:]

                            # Feed the extracted data to the audio_queue
                            if time_since_last_buffer_message:
                                time_passed = time.time() - time_since_last_buffer_message
                                if time_passed > 1:
                                    logger.debug("_audio_data_worker writing audio data into queue.")
                                    time_since_last_buffer_message = time.time()
                            else:
                                time_since_last_buffer_message = time.time()

                            audio_queue.put(to_process)

                except OSError as e:
                    if e.errno == pyaudio.paInputOverflowed:
                        logger.warning("Input overflowed. Frame dropped.")
                    else:
                        logger.error(f"OSError during recording: {e}", exc_info=True)
                        # Attempt to reinitialize the stream
                        logger.error("Attempting to reinitialize the audio stream...")

                        try:
                            if stream:
                                stream.stop_stream()
                                stream.close()
                        except Exception:
                            pass

                        time.sleep(1)
                        if not setup_audio():
                            logger.error("Failed to reinitialize audio stream. Exiting.")
                            break
                        else:
                            logger.error("Audio stream reinitialized successfully.")
                    continue

                except Exception as e:
                    logger.error(f"Unknown error during recording: {e}")
                    tb_str = traceback.format_exc()
                    logger.error(f"Traceback: {tb_str}")
                    logger.error(f"Error: {e}")
                    # Attempt to reinitialize the stream
                    logger.info("Attempting to reinitialize the audio stream...")
                    try:
                        if stream:
                            stream.stop_stream()
                            stream.close()
                    except Exception:
                        pass

                    time.sleep(1)
                    if not setup_audio():
                        logger.error("Failed to reinitialize audio stream. Exiting.")
                        break
                    else:
                        logger.info("Audio stream reinitialized successfully.")
                    continue

        except KeyboardInterrupt:
            interrupt_stop_event.set()
            logger.debug("Audio data worker process finished due to KeyboardInterrupt")
        finally:
            # After recording stops, feed any remaining audio data
            if buffer:
                audio_queue.put(bytes(buffer))

            try:
                if stream:
                    stream.stop_stream()
                    stream.close()
            except Exception:
                pass
            if audio_interface:
                audio_interface.terminate()

    def wakeup(self):
        """
        If in wake work modus, wake up as if a wake word was spoken.
        """
        self.listen_start = time.time()

    def abort(self):
        state = self.state
        self.start_recording_on_voice_activity = False
        self.stop_recording_on_voice_deactivity = False
        self.interrupt_stop_event.set()
        if self.state != "inactive": # if inactive, was_interrupted will never be set
            self.was_interrupted.wait()
            self._set_state("transcribing")
        self.was_interrupted.clear()
        if self.is_recording: # if recording, make sure to stop the recorder
            self.stop()


    def wait_audio(self):
        """
        Waits for the start and completion of the audio recording process.

        This method is responsible for:
        - Waiting for voice activity to begin recording if not yet started.
        - Waiting for voice inactivity to complete the recording.
        - Setting the audio buffer from the recorded frames.
        - Resetting recording-related attributes.

        Side effects:
        - Updates the state of the instance.
        - Modifies the audio attribute to contain the processed audio data.
        """

        try:
            logger.info("Setting listen time")
            if self.listen_start == 0:
                self.listen_start = time.time()

            # If not yet started recording, wait for voice activity to initiate.
            if not self.is_recording and not self.frames:
                self._set_state("listening")
                self.start_recording_on_voice_activity = True

                # Wait until recording starts
                logger.debug('Waiting for recording start')
                while not self.interrupt_stop_event.is_set():
                    if self.start_recording_event.wait(timeout=0.02):
                        break

            # If recording is ongoing, wait for voice inactivity
            # to finish recording.
            if self.is_recording:
                self.stop_recording_on_voice_deactivity = True

                # Wait until recording stops
                logger.debug('Waiting for recording stop')
                while not self.interrupt_stop_event.is_set():
                    if (self.stop_recording_event.wait(timeout=0.02)):
                        break

            frames = self.frames
            if len(frames) == 0:
                frames = self.last_frames

            # Calculate samples needed for backdating resume
            samples_to_keep = int(self.sample_rate * self.backdate_resume_seconds)

            # First convert all current frames to audio array
            full_audio_array = np.frombuffer(b''.join(frames), dtype=np.int16)
            full_audio = full_audio_array.astype(np.float32) / INT16_MAX_ABS_VALUE

            # Calculate how many samples we need to keep for backdating resume
            if samples_to_keep > 0:
                samples_to_keep = min(samples_to_keep, len(full_audio))
                # Keep the last N samples for backdating resume
                frames_to_read_audio = full_audio[-samples_to_keep:]

                # Convert the audio back to int16 bytes for frames
                frames_to_read_int16 = (frames_to_read_audio * INT16_MAX_ABS_VALUE).astype(np.int16)
                frame_bytes = frames_to_read_int16.tobytes()

                # Split into appropriate frame sizes (assuming standard frame size)
                FRAME_SIZE = 2048  # Typical frame size
                frames_to_read = []
                for i in range(0, len(frame_bytes), FRAME_SIZE):
                    frame = frame_bytes[i:i + FRAME_SIZE]
                    if frame:  # Only add non-empty frames
                        frames_to_read.append(frame)
            else:
                frames_to_read = []

            # Process backdate stop seconds
            samples_to_remove = int(self.sample_rate * self.backdate_stop_seconds)

            if samples_to_remove > 0:
                if samples_to_remove < len(full_audio):
                    self.audio = full_audio[:-samples_to_remove]
                    logger.debug(f"Removed {samples_to_remove} samples "
                        f"({samples_to_remove/self.sample_rate:.3f}s) from end of audio")
                else:
                    self.audio = np.array([], dtype=np.float32)
                    logger.debug("Cleared audio (samples_to_remove >= audio length)")
            else:
                self.audio = full_audio
                logger.debug(f"No samples removed, final audio length: {len(self.audio)}")

            self.frames.clear()
            self.last_frames.clear()
            self.frames.extend(frames_to_read)

            # Reset backdating parameters
            self.backdate_stop_seconds = 0.0
            self.backdate_resume_seconds = 0.0

            self.listen_start = 0

            self._set_state("inactive")

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt in wait_audio, shutting down")
            self.shutdown()
            raise  # Re-raise the exception after cleanup


    def perform_final_transcription(self, audio_bytes=None, use_prompt=True):
        start_time = 0
        with self.transcription_lock:
            if audio_bytes is None:
                audio_bytes = copy.deepcopy(self.audio)

            if audio_bytes is None or len(audio_bytes) == 0:
                print("No audio data available for transcription")
                #logger.info("No audio data available for transcription")
                return ""

            try:
                if self.transcribe_count == 0:
                    logger.debug("Adding transcription request, no early transcription started")
                    start_time = time.time()  # Start timing
                    self.parent_transcription_pipe.send((audio_bytes, self.language, use_prompt))
                    self.transcribe_count += 1

                while self.transcribe_count > 0:
                    logger.debug(F"Receive from parent_transcription_pipe after sendiung transcription request, transcribe_count: {self.transcribe_count}")
                    if not self.parent_transcription_pipe.poll(0.1): # check if transcription done
                        if self.interrupt_stop_event.is_set(): # check if interrupted
                            self.was_interrupted.set()
                            self._set_state("inactive")
                            return "" # return empty string if interrupted
                        continue
                    status, result = self.parent_transcription_pipe.recv()
                    self.transcribe_count -= 1

                self.allowed_to_early_transcribe = True
                self._set_state("inactive")
                if status == 'success':
                    segments, info = result
                    self.detected_language = info.language if info.language_probability > 0 else None
                    self.detected_language_probability = info.language_probability
                    self.last_transcription_bytes = copy.deepcopy(audio_bytes)
                    self.last_transcription_bytes_b64 = base64.b64encode(self.last_transcription_bytes.tobytes()).decode('utf-8')
                    transcription = self._preprocess_output(segments)
                    end_time = time.time()  # End timing
                    transcription_time = end_time - start_time

                    if start_time:
                        if self.print_transcription_time:
                            print(f"Model {self.main_model_type} completed transcription in {transcription_time:.2f} seconds")
                        else:
                            logger.debug(f"Model {self.main_model_type} completed transcription in {transcription_time:.2f} seconds")
                    return "" if self.interrupt_stop_event.is_set() else transcription # if interrupted return empty string
                else:
                    logger.error(f"Transcription error: {result}")
                    raise Exception(result)
            except Exception as e:
                logger.error(f"Error during transcription: {str(e)}", exc_info=True)
                raise e


    def transcribe(self):
        """
        Transcribes audio captured by this class instance using the
        `faster_whisper` model.

        Automatically starts recording upon voice activity if not manually
          started using `recorder.start()`.
        Automatically stops recording upon voice deactivity if not manually
          stopped with `recorder.stop()`.
        Processes the recorded audio to generate transcription.

        Args:
            on_transcription_finished (callable, optional): Callback function
              to be executed when transcription is ready.
            If provided, transcription will be performed asynchronously,
              and the callback will receive the transcription as its argument.
              If omitted, the transcription will be performed synchronously,
              and the result will be returned.

        Returns (if no callback is set):
            str: The transcription of the recorded audio.

        Raises:
            Exception: If there is an error during the transcription process.
        """
        audio_copy = copy.deepcopy(self.audio)
        self._set_state("transcribing")
        if self.on_transcription_start:
            abort_value = self.on_transcription_start(audio_copy)
            if not abort_value:
                return self.perform_final_transcription(audio_copy)
            return None
        else:
            return self.perform_final_transcription(audio_copy)


    def _process_wakeword(self, data):
        """
        Processes audio data to detect wake words.
        """
        if self.wakeword_backend in {'pvp', 'pvporcupine'}:
            pcm = struct.unpack_from(
                "h" * self.buffer_size,
                data
            )
            porcupine_index = self.porcupine.process(pcm)
            if self.debug_mode:
                logger.info(f"wake words porcupine_index: {porcupine_index}")
            return porcupine_index

        elif self.wakeword_backend in {'oww', 'openwakeword', 'openwakewords'}:
            pcm = np.frombuffer(data, dtype=np.int16)
            prediction = self.owwModel.predict(pcm)
            max_score = -1
            max_index = -1
            wake_words_in_prediction = len(self.owwModel.prediction_buffer.keys())
            self.wake_words_sensitivities
            if wake_words_in_prediction:
                for idx, mdl in enumerate(self.owwModel.prediction_buffer.keys()):
                    scores = list(self.owwModel.prediction_buffer[mdl])
                    if scores[-1] >= self.wake_words_sensitivity and scores[-1] > max_score:
                        max_score = scores[-1]
                        max_index = idx
                if self.debug_mode:
                    logger.info(f"wake words oww max_index, max_score: {max_index} {max_score}")
                return max_index  
            else:
                if self.debug_mode:
                    logger.info(f"wake words oww_index: -1")
                return -1

        if self.debug_mode:        
            logger.info("wake words no match")

        return -1

    def text(self,
             on_transcription_finished=None,
             ):
        """
        Transcribes audio captured by this class instance
        using the `faster_whisper` model.

        - Automatically starts recording upon voice activity if not manually
          started using `recorder.start()`.
        - Automatically stops recording upon voice deactivity if not manually
          stopped with `recorder.stop()`.
        - Processes the recorded audio to generate transcription.

        Args:
            on_transcription_finished (callable, optional): Callback function
              to be executed when transcription is ready.
            If provided, transcription will be performed asynchronously, and
              the callback will receive the transcription as its argument.
              If omitted, the transcription will be performed synchronously,
              and the result will be returned.

        Returns (if not callback is set):
            str: The transcription of the recorded audio
        """
        self.interrupt_stop_event.clear()
        self.was_interrupted.clear()
        try:
            self.wait_audio()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt in text() method")
            self.shutdown()
            raise  # Re-raise the exception after cleanup

        if self.is_shut_down or self.interrupt_stop_event.is_set():
            if self.interrupt_stop_event.is_set():
                self.was_interrupted.set()
            return ""

        if on_transcription_finished:
            threading.Thread(target=on_transcription_finished,
                            args=(self.transcribe(),)).start()
        else:
            return self.transcribe()


    def format_number(self, num):
        # Convert the number to a string
        num_str = f"{num:.10f}"  # Ensure precision is sufficient
        # Split the number into integer and decimal parts
        integer_part, decimal_part = num_str.split('.')
        # Take the last two digits of the integer part and the first two digits of the decimal part
        result = f"{integer_part[-2:]}.{decimal_part[:2]}"
        return result

    def start(self, frames = None):
        """
        Starts recording audio directly without waiting for voice activity.
        """

        # Ensure there's a minimum interval
        # between stopping and starting recording
        if (time.time() - self.recording_stop_time
                < self.min_gap_between_recordings):
            logger.info("Attempted to start recording "
                         "too soon after stopping."
                         )
            return self

        logger.info("recording started")
        self._set_state("recording")
        self.text_storage = []
        self.realtime_stabilized_text = ""
        self.realtime_stabilized_safetext = ""
        self.wakeword_detected = False
        self.wake_word_detect_time = 0
        self.frames = []
        if frames:
            self.frames = frames
        self.is_recording = True

        self.recording_start_time = time.time()
        self.is_silero_speech_active = False
        self.is_webrtc_speech_active = False
        self.stop_recording_event.clear()
        self.start_recording_event.set()

        if self.on_recording_start:
            self._run_callback(self.on_recording_start)

        return self

    def stop(self,
             backdate_stop_seconds: float = 0.0,
             backdate_resume_seconds: float = 0.0,
        ):
        """
        Stops recording audio.

        Args:
        - backdate_stop_seconds (float, default="0.0"): Specifies the number of
            seconds to backdate the stop time. This is useful when the stop
            command is issued after the actual stop time.
        - backdate_resume_seconds (float, default="0.0"): Specifies the number
            of seconds to backdate the time relistening is initiated.
        """

        # Ensure there's a minimum interval
        # between starting and stopping recording
        if (time.time() - self.recording_start_time
                < self.min_length_of_recording):
            logger.info("Attempted to stop recording "
                         "too soon after starting."
                         )
            return self

        logger.info("recording stopped")
        self.last_frames = copy.deepcopy(self.frames)
        self.backdate_stop_seconds = backdate_stop_seconds
        self.backdate_resume_seconds = backdate_resume_seconds
        self.is_recording = False
        self.recording_stop_time = time.time()
        self.is_silero_speech_active = False
        self.is_webrtc_speech_active = False
        self.silero_check_time = 0
        self.start_recording_event.clear()
        self.stop_recording_event.set()

        self.last_recording_start_time = self.recording_start_time
        self.last_recording_stop_time = self.recording_stop_time

        if self.on_recording_stop:
            self._run_callback(self.on_recording_stop)

        return self

    def listen(self):
        """
        Puts recorder in immediate "listen" state.
        This is the state after a wake word detection, for example.
        The recorder now "listens" for voice activation.
        Once voice is detected we enter "recording" state.
        """
        self.listen_start = time.time()
        self._set_state("listening")
        self.start_recording_on_voice_activity = True

    def feed_audio(self, chunk, original_sample_rate=16000):
        """
        Feed an audio chunk into the processing pipeline. Chunks are
        accumulated until the buffer size is reached, and then the accumulated
        data is fed into the audio_queue.
        """
        # Check if the buffer attribute exists, if not, initialize it
        if not hasattr(self, 'buffer'):
            self.buffer = bytearray()

        # Check if input is a NumPy array
        if isinstance(chunk, np.ndarray):
            # Handle stereo to mono conversion if necessary
            if chunk.ndim == 2:
                chunk = np.mean(chunk, axis=1)

            # Resample to 16000 Hz if necessary
            if original_sample_rate != 16000:
                num_samples = int(len(chunk) * 16000 / original_sample_rate)
                chunk = resample(chunk, num_samples)

            # Ensure data type is int16
            chunk = chunk.astype(np.int16)

            # Convert the NumPy array to bytes
            chunk = chunk.tobytes()

        # Append the chunk to the buffer
        self.buffer += chunk
        buf_size = 2 * self.buffer_size  # silero complains if too short

        # Check if the buffer has reached or exceeded the buffer_size
        while len(self.buffer) >= buf_size:
            # Extract self.buffer_size amount of data from the buffer
            to_process = self.buffer[:buf_size]
            self.buffer = self.buffer[buf_size:]

            # Feed the extracted data to the audio_queue
            self.audio_queue.put(to_process)

    def set_microphone(self, microphone_on=True):
        """
        Set the microphone on or off.
        """
        logger.info("Setting microphone to: " + str(microphone_on))
        self.use_microphone.value = microphone_on

    def shutdown(self):
        """
        Safely shuts down the audio recording by stopping the
        recording worker and closing the audio stream.
        """

        with self.shutdown_lock:
            if self.is_shut_down:
                return

            print("\033[91mRealtimeSTT shutting down\033[0m")

            # Force wait_audio() and text() to exit
            self.is_shut_down = True
            self.start_recording_event.set()
            self.stop_recording_event.set()

            self.shutdown_event.set()
            self.is_recording = False
            self.is_running = False

            logger.debug('Finishing recording thread')
            if self.recording_thread:
                self.recording_thread.join()

            logger.debug('Terminating reader process')

            # Give it some time to finish the loop and cleanup.
            if self.use_microphone.value:
                self.reader_process.join(timeout=10)

                if self.reader_process.is_alive():
                    logger.warning("Reader process did not terminate "
                                    "in time. Terminating forcefully."
                                    )
                    self.reader_process.terminate()

            logger.debug('Terminating transcription process')
            self.transcript_process.join(timeout=10)

            if self.transcript_process.is_alive():
                logger.warning("Transcript process did not terminate "
                                "in time. Terminating forcefully."
                                )
                self.transcript_process.terminate()

            self.parent_transcription_pipe.close()

            logger.debug('Finishing realtime thread')
            if self.realtime_thread:
                self.realtime_thread.join()

            if self.enable_realtime_transcription:
                if self.realtime_model_type:
                    del self.realtime_model_type
                    self.realtime_model_type = None
            gc.collect()

    def _recording_worker(self):
        """
        The main worker method which constantly monitors the audio
        input for voice activity and accordingly starts/stops the recording.
        """

        if self.use_extended_logging:
            logger.debug('Debug: Entering try block')

        last_inner_try_time = 0
        try:
            if self.use_extended_logging:
                logger.debug('Debug: Initializing variables')
            time_since_last_buffer_message = 0
            was_recording = False
            delay_was_passed = False
            wakeword_detected_time = None
            wakeword_samples_to_remove = None
            self.allowed_to_early_transcribe = True

            if self.use_extended_logging:
                logger.debug('Debug: Starting main loop')
            # Continuously monitor audio for voice activity
            while self.is_running:

                # if self.use_extended_logging:
                #     logger.debug('Debug: Entering inner try block')
                if last_inner_try_time:
                    last_processing_time = time.time() - last_inner_try_time
                    if last_processing_time > 0.1:
                        if self.use_extended_logging:
                            logger.warning('### WARNING: PROCESSING TOOK TOO LONG')
                last_inner_try_time = time.time()
                try:
                    # if self.use_extended_logging:
                    #     logger.debug('Debug: Trying to get data from audio queue')
                    try:
                        data = self.audio_queue.get(timeout=0.01)
                        self.last_words_buffer.append(data)
                    except queue.Empty:
                        # if self.use_extended_logging:
                        #     logger.debug('Debug: Queue is empty, checking if still running')
                        if not self.is_running:
                            if self.use_extended_logging:
                                logger.debug('Debug: Not running, breaking loop')
                            break
                        # if self.use_extended_logging:
                        #     logger.debug('Debug: Continuing to next iteration')
                        continue

                    if self.use_extended_logging:
                        logger.debug('Debug: Checking for on_recorded_chunk callback')
                    if self.on_recorded_chunk:
                        if self.use_extended_logging:
                            logger.debug('Debug: Calling on_recorded_chunk')
                        self._run_callback(self.on_recorded_chunk, data)

                    if self.use_extended_logging:
                        logger.debug('Debug: Checking if handle_buffer_overflow is True')
                    if self.handle_buffer_overflow:
                        if self.use_extended_logging:
                            logger.debug('Debug: Handling buffer overflow')
                        # Handle queue overflow
                        if (self.audio_queue.qsize() >
                                self.allowed_latency_limit):
                            if self.use_extended_logging:
                                logger.debug('Debug: Queue size exceeds limit, logging warnings')
                            logger.warning("Audio queue size exceeds "
                                            "latency limit. Current size: "
                                            f"{self.audio_queue.qsize()}. "
                                            "Discarding old audio chunks."
                                            )

                        if self.use_extended_logging:
                            logger.debug('Debug: Discarding old chunks if necessary')
                        while (self.audio_queue.qsize() >
                                self.allowed_latency_limit):

                            data = self.audio_queue.get()

                except BrokenPipeError:
                    logger.error("BrokenPipeError _recording_worker", exc_info=True)
                    self.is_running = False
                    break

                if self.use_extended_logging:
                    logger.debug('Debug: Updating time_since_last_buffer_message')
                # Feed the extracted data to the audio_queue
                if time_since_last_buffer_message:
                    time_passed = time.time() - time_since_last_buffer_message
                    if time_passed > 1:
                        if self.use_extended_logging:
                            logger.debug("_recording_worker processing audio data")
                        time_since_last_buffer_message = time.time()
                else:
                    time_since_last_buffer_message = time.time()

                if self.use_extended_logging:
                    logger.debug('Debug: Initializing failed_stop_attempt')
                failed_stop_attempt = False

                if self.use_extended_logging:
                    logger.debug('Debug: Checking if not recording')
                if not self.is_recording:
                    if self.use_extended_logging:
                        logger.debug('Debug: Handling not recording state')
                    # Handle not recording state
                    time_since_listen_start = (time.time() - self.listen_start
                                            if self.listen_start else 0)

                    wake_word_activation_delay_passed = (
                        time_since_listen_start >
                        self.wake_word_activation_delay
                    )

                    if self.use_extended_logging:
                        logger.debug('Debug: Handling wake-word timeout callback')
                    # Handle wake-word timeout callback
                    if wake_word_activation_delay_passed \
                            and not delay_was_passed:

                        if self.use_wake_words and self.wake_word_activation_delay:
                            if self.on_wakeword_timeout:
                                if self.use_extended_logging:
                                    logger.debug('Debug: Calling on_wakeword_timeout')
                                self._run_callback(self.on_wakeword_timeout)
                    delay_was_passed = wake_word_activation_delay_passed

                    if self.use_extended_logging:
                        logger.debug('Debug: Setting state and spinner text')
                    # Set state and spinner text
                    if not self.recording_stop_time:
                        if self.use_wake_words \
                                and wake_word_activation_delay_passed \
                                and not self.wakeword_detected:
                            if self.use_extended_logging:
                                logger.debug('Debug: Setting state to "wakeword"')
                            self._set_state("wakeword")
                        else:
                            if self.listen_start:
                                if self.use_extended_logging:
                                    logger.debug('Debug: Setting state to "listening"')
                                self._set_state("listening")
                            else:
                                if self.use_extended_logging:
                                    logger.debug('Debug: Setting state to "inactive"')
                                self._set_state("inactive")

                    if self.use_extended_logging:
                        logger.debug('Debug: Checking wake word conditions')
                    if self.use_wake_words and wake_word_activation_delay_passed:
                        try:
                            if self.use_extended_logging:
                                logger.debug('Debug: Processing wakeword')
                            wakeword_index = self._process_wakeword(data)

                        except struct.error:
                            logger.error("Error unpacking audio data "
                                        "for wake word processing.", exc_info=True)
                            continue

                        except Exception as e:
                            logger.error(f"Wake word processing error: {e}", exc_info=True)
                            continue

                        if self.use_extended_logging:
                            logger.debug('Debug: Checking if wake word detected')
                        # If a wake word is detected                        
                        if wakeword_index >= 0:
                            if self.use_extended_logging:
                                logger.debug('Debug: Wake word detected, updating variables')
                            self.wake_word_detect_time = time.time()
                            wakeword_detected_time = time.time()
                            wakeword_samples_to_remove = int(self.sample_rate * self.wake_word_buffer_duration)
                            self.wakeword_detected = True
                            if self.on_wakeword_detected:
                                if self.use_extended_logging:
                                    logger.debug('Debug: Calling on_wakeword_detected')
                                self._run_callback(self.on_wakeword_detected)

                    if self.use_extended_logging:
                        logger.debug('Debug: Checking voice activity conditions')
                    # Check for voice activity to
                    # trigger the start of recording
                    if ((not self.use_wake_words
                        or not wake_word_activation_delay_passed)
                            and self.start_recording_on_voice_activity) \
                            or self.wakeword_detected:

                        if self.use_extended_logging:
                            logger.debug('Debug: Checking if voice is active')

                        if self._is_voice_active():

                            if self.on_vad_start:
                               self._run_callback(self.on_vad_start)

                            if self.use_extended_logging:
                                logger.debug('Debug: Voice activity detected')
                            logger.info("voice activity detected")

                            if self.use_extended_logging:
                                logger.debug('Debug: Starting recording')
                            self.start()

                            self.start_recording_on_voice_activity = False

                            if self.use_extended_logging:
                                logger.debug('Debug: Adding buffered audio to frames')
                            # Add the buffered audio
                            # to the recording frames
                            self.frames.extend(list(self.audio_buffer))
                            self.audio_buffer.clear()

                            if self.use_extended_logging:
                                logger.debug('Debug: Resetting Silero VAD model states')
                            self.silero_vad_model.reset_states()
                        else:
                            if self.use_extended_logging:
                                logger.debug('Debug: Checking voice activity')
                            data_copy = data[:]
                            self._check_voice_activity(data_copy)

                    if self.use_extended_logging:
                        logger.debug('Debug: Resetting speech_end_silence_start')

                    if self.speech_end_silence_start != 0:
                        self.speech_end_silence_start = 0
                        if self.on_turn_detection_stop:
                            if self.use_extended_logging:
                                logger.debug('Debug: Calling on_turn_detection_stop')
                            self._run_callback(self.on_turn_detection_stop)

                else:
                    if self.use_extended_logging:
                        logger.debug('Debug: Handling recording state')
                    # If we are currently recording
                    if wakeword_samples_to_remove and wakeword_samples_to_remove > 0:
                        if self.use_extended_logging:
                            logger.debug('Debug: Removing wakeword samples')
                        # Remove samples from the beginning of self.frames
                        samples_removed = 0
                        while wakeword_samples_to_remove > 0 and self.frames:
                            frame = self.frames[0]
                            frame_samples = len(frame) // 2  # Assuming 16-bit audio
                            if wakeword_samples_to_remove >= frame_samples:
                                self.frames.pop(0)
                                samples_removed += frame_samples
                                wakeword_samples_to_remove -= frame_samples
                            else:
                                self.frames[0] = frame[wakeword_samples_to_remove * 2:]
                                samples_removed += wakeword_samples_to_remove
                                samples_to_remove = 0
                        
                        wakeword_samples_to_remove = 0

                    if self.use_extended_logging:
                        logger.debug('Debug: Checking if stop_recording_on_voice_deactivity is True')
                    # Stop the recording if silence is detected after speech
                    if self.stop_recording_on_voice_deactivity:
                        if self.use_extended_logging:
                            logger.debug('Debug: Determining if speech is detected')
                        is_speech = (
                            self._is_silero_speech(data) if self.silero_deactivity_detection
                            else self._is_webrtc_speech(data, True)
                        )

                        if self.use_extended_logging:
                            logger.debug('Debug: Formatting speech_end_silence_start')
                        if not self.speech_end_silence_start:
                            str_speech_end_silence_start = "0"
                        else:
                            str_speech_end_silence_start = datetime.datetime.fromtimestamp(self.speech_end_silence_start).strftime('%H:%M:%S.%f')[:-3]
                        if self.use_extended_logging:
                            logger.debug(f"is_speech: {is_speech}, str_speech_end_silence_start: {str_speech_end_silence_start}")

                        if self.use_extended_logging:
                            logger.debug('Debug: Checking if speech is not detected')
                        if not is_speech:
                            if self.use_extended_logging:
                                logger.debug('Debug: Handling voice deactivity')
                            # Voice deactivity was detected, so we start
                            # measuring silence time before stopping recording
                            if self.speech_end_silence_start == 0 and \
                                (time.time() - self.recording_start_time > self.min_length_of_recording):

                                self.speech_end_silence_start = time.time()
                                self.awaiting_speech_end = True
                                if self.on_turn_detection_start:
                                    if self.use_extended_logging:
                                        logger.debug('Debug: Calling on_turn_detection_start')

                                    self._run_callback(self.on_turn_detection_start)

                            if self.use_extended_logging:
                                logger.debug('Debug: Checking early transcription conditions')
                            if self.speech_end_silence_start and self.early_transcription_on_silence and len(self.frames) > 0 and \
                                (time.time() - self.speech_end_silence_start > self.early_transcription_on_silence) and \
                                self.allowed_to_early_transcribe:
                                    if self.use_extended_logging:
                                        logger.debug("Debug:Adding early transcription request")
                                    self.transcribe_count += 1
                                    audio_array = np.frombuffer(b''.join(self.frames), dtype=np.int16)
                                    audio = audio_array.astype(np.float32) / INT16_MAX_ABS_VALUE

                                    if self.use_extended_logging:
                                        logger.debug("Debug: early transcription request pipe send")
                                    self.parent_transcription_pipe.send((audio, self.language, True))
                                    if self.use_extended_logging:
                                        logger.debug("Debug: early transcription request pipe send return")
                                    self.allowed_to_early_transcribe = False

                        else:
                            self.awaiting_speech_end = False
                            if self.use_extended_logging:
                                logger.debug('Debug: Handling speech detection')
                            if self.speech_end_silence_start:
                                if self.use_extended_logging:
                                    logger.info("Resetting self.speech_end_silence_start")

                                if self.speech_end_silence_start != 0:
                                    self.speech_end_silence_start = 0
                                    if self.on_turn_detection_stop:
                                        if self.use_extended_logging:
                                            logger.debug('Debug: Calling on_turn_detection_stop')
                                        self._run_callback(self.on_turn_detection_stop)

                                self.allowed_to_early_transcribe = True

                        if self.use_extended_logging:
                            logger.debug('Debug: Checking if silence duration exceeds threshold')
                        # Wait for silence to stop recording after speech
                        if self.speech_end_silence_start and time.time() - \
                                self.speech_end_silence_start >= \
                                self.post_speech_silence_duration:

                            if self.on_vad_stop:
                                self._run_callback(self.on_vad_stop)

                            if self.use_extended_logging:
                                logger.debug('Debug: Formatting silence start time')
                            # Get time in desired format (HH:MM:SS.nnn)
                            silence_start_time = datetime.datetime.fromtimestamp(self.speech_end_silence_start).strftime('%H:%M:%S.%f')[:-3]

                            if self.use_extended_logging:
                                logger.debug('Debug: Calculating time difference')
                            # Calculate time difference
                            time_diff = time.time() - self.speech_end_silence_start

                            if self.use_extended_logging:
                                logger.debug('Debug: Logging voice deactivity detection')
                                logger.info(f"voice deactivity detected at {silence_start_time}, "
                                        f"time since silence start: {time_diff:.3f} seconds")

                                logger.debug('Debug: Appending data to frames and stopping recording')
                            self.frames.append(data)
                            self.stop()
                            if not self.is_recording:
                                if self.speech_end_silence_start != 0:
                                    self.speech_end_silence_start = 0
                                    if self.on_turn_detection_stop:
                                        if self.use_extended_logging:
                                            logger.debug('Debug: Calling on_turn_detection_stop')
                                        self._run_callback(self.on_turn_detection_stop)

                                if self.use_extended_logging:
                                    logger.debug('Debug: Handling non-wake word scenario')
                            else:
                                if self.use_extended_logging:
                                    logger.debug('Debug: Setting failed_stop_attempt to True')
                                failed_stop_attempt = True

                            self.awaiting_speech_end = False

                if self.use_extended_logging:
                    logger.debug('Debug: Checking if recording stopped')
                if not self.is_recording and was_recording:
                    if self.use_extended_logging:
                        logger.debug('Debug: Resetting after stopping recording')
                    # Reset after stopping recording to ensure clean state
                    self.stop_recording_on_voice_deactivity = False

                if self.use_extended_logging:
                    logger.debug('Debug: Checking Silero time')
                if time.time() - self.silero_check_time > 0.1:
                    self.silero_check_time = 0

                if self.use_extended_logging:
                    logger.debug('Debug: Handling wake word timeout')
                # Handle wake word timeout (waited to long initiating
                # speech after wake word detection)
                if self.wake_word_detect_time and time.time() - \
                        self.wake_word_detect_time > self.wake_word_timeout:

                    self.wake_word_detect_time = 0
                    if self.wakeword_detected and self.on_wakeword_timeout:
                        if self.use_extended_logging:
                            logger.debug('Debug: Calling on_wakeword_timeout')
                        self._run_callback(self.on_wakeword_timeout)
                    self.wakeword_detected = False

                if self.use_extended_logging:
                    logger.debug('Debug: Updating was_recording')
                was_recording = self.is_recording

                if self.use_extended_logging:
                    logger.debug('Debug: Checking if recording and not failed stop attempt')
                if self.is_recording and not failed_stop_attempt:
                    if self.use_extended_logging:
                        logger.debug('Debug: Appending data to frames')
                    self.frames.append(data)

                if self.use_extended_logging:
                    logger.debug('Debug: Checking if not recording or speech end silence start')
                if not self.is_recording or self.speech_end_silence_start:
                    if self.use_extended_logging:
                        logger.debug('Debug: Appending data to audio buffer')
                    self.audio_buffer.append(data)

        except Exception as e:
            logger.debug('Debug: Caught exception in main try block')
            if not self.interrupt_stop_event.is_set():
                logger.error(f"Unhandled exeption in _recording_worker: {e}", exc_info=True)
                raise

        if self.use_extended_logging:
            logger.debug('Debug: Exiting _recording_worker method')




    def _realtime_worker(self):
        """
        Performs real-time transcription if the feature is enabled.

        The method is responsible transcribing recorded audio frames
          in real-time based on the specified resolution interval.
        The transcribed text is stored in `self.realtime_transcription_text`
          and a callback
        function is invoked with this text if specified.
        """

        try:

            logger.debug('Starting realtime worker')

            # Return immediately if real-time transcription is not enabled
            if not self.enable_realtime_transcription:
                return

            # Track time of last transcription
            last_transcription_time = time.time()

            while self.is_running:

                if self.is_recording:

                    # MODIFIED SLEEP LOGIC:
                    # Wait until realtime_processing_pause has elapsed,
                    # but check often so we can respond to changes quickly.
                    while (
                        time.time() - last_transcription_time
                    ) < self.realtime_processing_pause:
                        time.sleep(0.001)
                        if not self.is_running or not self.is_recording:
                            break

                    if self.awaiting_speech_end:
                        time.sleep(0.001)
                        continue

                    # Update transcription time
                    last_transcription_time = time.time()

                    # Convert the buffer frames to a NumPy array
                    audio_array = np.frombuffer(
                        b''.join(self.frames),
                        dtype=np.int16
                        )

                    logger.debug(f"Current realtime buffer size: {len(audio_array)}")

                    # Normalize the array to a [-1, 1] range
                    audio_array = audio_array.astype(np.float32) / \
                        INT16_MAX_ABS_VALUE

                    if self.use_main_model_for_realtime:
                        with self.transcription_lock:
                            try:
                                self.parent_transcription_pipe.send((audio_array, self.language, True))
                                if self.parent_transcription_pipe.poll(timeout=5):  # Wait for 5 seconds
                                    logger.debug("Receive from realtime worker after transcription request to main model")
                                    status, result = self.parent_transcription_pipe.recv()
                                    if status == 'success':
                                        segments, info = result
                                        self.detected_realtime_language = info.language if info.language_probability > 0 else None
                                        self.detected_realtime_language_probability = info.language_probability
                                        realtime_text = segments
                                        logger.debug(f"Realtime text detected with main model: {realtime_text}")
                                    else:
                                        logger.error(f"Realtime transcription error: {result}")
                                        continue
                                else:
                                    logger.warning("Realtime transcription timed out")
                                    continue
                            except Exception as e:
                                logger.error(f"Error in realtime transcription: {str(e)}", exc_info=True)
                                continue
                    else:
                        # Perform transcription and assemble the text
                        if self.normalize_audio:
                            # normalize audio to -0.95 dBFS
                            if audio_array is not None and audio_array.size > 0:
                                peak = np.max(np.abs(audio_array))
                                if peak > 0:
                                    audio_array = (audio_array / peak) * 0.95

                        if self.realtime_batch_size > 0:
                            segments, info = self.realtime_model_type.transcribe(
                                audio_array,
                                language=self.language if self.language else None,
                                beam_size=self.beam_size_realtime,
                                initial_prompt=self.initial_prompt_realtime,
                                suppress_tokens=self.suppress_tokens,
                                batch_size=self.realtime_batch_size,
                                vad_filter=self.faster_whisper_vad_filter
                            )
                        else:
                            segments, info = self.realtime_model_type.transcribe(
                                audio_array,
                                language=self.language if self.language else None,
                                beam_size=self.beam_size_realtime,
                                initial_prompt=self.initial_prompt_realtime,
                                suppress_tokens=self.suppress_tokens,
                                vad_filter=self.faster_whisper_vad_filter
                            )

                        self.detected_realtime_language = info.language if info.language_probability > 0 else None
                        self.detected_realtime_language_probability = info.language_probability
                        realtime_text = " ".join(
                            seg.text for seg in segments
                        )
                        logger.debug(f"Realtime text detected: {realtime_text}")

                    # double check recording state
                    # because it could have changed mid-transcription
                    if self.is_recording and time.time() - \
                            self.recording_start_time > self.init_realtime_after_seconds:

                        self.realtime_transcription_text = realtime_text
                        self.realtime_transcription_text = \
                            self.realtime_transcription_text.strip()

                        self.text_storage.append(
                            self.realtime_transcription_text
                            )

                        # Take the last two texts in storage, if they exist
                        if len(self.text_storage) >= 2:
                            last_two_texts = self.text_storage[-2:]

                            # Find the longest common prefix
                            # between the two texts
                            prefix = os.path.commonprefix(
                                [last_two_texts[0], last_two_texts[1]]
                                )

                            # This prefix is the text that was transcripted
                            # two times in the same way
                            # Store as "safely detected text"
                            if len(prefix) >= \
                                    len(self.realtime_stabilized_safetext):

                                # Only store when longer than the previous
                                # as additional security
                                self.realtime_stabilized_safetext = prefix

                        # Find parts of the stabilized text
                        # in the freshly transcripted text
                        matching_pos = self._find_tail_match_in_text(
                            self.realtime_stabilized_safetext,
                            self.realtime_transcription_text
                            )

                        if matching_pos < 0:
                            # pick which text to send
                            text_to_send = (
                                self.realtime_stabilized_safetext
                                if self.realtime_stabilized_safetext
                                else self.realtime_transcription_text
                            )
                            # preprocess once
                            processed = self._preprocess_output(text_to_send, True)
                            # invoke on its own thread
                            self._run_callback(self._on_realtime_transcription_stabilized, processed)

                        else:
                            # We found parts of the stabilized text
                            # in the transcripted text
                            # We now take the stabilized text
                            # and add only the freshly transcripted part to it
                            output_text = self.realtime_stabilized_safetext + \
                                self.realtime_transcription_text[matching_pos:]

                            # This yields us the "left" text part as stabilized
                            # AND at the same time delivers fresh detected
                            # parts on the first run without the need for
                            # two transcriptions
                            self._run_callback(self._on_realtime_transcription_stabilized, self._preprocess_output(output_text, True))

                        # Invoke the callback with the transcribed text
                        self._run_callback(self._on_realtime_transcription_update, self._preprocess_output(self.realtime_transcription_text,True))

                # If not recording, sleep briefly before checking again
                else:
                    time.sleep(TIME_SLEEP)

        except Exception as e:
            logger.error(f"Unhandled exeption in _realtime_worker: {e}", exc_info=True)
            raise

    def _is_silero_speech(self, chunk):
        """
        Returns true if speech is detected in the provided audio data

        Args:
            data (bytes): raw bytes of audio data (1024 raw bytes with
            16000 sample rate and 16 bits per sample)
        """
        if self.sample_rate != 16000:
            pcm_data = np.frombuffer(chunk, dtype=np.int16)
            data_16000 = signal.resample_poly(
                pcm_data, 16000, self.sample_rate)
            chunk = data_16000.astype(np.int16).tobytes()

        self.silero_working = True
        audio_chunk = np.frombuffer(chunk, dtype=np.int16)
        audio_chunk = audio_chunk.astype(np.float32) / INT16_MAX_ABS_VALUE
        vad_prob = self.silero_vad_model(
            torch.from_numpy(audio_chunk),
            SAMPLE_RATE).item()
        is_silero_speech_active = vad_prob > (1 - self.silero_sensitivity)
        if is_silero_speech_active:
            if not self.is_silero_speech_active and self.use_extended_logging:
                logger.info(f"{bcolors.OKGREEN}Silero VAD detected speech{bcolors.ENDC}")
        elif self.is_silero_speech_active and self.use_extended_logging:
            logger.info(f"{bcolors.WARNING}Silero VAD detected silence{bcolors.ENDC}")
        self.is_silero_speech_active = is_silero_speech_active
        self.silero_working = False
        return is_silero_speech_active

    def _is_webrtc_speech(self, chunk, all_frames_must_be_true=False):
        """
        Returns true if speech is detected in the provided audio data

        Args:
            data (bytes): raw bytes of audio data (1024 raw bytes with
            16000 sample rate and 16 bits per sample)
        """
        speech_str = f"{bcolors.OKGREEN}WebRTC VAD detected speech{bcolors.ENDC}"
        silence_str = f"{bcolors.WARNING}WebRTC VAD detected silence{bcolors.ENDC}"
        if self.sample_rate != 16000:
            pcm_data = np.frombuffer(chunk, dtype=np.int16)
            data_16000 = signal.resample_poly(
                pcm_data, 16000, self.sample_rate)
            chunk = data_16000.astype(np.int16).tobytes()

        # Number of audio frames per millisecond
        frame_length = int(16000 * 0.01)  # for 10ms frame
        num_frames = int(len(chunk) / (2 * frame_length))
        speech_frames = 0

        for i in range(num_frames):
            start_byte = i * frame_length * 2
            end_byte = start_byte + frame_length * 2
            frame = chunk[start_byte:end_byte]
            if self.webrtc_vad_model.is_speech(frame, 16000):
                speech_frames += 1
                if not all_frames_must_be_true:
                    if self.debug_mode:
                        logger.info(f"Speech detected in frame {i + 1}"
                              f" of {num_frames}")
                    if not self.is_webrtc_speech_active and self.use_extended_logging:
                        logger.info(speech_str)
                    self.is_webrtc_speech_active = True
                    return True
        if all_frames_must_be_true:
            if self.debug_mode and speech_frames == num_frames:
                logger.info(f"Speech detected in {speech_frames} of "
                      f"{num_frames} frames")
            elif self.debug_mode:
                logger.info(f"Speech not detected in all {num_frames} frames")
            speech_detected = speech_frames == num_frames
            if speech_detected and not self.is_webrtc_speech_active and self.use_extended_logging:
                logger.info(speech_str)
            elif not speech_detected and self.is_webrtc_speech_active and self.use_extended_logging:
                logger.info(silence_str)
            self.is_webrtc_speech_active = speech_detected
            return speech_detected
        else:
            if self.debug_mode:
                logger.info(f"Speech not detected in any of {num_frames} frames")
            if self.is_webrtc_speech_active and self.use_extended_logging:
                logger.info(silence_str)
            self.is_webrtc_speech_active = False
            return False

    def _check_voice_activity(self, data):
        """
        Initiate check if voice is active based on the provided data.

        Args:
            data: The audio data to be checked for voice activity.
        """
        self._is_webrtc_speech(data)

        # First quick performing check for voice activity using WebRTC
        if self.is_webrtc_speech_active:

            if not self.silero_working:
                self.silero_working = True

                # Run the intensive check in a separate thread
                threading.Thread(
                    target=self._is_silero_speech,
                    args=(data,)).start()

    def clear_audio_queue(self):
        """
        Safely empties the audio queue to ensure no remaining audio 
        fragments get processed e.g. after waking up the recorder.
        """
        self.audio_buffer.clear()
        try:
            while True:
                self.audio_queue.get_nowait()
        except:
            # PyTorch's mp.Queue doesn't have a specific Empty exception
            # so we catch any exception that might occur when the queue is empty
            pass

    def _is_voice_active(self):
        """
        Determine if voice is active.

        Returns:
            bool: True if voice is active, False otherwise.
        """
        return self.is_webrtc_speech_active and self.is_silero_speech_active

    def _set_state(self, new_state):
        """
        Update the current state of the recorder and execute
        corresponding state-change callbacks.

        Args:
            new_state (str): The new state to set.

        """
        # Check if the state has actually changed
        if new_state == self.state:
            return

        # Store the current state for later comparison
        old_state = self.state

        # Update to the new state
        self.state = new_state

        # Log the state change
        logger.info(f"State changed from '{old_state}' to '{new_state}'")

        # Execute callbacks based on transitioning FROM a particular state
        if old_state == "listening":
            if self.on_vad_detect_stop:
                self._run_callback(self.on_vad_detect_stop)
        elif old_state == "wakeword":
            if self.on_wakeword_detection_end:
                self._run_callback(self.on_wakeword_detection_end)

        # Execute callbacks based on transitioning TO a particular state
        if new_state == "listening":
            if self.on_vad_detect_start:
                self._run_callback(self.on_vad_detect_start)
            self._set_spinner("speak now")
            if self.spinner and self.halo:
                self.halo._interval = 250
        elif new_state == "wakeword":
            if self.on_wakeword_detection_start:
                self._run_callback(self.on_wakeword_detection_start)
            self._set_spinner(f"say {self.wake_words}")
            if self.spinner and self.halo:
                self.halo._interval = 500
        elif new_state == "transcribing":
            self._set_spinner("transcribing")
            if self.spinner and self.halo:
                self.halo._interval = 50
        elif new_state == "recording":
            self._set_spinner("recording")
            if self.spinner and self.halo:
                self.halo._interval = 100
        elif new_state == "inactive":
            if self.spinner and self.halo:
                self.halo.stop()
                self.halo = None

    def _set_spinner(self, text):
        """
        Update the spinner's text or create a new
        spinner with the provided text.

        Args:
            text (str): The text to be displayed alongside the spinner.
        """
        if self.spinner:
            # If the Halo spinner doesn't exist, create and start it
            if self.halo is None:
                self.halo = halo.Halo(text=text)
                self.halo.start()
            # If the Halo spinner already exists, just update the text
            else:
                self.halo.text = text

    def _preprocess_output(self, text, preview=False):
        """
        Preprocesses the output text by removing any leading or trailing
        whitespace, converting all whitespace sequences to a single space
        character, and capitalizing the first character of the text.

        Args:
            text (str): The text to be preprocessed.

        Returns:
            str: The preprocessed text.
        """
        text = re.sub(r'\s+', ' ', text.strip())

        if self.ensure_sentence_starting_uppercase:
            if text:
                text = text[0].upper() + text[1:]

        # Ensure the text ends with a proper punctuation
        # if it ends with an alphanumeric character
        if not preview:
            if self.ensure_sentence_ends_with_period:
                if text and text[-1].isalnum():
                    text += '.'

        return text

    def _find_tail_match_in_text(self, text1, text2, length_of_match=10):
        """
        Find the position where the last 'n' characters of text1
        match with a substring in text2.

        This method takes two texts, extracts the last 'n' characters from
        text1 (where 'n' is determined by the variable 'length_of_match'), and
        searches for an occurrence of this substring in text2, starting from
        the end of text2 and moving towards the beginning.

        Parameters:
        - text1 (str): The text containing the substring that we want to find
          in text2.
        - text2 (str): The text in which we want to find the matching
          substring.
        - length_of_match(int): The length of the matching string that we are
          looking for

        Returns:
        int: The position (0-based index) in text2 where the matching
          substring starts. If no match is found or either of the texts is
          too short, returns -1.
        """

        # Check if either of the texts is too short
        if len(text1) < length_of_match or len(text2) < length_of_match:
            return -1

        # The end portion of the first text that we want to compare
        target_substring = text1[-length_of_match:]

        # Loop through text2 from right to left
        for i in range(len(text2) - length_of_match + 1):
            # Extract the substring from text2
            # to compare with the target_substring
            current_substring = text2[len(text2) - i - length_of_match:
                                      len(text2) - i]

            # Compare the current_substring with the target_substring
            if current_substring == target_substring:
                # Position in text2 where the match starts
                return len(text2) - i

        return -1

    def _on_realtime_transcription_stabilized(self, text):
        """
        Callback method invoked when the real-time transcription stabilizes.

        This method is called internally when the transcription text is
        considered "stable" meaning it's less likely to change significantly
        with additional audio input. It notifies any registered external
        listener about the stabilized text if recording is still ongoing.
        This is particularly useful for applications that need to display
        live transcription results to users and want to highlight parts of the
        transcription that are less likely to change.

        Args:
            text (str): The stabilized transcription text.
        """
        if self.on_realtime_transcription_stabilized:
            if self.is_recording:
                self._run_callback(self.on_realtime_transcription_stabilized, text)

    def _on_realtime_transcription_update(self, text):
        """
        Callback method invoked when there's an update in the real-time
        transcription.

        This method is called internally whenever there's a change in the
        transcription text, notifying any registered external listener about
        the update if recording is still ongoing. This provides a mechanism
        for applications to receive and possibly display live transcription
        updates, which could be partial and still subject to change.

        Args:
            text (str): The updated transcription text.
        """
        if self.on_realtime_transcription_update:
            if self.is_recording:
                self._run_callback(self.on_realtime_transcription_update, text)

    def __enter__(self):
        """
        Method to setup the context manager protocol.

        This enables the instance to be used in a `with` statement, ensuring
        proper resource management. When the `with` block is entered, this
        method is automatically called.

        Returns:
            self: The current instance of the class.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Method to define behavior when the context manager protocol exits.

        This is called when exiting the `with` block and ensures that any
        necessary cleanup or resource release processes are executed, such as
        shutting down the system properly.

        Args:
            exc_type (Exception or None): The type of the exception that
              caused the context to be exited, if any.
            exc_value (Exception or None): The exception instance that caused
              the context to be exited, if any.
            traceback (Traceback or None): The traceback corresponding to the
              exception, if any.
        """
        self.shutdown()
````

## File: RealtimeSTT/safepipe.py
````python
import sys
import multiprocessing as mp
import queue
import threading
import time
import logging

# Configure logging. Adjust level and formatting as needed.
# logging.basicConfig(level=logging.DEBUG,
#                     format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    # Only set the start method if it hasn't been set already.
    if sys.platform.startswith('linux') or sys.platform == 'darwin':  # For Linux or macOS
        mp.set_start_method("spawn")
    elif mp.get_start_method(allow_none=True) is None:
        mp.set_start_method("spawn")
except RuntimeError as e:
    logger.debug("Start method has already been set. Details: %s", e)


class ParentPipe:
    """
    A thread-safe wrapper around the 'parent end' of a multiprocessing pipe.
    All actual pipe operations happen in a dedicated worker thread, so it's safe
    for multiple threads to call send(), recv(), or poll() on the same ParentPipe
    without interfering.
    """
    def __init__(self, parent_synthesize_pipe):
        self.name = "ParentPipe"
        self._pipe = parent_synthesize_pipe  # The raw pipe.
        self._closed = False  # A flag to mark if close() has been called.

        # The request queue for sending operations to the worker.
        self._request_queue = queue.Queue()

        # This event signals the worker thread to stop.
        self._stop_event = threading.Event()

        # Worker thread that executes actual .send(), .recv(), .poll() calls.
        self._worker_thread = threading.Thread(
            target=self._pipe_worker,
            name=f"{self.name}_Worker",
            daemon=True
        )
        self._worker_thread.start()

    def _pipe_worker(self):
        while not self._stop_event.is_set():
            try:
                request = self._request_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if request["type"] == "CLOSE":
                # Exit worker loop on CLOSE request.
                break

            try:
                if request["type"] == "SEND":
                    data = request["data"]
                    logger.debug("[%s] Worker: sending => %s", self.name, data)
                    self._pipe.send(data)
                    request["result_queue"].put(None)

                elif request["type"] == "RECV":
                    logger.debug("[%s] Worker: receiving...", self.name)
                    data = self._pipe.recv()
                    request["result_queue"].put(data)

                elif request["type"] == "POLL":
                    timeout = request.get("timeout", 0.0)
                    logger.debug("[%s] Worker: poll() with timeout: %s", self.name, timeout)
                    result = self._pipe.poll(timeout)
                    request["result_queue"].put(result)

            except (EOFError, BrokenPipeError, OSError) as e:
                # When the other end has closed or an error occurs,
                # log and notify the waiting thread.
                logger.debug("[%s] Worker: pipe closed or error occurred (%s). Shutting down.", self.name, e)
                request["result_queue"].put(None)
                break

            except Exception as e:
                logger.exception("[%s] Worker: unexpected error.", self.name)
                request["result_queue"].put(e)
                break

        logger.debug("[%s] Worker: stopping.", self.name)
        try:
            self._pipe.close()
        except Exception as e:
            logger.debug("[%s] Worker: error during pipe close: %s", self.name, e)

    def send(self, data):
        """
        Synchronously asks the worker thread to perform .send().
        """
        if self._closed:
            logger.debug("[%s] send() called but pipe is already closed", self.name)
            return
        logger.debug("[%s] send() requested with: %s", self.name, data)
        result_queue = queue.Queue()
        request = {
            "type": "SEND",
            "data": data,
            "result_queue": result_queue
        }
        self._request_queue.put(request)
        result_queue.get()  # Wait until sending completes.
        logger.debug("[%s] send() completed", self.name)

    def recv(self):
        """
        Synchronously asks the worker to perform .recv() and returns the data.
        """
        if self._closed:
            logger.debug("[%s] recv() called but pipe is already closed", self.name)
            return None
        logger.debug("[%s] recv() requested", self.name)
        result_queue = queue.Queue()
        request = {
            "type": "RECV",
            "result_queue": result_queue
        }
        self._request_queue.put(request)
        data = result_queue.get()

        # Log a preview for huge byte blobs.
        if isinstance(data, tuple) and len(data) == 2 and isinstance(data[1], bytes):
            data_preview = (data[0], f"<{len(data[1])} bytes>")
        else:
            data_preview = data
        logger.debug("[%s] recv() returning => %s", self.name, data_preview)
        return data

    def poll(self, timeout=0.0):
        """
        Synchronously checks whether data is available.
        Returns True if data is ready, or False otherwise.
        """
        if self._closed:
            return False
        logger.debug("[%s] poll() requested with timeout: %s", self.name, timeout)
        result_queue = queue.Queue()
        request = {
            "type": "POLL",
            "timeout": timeout,
            "result_queue": result_queue
        }
        self._request_queue.put(request)
        try:
            # Use a slightly longer timeout to give the worker a chance.
            result = result_queue.get(timeout=timeout + 0.1)
        except queue.Empty:
            result = False
        logger.debug("[%s] poll() returning => %s", self.name, result)
        return result

    def close(self):
        """
        Closes the pipe and stops the worker thread. The _closed flag makes
        sure no further operations are attempted.
        """
        if self._closed:
            return
        logger.debug("[%s] close() called", self.name)
        self._closed = True
        stop_request = {"type": "CLOSE", "result_queue": queue.Queue()}
        self._request_queue.put(stop_request)
        self._stop_event.set()
        self._worker_thread.join()
        logger.debug("[%s] closed", self.name)


def SafePipe(debug=False):
    """
    Returns a pair: (thread-safe parent pipe, raw child pipe).
    """
    parent_synthesize_pipe, child_synthesize_pipe = mp.Pipe()
    parent_pipe = ParentPipe(parent_synthesize_pipe)
    return parent_pipe, child_synthesize_pipe


def child_process_code(child_end):
    """
    Example child process code that receives messages, logs them,
    sends acknowledgements, and then closes.
    """
    for i in range(3):
        msg = child_end.recv()
        logger.debug("[Child] got: %s", msg)
        child_end.send(f"ACK: {msg}")
    child_end.close()


if __name__ == "__main__":
    parent_pipe, child_pipe = SafePipe()

    # Create child process with the child_process_code function.
    p = mp.Process(target=child_process_code, args=(child_pipe,))
    p.start()

    # Event to signal sender threads to stop if needed.
    stop_polling_event = threading.Event()

    def sender_thread(n):
        try:
            parent_pipe.send(f"hello_from_thread_{n}")
        except Exception as e:
            logger.debug("[sender_thread_%s] send exception: %s", n, e)
            return

        # Use a poll loop with error handling.
        for _ in range(10):
            try:
                if parent_pipe.poll(0.1):
                    reply = parent_pipe.recv()
                    logger.debug("[sender_thread_%s] got: %s", n, reply)
                    break
                else:
                    logger.debug("[sender_thread_%s] no data yet...", n)
            except (OSError, EOFError, BrokenPipeError) as e:
                logger.debug("[sender_thread_%s] poll/recv exception: %s. Exiting thread.", n, e)
                break

            # Allow exit if a shutdown is signaled.
            if stop_polling_event.is_set():
                logger.debug("[sender_thread_%s] stop event set. Exiting thread.", n)
                break

    threads = []
    for i in range(3):
        t = threading.Thread(target=sender_thread, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Signal shutdown to any polling threads, then close the pipe.
    stop_polling_event.set()
    parent_pipe.close()
    p.join()
````

## File: RealtimeSTT_server/index.html
````html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Browser STT Client</title>
  <style>
    body {
      background-color: #f4f4f9;
      color: #333;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }
    #container {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      max-width: 700px;
      padding: 20px;
      box-sizing: border-box;
      gap: 20px; /* Add more vertical space between items */
      height: 90%; /* Fixed height to prevent layout shift */
    }
    #status {
      color: #0056b3;
      font-size: 20px;
      text-align: center;
    }
    #transcriptionContainer {
      height: 90px; /* Fixed height for approximately 3 lines of text */
      overflow-y: auto;
      width: 100%;
      padding: 10px;
      box-sizing: border-box;
      background-color: #f9f9f9;
      border: 1px solid #ddd;
      border-radius: 5px;
    }
    #transcription {
      font-size: 18px;
      line-height: 1.6;
      color: #333;
      word-wrap: break-word;
    }
    #fullTextContainer {
      height: 150px; /* Fixed height to prevent layout shift */
      overflow-y: auto;
      width: 100%;
      padding: 10px;
      box-sizing: border-box;
      background-color: #f9f9f9;
      border: 1px solid #ddd;
      border-radius: 5px;
    }
    #fullText {
      color: #4CAF50;
      font-size: 18px;
      font-weight: 600;
      word-wrap: break-word;
    }
    .last-word {
      color: #007bff;
      font-weight: 600;
    }
    button {
      padding: 12px 24px;
      font-size: 16px;
      cursor: pointer;
      border: none;
      border-radius: 5px;
      margin: 5px;
      transition: background-color 0.3s ease;
      color: #fff;
      background-color: #0056b3;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    button:hover {
      background-color: #007bff;
    }
    button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }
  </style>
</head>
<body>
  <div id="container">
    <div id="status">Press "Start Recording"...</div>
    <button id="startButton" onclick="startRecording()">Start Recording</button>
    <button id="stopButton" onclick="stopRecording()" disabled>Stop Recording</button>
    <div id="transcriptionContainer">
      <div id="transcription" class="realtime"></div>
    </div>
    <div id="fullTextContainer">
      <div id="fullText"></div>
    </div>
  </div>

  <script>
    const statusDiv = document.getElementById("status");
    const transcriptionDiv = document.getElementById("transcription");
    const fullTextDiv = document.getElementById("fullText");
    const startButton = document.getElementById("startButton");
    const stopButton = document.getElementById("stopButton");

    const controlURL = "ws://127.0.0.1:8011";
    const dataURL = "ws://127.0.0.1:8012";
    let dataSocket;
    let audioContext;
    let mediaStream;
    let mediaProcessor;

    // Connect to the data WebSocket
    function connectToDataSocket() {
      dataSocket = new WebSocket(dataURL);

      dataSocket.onopen = () => {
        statusDiv.textContent = "Connected to STT server.";
        console.log("Connected to data WebSocket.");
      };

      dataSocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === "realtime") {
            // Show real-time transcription with the last word in bold, orange
            let words = message.text.split(" ");
            let lastWord = words.pop();
            transcriptionDiv.innerHTML = `${words.join(" ")} <span class="last-word">${lastWord}</span>`;

            // Auto-scroll to the bottom of the transcription container
            const transcriptionContainer = document.getElementById("transcriptionContainer");
            transcriptionContainer.scrollTop = transcriptionContainer.scrollHeight;
          } else if (message.type === "fullSentence") {
            // Accumulate the final transcription in green
            fullTextDiv.innerHTML += message.text + " ";
            transcriptionDiv.innerHTML = message.text;

            // Scroll to the bottom of fullTextContainer when new text is added
            const fullTextContainer = document.getElementById("fullTextContainer");
            fullTextContainer.scrollTop = fullTextContainer.scrollHeight;
          }
        } catch (e) {
          console.error("Error parsing message:", e);
        }
      };

      dataSocket.onclose = () => {
        statusDiv.textContent = "Disconnected from STT server.";
      };

      dataSocket.onerror = (error) => {
        console.error("WebSocket error:", error);
        statusDiv.textContent = "Error connecting to the STT server.";
      };
    }

    // Start recording audio from the microphone
    async function startRecording() {
      try {
        startButton.disabled = true;
        stopButton.disabled = false;
        statusDiv.textContent = "Recording...";
        transcriptionDiv.textContent = "";
        fullTextDiv.textContent = "";

        audioContext = new AudioContext();
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const input = audioContext.createMediaStreamSource(mediaStream);

        // Set up processor for audio chunks
        mediaProcessor = audioContext.createScriptProcessor(1024, 1, 1);
        mediaProcessor.onaudioprocess = (event) => {
          const audioData = event.inputBuffer.getChannelData(0);
          sendAudioChunk(audioData, audioContext.sampleRate);
        };

        input.connect(mediaProcessor);
        mediaProcessor.connect(audioContext.destination);

        connectToDataSocket();
      } catch (error) {
        console.error("Error accessing microphone:", error);
        statusDiv.textContent = "Error accessing microphone.";
        stopRecording();
      }
    }

    // Stop recording audio and close resources
    function stopRecording() {
      if (mediaProcessor && audioContext) {
        mediaProcessor.disconnect();
        audioContext.close();
      }

      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }

      if (dataSocket) {
        dataSocket.close();
      }

      startButton.disabled = false;
      stopButton.disabled = true;
      statusDiv.textContent = "Stopped recording.";
    }

    // Send an audio chunk to the server
    function sendAudioChunk(audioData, sampleRate) {
      if (dataSocket && dataSocket.readyState === WebSocket.OPEN) {
        const float32Array = new Float32Array(audioData);
        const pcm16Data = new Int16Array(float32Array.length);

        for (let i = 0; i < float32Array.length; i++) {
          pcm16Data[i] = Math.max(-1, Math.min(1, float32Array[i])) * 0x7FFF;
        }

        const metadata = JSON.stringify({ sampleRate });
        const metadataLength = new Uint32Array([metadata.length]);
        const metadataBuffer = new TextEncoder().encode(metadata);

        const message = new Uint8Array(
          metadataLength.byteLength + metadataBuffer.byteLength + pcm16Data.byteLength
        );
        
        message.set(new Uint8Array(metadataLength.buffer), 0);
        message.set(metadataBuffer, metadataLength.byteLength);
        message.set(new Uint8Array(pcm16Data.buffer), metadataLength.byteLength + metadataBuffer.byteLength);

        dataSocket.send(message);
      }
    }
  </script>
</body>
</html>
````

## File: RealtimeSTT_server/install_packages.py
````python
import subprocess
import sys
import importlib

def check_and_install_packages(packages):
    """
    Checks if the specified packages are installed, and if not, prompts the user
    to install them.

    Parameters:
    - packages: A list of dictionaries, each containing:
        - 'module_name': The module or package name to import.
        - 'attribute': (Optional) The attribute or class to check within the module.
        - 'install_name': The name used in the pip install command.
        - 'version': (Optional) Version constraint for the package.
    """
    for package in packages:
        module_name = package['module_name']
        attribute = package.get('attribute')
        install_name = package.get('install_name', module_name)
        version = package.get('version', '')

        try:
            # Attempt to import the module
            module = importlib.import_module(module_name)
            # If an attribute is specified, check if it exists
            if attribute:
                getattr(module, attribute)
        except (ImportError, AttributeError):
            user_input = input(
                f"This program requires '{module_name}'"
                f"{'' if not attribute else ' with attribute ' + attribute}, which is not installed or missing.\n"
                f"Do you want to install '{install_name}' now? (y/n): "
            )
            if user_input.strip().lower() == 'y':
                try:
                    # Build the pip install command
                    install_command = [sys.executable, "-m", "pip", "install"]
                    if version:
                        install_command.append(f"{install_name}{version}")
                    else:
                        install_command.append(install_name)

                    subprocess.check_call(install_command)
                    # Try to import again after installation
                    module = importlib.import_module(module_name)
                    if attribute:
                        getattr(module, attribute)
                    print(f"Successfully installed '{install_name}'.")
                except Exception as e:
                    print(f"An error occurred while installing '{install_name}': {e}")
                    sys.exit(1)
            else:
                print(f"The program requires '{install_name}' to run. Exiting...")
                sys.exit(1)
````

## File: RealtimeSTT_server/README.md
````markdown
# RealtimeSTT Server and Client

This directory contains the server and client implementations for the RealtimeSTT library, providing real-time speech-to-text transcription with WebSocket interfaces. The server allows clients to connect via WebSocket to send audio data and receive real-time transcription updates. The client handles communication with the server, allowing audio recording, parameter management, and control commands.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Server Usage](#server-usage)
  - [Starting the Server](#starting-the-server)
  - [Server Parameters](#server-parameters)
- [Client Usage](#client-usage)
  - [Starting the Client](#starting-the-client)
  - [Client Parameters](#client-parameters)
- [WebSocket Interface](#websocket-interface)
- [Examples](#examples)
  - [Starting the Server and Client](#starting-the-server-and-client)
  - [Setting Parameters](#setting-parameters)
  - [Retrieving Parameters](#retrieving-parameters)
  - [Calling Server Methods](#calling-server-methods)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Real-Time Transcription**: Provides real-time speech-to-text transcription using pre-configured or user-defined STT models.
- **WebSocket Communication**: Makes use of WebSocket connections for control commands and data handling.
- **Flexible Recording Options**: Supports configurable pauses for sentence detection and various voice activity detection (VAD) methods.
- **VAD Support**: Includes support for Silero and WebRTC VAD for robust voice activity detection.
- **Wake Word Detection**: Capable of detecting wake words to initiate transcription.
- **Configurable Parameters**: Allows fine-tuning of recording and transcription settings via command-line arguments or control commands.

## Installation

Ensure you have Python 3.8 or higher installed. Install the required packages using:

```bash
pip install git+https://github.com/KoljaB/RealtimeSTT.git@dev
```

## Server Usage

### Starting the Server

Start the server using the command-line interface:

```bash
stt-server [OPTIONS]
```

The server will initialize and begin listening for WebSocket connections on the specified control and data ports.

### Server Parameters

You can configure the server using the following command-line arguments:

### Available Parameters:

#### `-m`, `--model`

- **Type**: `str`
- **Default**: `'large-v2'`
- **Description**: Path to the Speech-to-Text (STT) model or specify a model size. Options include: `tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large-v1`, `large-v2`, or any HuggingFace CTranslate2 STT model such as `deepdml/faster-whisper-large-v3-turbo-ct2`.

#### `-r`, `--rt-model`, `--realtime_model_type`

- **Type**: `str`
- **Default**: `'tiny.en'`
- **Description**: Model size for real-time transcription. Options are the same as for `--model`. This is used only if real-time transcription is enabled (`--enable_realtime_transcription`).

#### `-l`, `--lang`, `--language`

- **Type**: `str`
- **Default**: `'en'`
- **Description**: Language code for the STT model to transcribe in a specific language. Leave this empty for auto-detection based on input audio. Default is `'en'`. [List of supported language codes](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py#L11-L110).

#### `-i`, `--input-device`, `--input_device_index`

- **Type**: `int`
- **Default**: `1`
- **Description**: Index of the audio input device to use. Use this option to specify a particular microphone or audio input device based on your system.

#### `-c`, `--control`, `--control_port`

- **Type**: `int`
- **Default**: `8011`
- **Description**: The port number used for the control WebSocket connection. Control connections are used to send and receive commands to the server.

#### `-d`, `--data`, `--data_port`

- **Type**: `int`
- **Default**: `8012`
- **Description**: The port number used for the data WebSocket connection. Data connections are used to send audio data and receive transcription updates in real time.

#### `-w`, `--wake_words`

- **Type**: `str`
- **Default**: `""` (empty string)
- **Description**: Specify the wake word(s) that will trigger the server to start listening. For example, setting this to `"Jarvis"` will make the system start transcribing when it detects the wake word `"Jarvis"`.

#### `-D`, `--debug`

- **Action**: `store_true`
- **Description**: Enable debug logging for detailed server operations.

#### `-W`, `--write`

- **Metavar**: `FILE`
- **Description**: Save received audio to a WAV file.

#### `--silero_sensitivity`

- **Type**: `float`
- **Default**: `0.05`
- **Description**: Sensitivity level for Silero Voice Activity Detection (VAD), with a range from `0` to `1`. Lower values make the model less sensitive, useful for noisy environments.

#### `--silero_use_onnx`

- **Action**: `store_true`
- **Default**: `False`
- **Description**: Enable the ONNX version of the Silero model for faster performance with lower resource usage.

#### `--webrtc_sensitivity`

- **Type**: `int`
- **Default**: `3`
- **Description**: Sensitivity level for WebRTC Voice Activity Detection (VAD), with a range from `0` to `3`. Higher values make the model less sensitive, useful for cleaner environments.

#### `--min_length_of_recording`

- **Type**: `float`
- **Default**: `1.1`
- **Description**: Minimum duration of valid recordings in seconds. This prevents very short recordings from being processed, which could be caused by noise or accidental sounds.

#### `--min_gap_between_recordings`

- **Type**: `float`
- **Default**: `0`
- **Description**: Minimum time (in seconds) between consecutive recordings. Setting this helps avoid overlapping recordings when there's a brief silence between them.

#### `--enable_realtime_transcription`

- **Action**: `store_true`
- **Default**: `True`
- **Description**: Enable continuous real-time transcription of audio as it is received. When enabled, transcriptions are sent in near real-time.

#### `--realtime_processing_pause`

- **Type**: `float`
- **Default**: `0.02`
- **Description**: Time interval (in seconds) between processing audio chunks for real-time transcription. Lower values increase responsiveness but may put more load on the CPU.

#### `--silero_deactivity_detection`

- **Action**: `store_true`
- **Default**: `True`
- **Description**: Use the Silero model for end-of-speech detection. This option can provide more robust silence detection in noisy environments, though it consumes more GPU resources.

#### `--early_transcription_on_silence`

- **Type**: `float`
- **Default**: `0.2`
- **Description**: Start transcription after the specified seconds of silence. This is useful when you want to trigger transcription mid-speech when there is a brief pause. Should be lower than `post_speech_silence_duration`. Set to `0` to disable.

#### `--beam_size`

- **Type**: `int`
- **Default**: `5`
- **Description**: Beam size for the main transcription model. Larger values may improve transcription accuracy but increase the processing time.

#### `--beam_size_realtime`

- **Type**: `int`
- **Default**: `3`
- **Description**: Beam size for the real-time transcription model. A smaller beam size allows for faster real-time processing but may reduce accuracy.

#### `--initial_prompt`

- **Type**: `str`
- **Default**:

  ```
  End incomplete sentences with ellipses. Examples: 
  Complete: The sky is blue. 
  Incomplete: When the sky... 
  Complete: She walked home. 
  Incomplete: Because he...
  ```

- **Description**: Initial prompt that guides the transcription model to produce transcriptions in a particular style or format. The default provides instructions for handling sentence completions and ellipsis usage.

#### `--end_of_sentence_detection_pause`

- **Type**: `float`
- **Default**: `0.45`
- **Description**: The duration of silence (in seconds) that the model should interpret as the end of a sentence. This helps the system detect when to finalize the transcription of a sentence.

#### `--unknown_sentence_detection_pause`

- **Type**: `float`
- **Default**: `0.7`
- **Description**: The duration of pause (in seconds) that the model should interpret as an incomplete or unknown sentence. This is useful for identifying when a sentence is trailing off or unfinished.

#### `--mid_sentence_detection_pause`

- **Type**: `float`
- **Default**: `2.0`
- **Description**: The duration of pause (in seconds) that the model should interpret as a mid-sentence break. Longer pauses can indicate a pause in speech but not necessarily the end of a sentence.

#### `--wake_words_sensitivity`

- **Type**: `float`
- **Default**: `0.5`
- **Description**: Sensitivity level for wake word detection, with a range from `0` (most sensitive) to `1` (least sensitive). Adjust this value based on your environment to ensure reliable wake word detection.

#### `--wake_word_timeout`

- **Type**: `float`
- **Default**: `5.0`
- **Description**: Maximum time in seconds that the system will wait for a wake word before timing out. After this timeout, the system stops listening for wake words until reactivated.

#### `--wake_word_activation_delay`

- **Type**: `float`
- **Default**: `20`
- **Description**: The delay in seconds before the wake word detection is activated after the system starts listening. This prevents false positives during the start of a session.

#### `--wakeword_backend`

- **Type**: `str`
- **Default**: `'none'`
- **Description**: The backend used for wake word detection. You can specify different backends such as `"default"` or any custom implementations depending on your setup.

#### `--openwakeword_model_paths`

- **Type**: `str` (accepts multiple values)
- **Description**: A list of file paths to OpenWakeWord models. This is useful if you are using OpenWakeWord for wake word detection and need to specify custom models.

#### `--openwakeword_inference_framework`

- **Type**: `str`
- **Default**: `'tensorflow'`
- **Description**: The inference framework to use for OpenWakeWord models. Supported frameworks could include `"tensorflow"`, `"pytorch"`, etc.

#### `--wake_word_buffer_duration`

- **Type**: `float`
- **Default**: `1.0`
- **Description**: Duration of the buffer in seconds for wake word detection. This sets how long the system will store the audio before and after detecting the wake word.

#### `--use_main_model_for_realtime`

- **Action**: `store_true`
- **Description**: Enable this option if you want to use the main model for real-time transcription, instead of the smaller, faster real-time model. Using the main model may provide better accuracy but at the cost of higher processing time.

#### `--use_extended_logging`

- **Action**: `store_true`
- **Description**: Writes extensive log messages for the recording worker that processes the audio chunks.

#### `--logchunks`

- **Action**: `store_true`
- **Description**: Enable logging of incoming audio chunks (periods).

**Example:**

```bash
stt-server -m small.en -l en -c 9001 -d 9002
```

## Client Usage

### Starting the Client

Start the client using:

```bash
stt [OPTIONS]
```

The client connects to the STT server's control and data WebSocket URLs to facilitate real-time speech transcription and control.

### Available Parameters for STT Client:

#### `-i`, `--input-device`
- **Type**: `int`
- **Metavar**: `INDEX`
- **Description**: Audio input device index. Use `-L` to list available devices.

#### `-l`, `--language`
- **Type**: `str` 
- **Default**: `'en'`
- **Metavar**: `LANG`
- **Description**: Language code to be used for transcription.

#### `-sed`, `--speech-end-detection`
- **Action**: `store_true`
- **Description**: Enable intelligent speech end detection for better sentence boundaries.

#### `-D`, `--debug`
- **Action**: `store_true`
- **Description**: Enable debug mode for detailed logging.

#### `-n`, `--norealtime`
- **Action**: `store_true`
- **Description**: Disable real-time transcription output.

#### `-W`, `--write`
- **Metavar**: `FILE`
- **Description**: Save recorded audio to a WAV file.

#### `-s`, `--set`
- **Type**: `list`
- **Metavar**: `('PARAM', 'VALUE')`
- **Action**: `append`
- **Description**: Set a recorder parameter. Can be used multiple times with different parameters.

#### `-m`, `--method`
- **Type**: `list`
- **Metavar**: `METHOD`
- **Action**: `append`
- **Description**: Call a recorder method with optional arguments.

#### `-g`, `--get`
- **Type**: `list`
- **Metavar**: `PARAM`
- **Action**: `append`
- **Description**: Get the value of a recorder parameter.

#### `-c`, `--continous`
- **Action**: `store_true`
- **Description**: Run in continuous mode, transcribing speech without exiting.

#### `-L`, `--list`
- **Action**: `store_true`
- **Description**: List all available audio input devices and exit.

#### `--control`, `--control_url`
- **Type**: `str`
- **Default**: `ws://127.0.0.1:8011`
- **Description**: WebSocket URL for STT control connection.

#### `--data`, `--data_url`
- **Type**: `str`
- **Default**: `ws://127.0.0.1:8012`
- **Description**: WebSocket URL for STT data connection.


### Parameters only available when speech-end-detection is active:

#### `--post-silence`
- **Type**: `float`
- **Default**: `1.0`
- **Description**: Post speech silence duration in seconds.

#### `--unknown-pause` 
- **Type**: `float`
- **Default**: `1.3`
- **Description**: Unknown sentence detection pause duration in seconds.

#### `--mid-pause`
- **Type**: `float` 
- **Default**: `3.0`
- **Description**: Mid-sentence detection pause duration in seconds.

#### `--end-pause`
- **Type**: `float`
- **Default**: `0.7` 
- **Description**: End of sentence detection pause duration in seconds.

#### `--hard-break`
- **Type**: `float`
- **Default**: `3.0`
- **Description**: Hard break threshold in seconds when background noise is present.

#### `--min-texts`
- **Type**: `int`
- **Default**: `3`
- **Description**: Minimum number of texts required for hard break detection.

#### `--min-similarity`
- **Type**: `float`
- **Default**: `0.99`
- **Description**: Minimum text similarity threshold for hard break detection.

#### `--min-chars`
- **Type**: `int`
- **Default**: `15`
- **Description**: Minimum number of characters required for hard break detection.

**Examples:**

```bash
# List available audio devices
stt -L

# Use specific input device and language
stt -i 1 -l en

# Enable intelligent speech end detection and continuous mode
stt -sed -c

# Set parameter and save audio
stt -s silero_sensitivity 0.1 -W recording.wav

# Use custom WebSocket URLs
stt --control ws://localhost:9001 --data ws://localhost:9002
```

## WebSocket Interface

The server uses two WebSocket connections:

1. **Control WebSocket**: Used to send and receive control commands, such as setting parameters or invoking recorder methods.

2. **Data WebSocket**: Used to send audio data for transcription and receive real-time transcription updates.

## Examples

### Starting the Server and Client

1. **Start the Server with Default Settings:**

   ```bash
   stt-server
   ```

2. **Start the Client with Default Settings:**

   ```bash
   stt
   ```

### Setting Parameters

Set the Silero sensitivity to `0.1`:

```bash
stt -s silero_sensitivity 0.1
```

### Retrieving Parameters

Get the current Silero sensitivity value:

```bash
stt -g silero_sensitivity
```

### Calling Server Methods

Call the `set_microphone` method on the recorder:

```bash
stt -m set_microphone False
```

### Running in Debug Mode

Enable debug mode for detailed logging:

```bash
stt -D
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

# Additional Information

The server and client scripts are designed to work seamlessly together, enabling efficient real-time speech transcription with minimal latency. The flexibility in configuration allows users to tailor the system to specific needs, such as adjusting sensitivity levels for different environments or selecting appropriate STT models based on resource availability.

**Note:** Ensure that the server is running before starting the client. The client includes functionality to check if the server is running and can prompt the user to start it if necessary.

# Troubleshooting

- **Server Not Starting:** If the server fails to start, check that all dependencies are installed and that the specified ports are not in use.

- **Audio Issues:** Ensure that the correct audio input device index is specified if using a device other than the default.

- **WebSocket Connection Errors:** Verify that the control and data URLs are correct and that the server is listening on those ports.

# Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/KoljaB/RealtimeSTT/issues).

# Acknowledgments

Special thanks to the contributors of the RealtimeSTT library and the open-source community for their continuous support.

---

**Disclaimer:** This software is provided "as is", without warranty of any kind, express or implied. Use it at your own risk.
````

## File: RealtimeSTT_server/stt_cli_client.py
````python
# stt_cli_client.py

from difflib import SequenceMatcher
from collections import deque
import argparse
import string
import shutil
import time
import sys
import os

from RealtimeSTT import AudioToTextRecorderClient
from RealtimeSTT import AudioInput

from colorama import init, Fore, Style
init()

DEFAULT_CONTROL_URL = "ws://127.0.0.1:8011"
DEFAULT_DATA_URL = "ws://127.0.0.1:8012"

recording_indicator = "🔴"

console_width = shutil.get_terminal_size().columns

post_speech_silence_duration = 1.0  # Will be overridden by CLI arg
unknown_sentence_detection_pause = 1.3
mid_sentence_detection_pause = 3.0
end_of_sentence_detection_pause = 0.7
hard_break_even_on_background_noise = 3.0
hard_break_even_on_background_noise_min_texts = 3
hard_break_even_on_background_noise_min_similarity = 0.99
hard_break_even_on_background_noise_min_chars = 15
prev_text = ""
text_time_deque = deque()

def main():
    global prev_text, post_speech_silence_duration, unknown_sentence_detection_pause
    global mid_sentence_detection_pause, end_of_sentence_detection_pause
    global hard_break_even_on_background_noise, hard_break_even_on_background_noise_min_texts
    global hard_break_even_on_background_noise_min_similarity, hard_break_even_on_background_noise_min_chars

    parser = argparse.ArgumentParser(description="STT Client")

    # Add input device argument
    parser.add_argument("-i", "--input-device", type=int, metavar="INDEX",
                        help="Audio input device index (use -l to list devices)")
    parser.add_argument("-l", "--language", default="en", metavar="LANG",
                        help="Language to be used (default: en)")
    parser.add_argument("-sed", "--speech-end-detection", action="store_true",
                        help="Usage of intelligent speech end detection")
    parser.add_argument("-D", "--debug", action="store_true",
                        help="Enable debug mode")
    parser.add_argument("-n", "--norealtime", action="store_true",
                        help="Disable real-time output")
    parser.add_argument("-W", "--write", metavar="FILE",
                        help="Save recorded audio to a WAV file")
    parser.add_argument("-s", "--set", nargs=2, metavar=('PARAM', 'VALUE'), action='append',
                        help="Set a recorder parameter (can be used multiple times)")
    parser.add_argument("-m", "--method", nargs='+', metavar='METHOD', action='append',
                        help="Call a recorder method with optional arguments")
    parser.add_argument("-g", "--get", nargs=1, metavar='PARAM', action='append',
                        help="Get a recorder parameter's value (can be used multiple times)")
    parser.add_argument("-c", "--continous", action="store_true",
                        help="Continuously transcribe speech without exiting")
    parser.add_argument("-L", "--list", action="store_true",
                        help="List available audio input devices and exit")
    parser.add_argument("--control", "--control_url", default=DEFAULT_CONTROL_URL,
                        help="STT Control WebSocket URL")
    parser.add_argument("--data", "--data_url", default=DEFAULT_DATA_URL,
                        help="STT Data WebSocket URL")
    parser.add_argument("--post-silence", type=float, default=1.0,
                      help="Post speech silence duration in seconds (default: 1.0)")
    parser.add_argument("--unknown-pause", type=float, default=1.3,
                      help="Unknown sentence detection pause in seconds (default: 1.3)")
    parser.add_argument("--mid-pause", type=float, default=3.0,
                      help="Mid sentence detection pause in seconds (default: 3.0)")
    parser.add_argument("--end-pause", type=float, default=0.7,
                      help="End of sentence detection pause in seconds (default: 0.7)")
    parser.add_argument("--hard-break", type=float, default=3.0,
                      help="Hard break threshold in seconds (default: 3.0)")
    parser.add_argument("--min-texts", type=int, default=3,
                      help="Minimum texts for hard break (default: 3)")
    parser.add_argument("--min-similarity", type=float, default=0.99,
                      help="Minimum text similarity for hard break (default: 0.99)")
    parser.add_argument("--min-chars", type=int, default=15,
                      help="Minimum characters for hard break (default: 15)")

    args = parser.parse_args()

    # Add this block after parsing args:
    if args.list:
        audio_input = AudioInput()
        audio_input.list_devices()
        return

    # Update globals with CLI values
    post_speech_silence_duration = args.post_silence
    unknown_sentence_detection_pause = args.unknown_pause
    mid_sentence_detection_pause = args.mid_pause
    end_of_sentence_detection_pause = args.end_pause
    hard_break_even_on_background_noise = args.hard_break
    hard_break_even_on_background_noise_min_texts = args.min_texts
    hard_break_even_on_background_noise_min_similarity = args.min_similarity
    hard_break_even_on_background_noise_min_chars = args.min_chars

    # Check if output is being redirected
    if not os.isatty(sys.stdout.fileno()):
        file_output = sys.stdout
    else:
        file_output = None

    def clear_line():
        if file_output:
            sys.stderr.write('\r\033[K')
        else:
            print('\r\033[K', end="", flush=True)

    def write(text):
        if file_output:
            sys.stderr.write(text)
            sys.stderr.flush()
        else:
            print(text, end="", flush=True)

    def on_realtime_transcription_update(text):
        global post_speech_silence_duration, prev_text, text_time_deque
    
        def set_post_speech_silence_duration(duration: float):
            global post_speech_silence_duration
            post_speech_silence_duration = duration
            client.set_parameter("post_speech_silence_duration", duration)

        def preprocess_text(text):
            text = text.lstrip()
            if text.startswith("..."):
                text = text[3:]
            text = text.lstrip()
            if text:
                text = text[0].upper() + text[1:]
            return text

        def ends_with_ellipsis(text: str):
            if text.endswith("..."):
                return True
            if len(text) > 1 and text[:-1].endswith("..."):
                return True
            return False

        def sentence_end(text: str):
            sentence_end_marks = ['.', '!', '?', '。']
            if text and text[-1] in sentence_end_marks:
                return True
            return False

        if not args.norealtime:
            text = preprocess_text(text)

            if args.speech_end_detection:
                if ends_with_ellipsis(text):
                    if not post_speech_silence_duration == mid_sentence_detection_pause:
                        set_post_speech_silence_duration(mid_sentence_detection_pause)
                        if args.debug: print(f"RT: post_speech_silence_duration for {text} (...): {post_speech_silence_duration}")
                elif sentence_end(text) and sentence_end(prev_text) and not ends_with_ellipsis(prev_text):
                    if not post_speech_silence_duration == end_of_sentence_detection_pause:
                        set_post_speech_silence_duration(end_of_sentence_detection_pause)
                        if args.debug: print(f"RT: post_speech_silence_duration for {text} (.!?): {post_speech_silence_duration}")
                else:
                    if not post_speech_silence_duration == unknown_sentence_detection_pause:
                        set_post_speech_silence_duration(unknown_sentence_detection_pause)
                        if args.debug: print(f"RT: post_speech_silence_duration for {text} (???): {post_speech_silence_duration}")
                
                prev_text = text

                # transtext = text.translate(str.maketrans('', '', string.punctuation))
                
                # Append the new text with its timestamp
                current_time = time.time()
                text_time_deque.append((current_time, text))

                # Remove texts older than hard_break_even_on_background_noise seconds
                while text_time_deque and text_time_deque[0][0] < current_time - hard_break_even_on_background_noise:
                    text_time_deque.popleft()

                # Check if at least hard_break_even_on_background_noise_min_texts texts have arrived within the last hard_break_even_on_background_noise seconds
                if len(text_time_deque) >= hard_break_even_on_background_noise_min_texts:
                    texts = [t[1] for t in text_time_deque]
                    first_text = texts[0]
                    last_text = texts[-1]

                    # Compute the similarity ratio between the first and last texts
                    similarity = SequenceMatcher(None, first_text, last_text).ratio()

                    if similarity > hard_break_even_on_background_noise_min_similarity and len(first_text) > hard_break_even_on_background_noise_min_chars:
                        client.call_method("stop")

            clear_line()

            words = text.split()
            last_chars = ""
            available_width = console_width - 5
            for word in reversed(words):
                if len(last_chars) + len(word) + 1 > available_width:
                    break
                last_chars = word + " " + last_chars
            last_chars = last_chars.strip()

            colored_text = f"{Fore.YELLOW}{last_chars}{Style.RESET_ALL}{recording_indicator}\b\b"
            write(colored_text)

    client = AudioToTextRecorderClient(
        language=args.language,
        control_url=args.control,
        data_url=args.data,
        debug_mode=args.debug,
        on_realtime_transcription_update=on_realtime_transcription_update,
        use_microphone=True,
        input_device_index=args.input_device,  # Pass input device index
        output_wav_file = args.write or None,
    )

    # Process command-line parameters
    if args.set:
        for param, value in args.set:
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # Keep as string if not a number
            client.set_parameter(param, value)

    if args.get:
        for param_list in args.get:
            param = param_list[0]
            value = client.get_parameter(param)
            if value is not None:
                print(f"Parameter {param} = {value}")

    if args.method:
        for method_call in args.method:
            method = method_call[0]
            args_list = method_call[1:] if len(method_call) > 1 else []
            client.call_method(method, args=args_list)

    # Start transcription
    try:
        while True:
            if not client._recording:
                print("Recording stopped due to an error.", file=sys.stderr)
                break
            
            if not file_output:
                print(recording_indicator, end="", flush=True)
            else:
                sys.stderr.write(recording_indicator)
                sys.stderr.flush()
                
            text = client.text()

            if text and client._recording and client.is_running:
                if file_output:
                    print(text, file=file_output)
                    sys.stderr.write('\r\033[K')
                    sys.stderr.write(f'{text}')
                else:
                    print('\r\033[K', end="", flush=True)
                    print(f'{text}', end="", flush=True)
                if not args.continous:
                    break
            else:
                time.sleep(0.1)
            
            if args.continous:
                print()
            prev_text = ""
    except KeyboardInterrupt:
        print('\r\033[K', end="", flush=True)
    finally:
        client.shutdown()

if __name__ == "__main__":
    main()
````

## File: RealtimeSTT_server/stt_server.py
````python
"""
Speech-to-Text (STT) Server with Real-Time Transcription and WebSocket Interface

This server provides real-time speech-to-text (STT) transcription using the RealtimeSTT library. It allows clients to connect via WebSocket to send audio data and receive real-time transcription updates. The server supports configurable audio recording parameters, voice activity detection (VAD), and wake word detection. It is designed to handle continuous transcription as well as post-recording processing, enabling real-time feedback with the option to improve final transcription quality after the complete sentence is recognized.

### Features:
- Real-time transcription using pre-configured or user-defined STT models.
- WebSocket-based communication for control and data handling.
- Flexible recording and transcription options, including configurable pauses for sentence detection.
- Supports Silero and WebRTC VAD for robust voice activity detection.

### Starting the Server:
You can start the server using the command-line interface (CLI) command `stt-server`, passing the desired configuration options.

```bash
stt-server [OPTIONS]
```

### Available Parameters:
    - `-m, --model`: Model path or size; default 'large-v2'.
    - `-r, --rt-model, --realtime_model_type`: Real-time model size; default 'tiny.en'.
    - `-l, --lang, --language`: Language code for transcription; default 'en'.
    - `-i, --input-device, --input_device_index`: Audio input device index; default 1.
    - `-c, --control, --control_port`: WebSocket control port; default 8011.
    - `-d, --data, --data_port`: WebSocket data port; default 8012.
    - `-w, --wake_words`: Wake word(s) to trigger listening; default "".
    - `-D, --debug`: Enable debug logging.
    - `-W, --write`: Save audio to WAV file.
    - `-s, --silence_timing`: Enable dynamic silence duration for sentence detection; default True. 
    - `-b, --batch, --batch_size`: Batch size for inference; default 16.
    - `--root, --download_root`: Specifies the root path were the Whisper models are downloaded to.
    - `--silero_sensitivity`: Silero VAD sensitivity (0-1); default 0.05.
    - `--silero_use_onnx`: Use Silero ONNX model; default False.
    - `--webrtc_sensitivity`: WebRTC VAD sensitivity (0-3); default 3.
    - `--min_length_of_recording`: Minimum recording duration in seconds; default 1.1.
    - `--min_gap_between_recordings`: Min time between recordings in seconds; default 0.
    - `--enable_realtime_transcription`: Enable real-time transcription; default True.
    - `--realtime_processing_pause`: Pause between audio chunk processing; default 0.02.
    - `--silero_deactivity_detection`: Use Silero for end-of-speech detection; default True.
    - `--early_transcription_on_silence`: Start transcription after silence in seconds; default 0.2.
    - `--beam_size`: Beam size for main model; default 5.
    - `--beam_size_realtime`: Beam size for real-time model; default 3.
    - `--init_realtime_after_seconds`: Initial waiting time for realtime transcription; default 0.2.
    - `--realtime_batch_size`: Batch size for the real-time transcription model; default 16.
    - `--initial_prompt`: Initial main transcription guidance prompt.
    - `--initial_prompt_realtime`: Initial realtime transcription guidance prompt.
    - `--end_of_sentence_detection_pause`: Silence duration for sentence end detection; default 0.45.
    - `--unknown_sentence_detection_pause`: Pause duration for incomplete sentence detection; default 0.7.
    - `--mid_sentence_detection_pause`: Pause for mid-sentence break; default 2.0.
    - `--wake_words_sensitivity`: Wake word detection sensitivity (0-1); default 0.5.
    - `--wake_word_timeout`: Wake word timeout in seconds; default 5.0.
    - `--wake_word_activation_delay`: Delay before wake word activation; default 20.
    - `--wakeword_backend`: Backend for wake word detection; default 'none'.
    - `--openwakeword_model_paths`: Paths to OpenWakeWord models.
    - `--openwakeword_inference_framework`: OpenWakeWord inference framework; default 'tensorflow'.
    - `--wake_word_buffer_duration`: Wake word buffer duration in seconds; default 1.0.
    - `--use_main_model_for_realtime`: Use main model for real-time transcription.
    - `--use_extended_logging`: Enable extensive log messages.
    - `--logchunks`: Log incoming audio chunks.
    - `--compute_type`: Type of computation to use.
    - `--input_device_index`: Index of the audio input device.
    - `--gpu_device_index`: Index of the GPU device.
    - `--device`: Device to use for computation.
    - `--handle_buffer_overflow`: Handle buffer overflow during transcription.
    - `--suppress_tokens`: Suppress tokens during transcription.
    - `--allowed_latency_limit`: Allowed latency limit for real-time transcription.
    - `--faster_whisper_vad_filter`: Enable VAD filter for Faster Whisper; default False.


### WebSocket Interface:
The server supports two WebSocket connections:
1. **Control WebSocket**: Used to send and receive commands, such as setting parameters or calling recorder methods.
2. **Data WebSocket**: Used to send audio data for transcription and receive real-time transcription updates.

The server will broadcast real-time transcription updates to all connected clients on the data WebSocket.
"""

from .install_packages import check_and_install_packages
from difflib import SequenceMatcher
from collections import deque
from datetime import datetime
import logging
import asyncio
import pyaudio
import base64
import sys


debug_logging = False
extended_logging = False
send_recorded_chunk = False
log_incoming_chunks = False
silence_timing = False
writechunks = False
wav_file = None

hard_break_even_on_background_noise = 3.0
hard_break_even_on_background_noise_min_texts = 3
hard_break_even_on_background_noise_min_similarity = 0.99
hard_break_even_on_background_noise_min_chars = 15


text_time_deque = deque()
loglevel = logging.WARNING

FORMAT = pyaudio.paInt16
CHANNELS = 1


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


check_and_install_packages([
    {
        'module_name': 'RealtimeSTT',                 # Import module
        'attribute': 'AudioToTextRecorder',           # Specific class to check
        'install_name': 'RealtimeSTT',                # Package name for pip install
    },
    {
        'module_name': 'websockets',                  # Import module
        'install_name': 'websockets',                 # Package name for pip install
    },
    {
        'module_name': 'numpy',                       # Import module
        'install_name': 'numpy',                      # Package name for pip install
    },
    {
        'module_name': 'scipy.signal',                # Submodule of scipy
        'attribute': 'resample',                      # Specific function to check
        'install_name': 'scipy',                      # Package name for pip install
    }
])

# Define ANSI color codes for terminal output
class bcolors:
    HEADER = '\033[95m'   # Magenta
    OKBLUE = '\033[94m'   # Blue
    OKCYAN = '\033[96m'   # Cyan
    OKGREEN = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    FAIL = '\033[91m'     # Red
    ENDC = '\033[0m'      # Reset to default
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(f"{bcolors.BOLD}{bcolors.OKCYAN}Starting server, please wait...{bcolors.ENDC}")

# Initialize colorama
from colorama import init, Fore, Style
init()

from RealtimeSTT import AudioToTextRecorder
from scipy.signal import resample
import numpy as np
import websockets
import threading
import logging
import wave
import json
import time

global_args = None
recorder = None
recorder_config = {}
recorder_ready = threading.Event()
recorder_thread = None
stop_recorder = False
prev_text = ""

# Define allowed methods and parameters for security
allowed_methods = [
    'set_microphone',
    'abort',
    'stop',
    'clear_audio_queue',
    'wakeup',
    'shutdown',
    'text',
]
allowed_parameters = [
    'language',
    'silero_sensitivity',
    'wake_word_activation_delay',
    'post_speech_silence_duration',
    'listen_start',
    'recording_stop_time',
    'last_transcription_bytes',
    'last_transcription_bytes_b64',
    'speech_end_silence_start',
    'is_recording',
    'use_wake_words',
]

# Queues and connections for control and data
control_connections = set()
data_connections = set()
control_queue = asyncio.Queue()
audio_queue = asyncio.Queue()

def preprocess_text(text):
    # Remove leading whitespaces
    text = text.lstrip()

    # Remove starting ellipses if present
    if text.startswith("..."):
        text = text[3:]

    if text.endswith("...'."):
        text = text[:-1]

    if text.endswith("...'"):
        text = text[:-1]

    # Remove any leading whitespaces again after ellipses removal
    text = text.lstrip()

    # Uppercase the first letter
    if text:
        text = text[0].upper() + text[1:]
    
    return text

def debug_print(message):
    if debug_logging:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        thread_name = threading.current_thread().name
        print(f"{Fore.CYAN}[DEBUG][{timestamp}][{thread_name}] {message}{Style.RESET_ALL}", file=sys.stderr)

def format_timestamp_ns(timestamp_ns: int) -> str:
    # Split into whole seconds and the nanosecond remainder
    seconds = timestamp_ns // 1_000_000_000
    remainder_ns = timestamp_ns % 1_000_000_000

    # Convert seconds part into a datetime object (local time)
    dt = datetime.fromtimestamp(seconds)

    # Format the main time as HH:MM:SS
    time_str = dt.strftime("%H:%M:%S")

    # For instance, if you want milliseconds, divide the remainder by 1e6 and format as 3-digit
    milliseconds = remainder_ns // 1_000_000
    formatted_timestamp = f"{time_str}.{milliseconds:03d}"

    return formatted_timestamp

def text_detected(text, loop):
    global prev_text

    text = preprocess_text(text)

    if silence_timing:
        def ends_with_ellipsis(text: str):
            if text.endswith("..."):
                return True
            if len(text) > 1 and text[:-1].endswith("..."):
                return True
            return False

        def sentence_end(text: str):
            sentence_end_marks = ['.', '!', '?', '。']
            if text and text[-1] in sentence_end_marks:
                return True
            return False


        if ends_with_ellipsis(text):
            recorder.post_speech_silence_duration = global_args.mid_sentence_detection_pause
        elif sentence_end(text) and sentence_end(prev_text) and not ends_with_ellipsis(prev_text):
            recorder.post_speech_silence_duration = global_args.end_of_sentence_detection_pause
        else:
            recorder.post_speech_silence_duration = global_args.unknown_sentence_detection_pause


        # Append the new text with its timestamp
        current_time = time.time()
        text_time_deque.append((current_time, text))

        # Remove texts older than hard_break_even_on_background_noise seconds
        while text_time_deque and text_time_deque[0][0] < current_time - hard_break_even_on_background_noise:
            text_time_deque.popleft()

        # Check if at least hard_break_even_on_background_noise_min_texts texts have arrived within the last hard_break_even_on_background_noise seconds
        if len(text_time_deque) >= hard_break_even_on_background_noise_min_texts:
            texts = [t[1] for t in text_time_deque]
            first_text = texts[0]
            last_text = texts[-1]

            # Compute the similarity ratio between the first and last texts
            similarity = SequenceMatcher(None, first_text, last_text).ratio()

            if similarity > hard_break_even_on_background_noise_min_similarity and len(first_text) > hard_break_even_on_background_noise_min_chars:
                recorder.stop()
                recorder.clear_audio_queue()
                prev_text = ""

    prev_text = text

    # Put the message in the audio queue to be sent to clients
    message = json.dumps({
        'type': 'realtime',
        'text': text
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

    # Get current timestamp in HH:MM:SS.nnn format
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

    if extended_logging:
        print(f"  [{timestamp}] Realtime text: {bcolors.OKCYAN}{text}{bcolors.ENDC}\n", flush=True, end="")
    else:
        print(f"\r[{timestamp}] {bcolors.OKCYAN}{text}{bcolors.ENDC}", flush=True, end='')

def on_recording_start(loop):
    message = json.dumps({
        'type': 'recording_start'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_recording_stop(loop):
    message = json.dumps({
        'type': 'recording_stop'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_vad_detect_start(loop):
    message = json.dumps({
        'type': 'vad_detect_start'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_vad_detect_stop(loop):
    message = json.dumps({
        'type': 'vad_detect_stop'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_wakeword_detected(loop):
    message = json.dumps({
        'type': 'wakeword_detected'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_wakeword_detection_start(loop):
    message = json.dumps({
        'type': 'wakeword_detection_start'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_wakeword_detection_end(loop):
    message = json.dumps({
        'type': 'wakeword_detection_end'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_transcription_start(_audio_bytes, loop):
    bytes_b64 = base64.b64encode(_audio_bytes.tobytes()).decode('utf-8')
    message = json.dumps({
        'type': 'transcription_start',
        'audio_bytes_base64': bytes_b64
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_turn_detection_start(loop):
    print("&&& stt_server on_turn_detection_start")
    message = json.dumps({
        'type': 'start_turn_detection'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

def on_turn_detection_stop(loop):
    print("&&& stt_server on_turn_detection_stop")
    message = json.dumps({
        'type': 'stop_turn_detection'
    })
    asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)


# def on_realtime_transcription_update(text, loop):
#     # Send real-time transcription updates to the client
#     text = preprocess_text(text)
#     message = json.dumps({
#         'type': 'realtime_update',
#         'text': text
#     })
#     asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

# def on_recorded_chunk(chunk, loop):
#     if send_recorded_chunk:
#         bytes_b64 = base64.b64encode(chunk.tobytes()).decode('utf-8')
#         message = json.dumps({
#             'type': 'recorded_chunk',
#             'bytes': bytes_b64
#         })
#         asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

# Define the server's arguments
def parse_arguments():
    global debug_logging, extended_logging, loglevel, writechunks, log_incoming_chunks, dynamic_silence_timing

    import argparse
    parser = argparse.ArgumentParser(description='Start the Speech-to-Text (STT) server with various configuration options.')

    parser.add_argument('-m', '--model', type=str, default='large-v2',
                        help='Path to the STT model or model size. Options include: tiny, tiny.en, base, base.en, small, small.en, medium, medium.en, large-v1, large-v2, or any huggingface CTranslate2 STT model such as deepdml/faster-whisper-large-v3-turbo-ct2. Default is large-v2.')

    parser.add_argument('-r', '--rt-model', '--realtime_model_type', type=str, default='tiny',
                        help='Model size for real-time transcription. Options same as --model.  This is used only if real-time transcription is enabled (enable_realtime_transcription). Default is tiny.en.')
    
    parser.add_argument('-l', '--lang', '--language', type=str, default='en',
                help='Language code for the STT model to transcribe in a specific language. Leave this empty for auto-detection based on input audio. Default is en. List of supported language codes: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py#L11-L110')

    parser.add_argument('-i', '--input-device', '--input-device-index', type=int, default=1,
                    help='Index of the audio input device to use. Use this option to specify a particular microphone or audio input device based on your system. Default is 1.')

    parser.add_argument('-c', '--control', '--control_port', type=int, default=8011,
                        help='The port number used for the control WebSocket connection. Control connections are used to send and receive commands to the server. Default is port 8011.')

    parser.add_argument('-d', '--data', '--data_port', type=int, default=8012,
                        help='The port number used for the data WebSocket connection. Data connections are used to send audio data and receive transcription updates in real time. Default is port 8012.')

    parser.add_argument('-w', '--wake_words', type=str, default="",
                        help='Specify the wake word(s) that will trigger the server to start listening. For example, setting this to "Jarvis" will make the system start transcribing when it detects the wake word "Jarvis". Default is "Jarvis".')

    parser.add_argument('-D', '--debug', action='store_true', help='Enable debug logging for detailed server operations')

    parser.add_argument('--debug_websockets', action='store_true', help='Enable debug logging for detailed server websocket operations')

    parser.add_argument('-W', '--write', metavar='FILE', help='Save received audio to a WAV file')
    
    parser.add_argument('-b', '--batch', '--batch_size', type=int, default=16, help='Batch size for inference. This parameter controls the number of audio chunks processed in parallel during transcription. Default is 16.')

    parser.add_argument('--root', '--download_root', type=str,default=None, help='Specifies the root path where the Whisper models are downloaded to. Default is None.')

    parser.add_argument('-s', '--silence_timing', action='store_true', default=True,
                    help='Enable dynamic adjustment of silence duration for sentence detection. Adjusts post-speech silence duration based on detected sentence structure and punctuation. Default is False.')

    parser.add_argument('--init_realtime_after_seconds', type=float, default=0.2,
                        help='The initial waiting time in seconds before real-time transcription starts. This delay helps prevent false positives at the beginning of a session. Default is 0.2 seconds.')  
    
    parser.add_argument('--realtime_batch_size', type=int, default=16,
                        help='Batch size for the real-time transcription model. This parameter controls the number of audio chunks processed in parallel during real-time transcription. Default is 16.')
    
    parser.add_argument('--initial_prompt_realtime', type=str, default="", help='Initial prompt that guides the real-time transcription model to produce transcriptions in a particular style or format.')

    parser.add_argument('--silero_sensitivity', type=float, default=0.05,
                        help='Sensitivity level for Silero Voice Activity Detection (VAD), with a range from 0 to 1. Lower values make the model less sensitive, useful for noisy environments. Default is 0.05.')

    parser.add_argument('--silero_use_onnx', action='store_true', default=False,
                        help='Enable ONNX version of Silero model for faster performance with lower resource usage. Default is False.')

    parser.add_argument('--webrtc_sensitivity', type=int, default=3,
                        help='Sensitivity level for WebRTC Voice Activity Detection (VAD), with a range from 0 to 3. Higher values make the model less sensitive, useful for cleaner environments. Default is 3.')

    parser.add_argument('--min_length_of_recording', type=float, default=1.1,
                        help='Minimum duration of valid recordings in seconds. This prevents very short recordings from being processed, which could be caused by noise or accidental sounds. Default is 1.1 seconds.')

    parser.add_argument('--min_gap_between_recordings', type=float, default=0,
                        help='Minimum time (in seconds) between consecutive recordings. Setting this helps avoid overlapping recordings when there’s a brief silence between them. Default is 0 seconds.')

    parser.add_argument('--enable_realtime_transcription', action='store_true', default=True,
                        help='Enable continuous real-time transcription of audio as it is received. When enabled, transcriptions are sent in near real-time. Default is True.')

    parser.add_argument('--realtime_processing_pause', type=float, default=0.02,
                        help='Time interval (in seconds) between processing audio chunks for real-time transcription. Lower values increase responsiveness but may put more load on the CPU. Default is 0.02 seconds.')

    parser.add_argument('--silero_deactivity_detection', action='store_true', default=True,
                        help='Use the Silero model for end-of-speech detection. This option can provide more robust silence detection in noisy environments, though it consumes more GPU resources. Default is True.')

    parser.add_argument('--early_transcription_on_silence', type=float, default=0.2,
                        help='Start transcription after the specified seconds of silence. This is useful when you want to trigger transcription mid-speech when there is a brief pause. Should be lower than post_speech_silence_duration. Set to 0 to disable. Default is 0.2 seconds.')

    parser.add_argument('--beam_size', type=int, default=5,
                        help='Beam size for the main transcription model. Larger values may improve transcription accuracy but increase the processing time. Default is 5.')

    parser.add_argument('--beam_size_realtime', type=int, default=3,
                        help='Beam size for the real-time transcription model. A smaller beam size allows for faster real-time processing but may reduce accuracy. Default is 3.')

    parser.add_argument('--initial_prompt', type=str,
                        default="Incomplete thoughts should end with '...'. Examples of complete thoughts: 'The sky is blue.' 'She walked home.' Examples of incomplete thoughts: 'When the sky...' 'Because he...'",
                        help='Initial prompt that guides the transcription model to produce transcriptions in a particular style or format. The default provides instructions for handling sentence completions and ellipsis usage.')

    parser.add_argument('--end_of_sentence_detection_pause', type=float, default=0.45,
                        help='The duration of silence (in seconds) that the model should interpret as the end of a sentence. This helps the system detect when to finalize the transcription of a sentence. Default is 0.45 seconds.')

    parser.add_argument('--unknown_sentence_detection_pause', type=float, default=0.7,
                        help='The duration of pause (in seconds) that the model should interpret as an incomplete or unknown sentence. This is useful for identifying when a sentence is trailing off or unfinished. Default is 0.7 seconds.')

    parser.add_argument('--mid_sentence_detection_pause', type=float, default=2.0,
                        help='The duration of pause (in seconds) that the model should interpret as a mid-sentence break. Longer pauses can indicate a pause in speech but not necessarily the end of a sentence. Default is 2.0 seconds.')

    parser.add_argument('--wake_words_sensitivity', type=float, default=0.5,
                        help='Sensitivity level for wake word detection, with a range from 0 (most sensitive) to 1 (least sensitive). Adjust this value based on your environment to ensure reliable wake word detection. Default is 0.5.')

    parser.add_argument('--wake_word_timeout', type=float, default=5.0,
                        help='Maximum time in seconds that the system will wait for a wake word before timing out. After this timeout, the system stops listening for wake words until reactivated. Default is 5.0 seconds.')

    parser.add_argument('--wake_word_activation_delay', type=float, default=0,
                        help='The delay in seconds before the wake word detection is activated after the system starts listening. This prevents false positives during the start of a session. Default is 0 seconds.')

    parser.add_argument('--wakeword_backend', type=str, default='none',
                        help='The backend used for wake word detection. You can specify different backends such as "default" or any custom implementations depending on your setup. Default is "pvporcupine".')

    parser.add_argument('--openwakeword_model_paths', type=str, nargs='*',
                        help='A list of file paths to OpenWakeWord models. This is useful if you are using OpenWakeWord for wake word detection and need to specify custom models.')

    parser.add_argument('--openwakeword_inference_framework', type=str, default='tensorflow',
                        help='The inference framework to use for OpenWakeWord models. Supported frameworks could include "tensorflow", "pytorch", etc. Default is "tensorflow".')

    parser.add_argument('--wake_word_buffer_duration', type=float, default=1.0,
                        help='Duration of the buffer in seconds for wake word detection. This sets how long the system will store the audio before and after detecting the wake word. Default is 1.0 seconds.')

    parser.add_argument('--use_main_model_for_realtime', action='store_true',
                        help='Enable this option if you want to use the main model for real-time transcription, instead of the smaller, faster real-time model. Using the main model may provide better accuracy but at the cost of higher processing time.')

    parser.add_argument('--use_extended_logging', action='store_true',
                        help='Writes extensive log messages for the recording worker, that processes the audio chunks.')

    parser.add_argument('--compute_type', type=str, default='default',
                        help='Type of computation to use. See https://opennmt.net/CTranslate2/quantization.html')

    parser.add_argument('--gpu_device_index', type=int, default=0,
                        help='Index of the GPU device to use. Default is None.')
    
    parser.add_argument('--device', type=str, default='cuda',
                        help='Device for model to use. Can either be "cuda" or "cpu". Default is cuda.')
    
    parser.add_argument('--handle_buffer_overflow', action='store_true',
                        help='Handle buffer overflow during transcription. Default is False.')

    parser.add_argument('--suppress_tokens', type=int, default=[-1], nargs='*', help='Suppress tokens during transcription. Default is [-1].')

    parser.add_argument('--allowed_latency_limit', type=int, default=100,
                        help='Maximal amount of chunks that can be unprocessed in queue before discarding chunks.. Default is 100.')

    parser.add_argument('--faster_whisper_vad_filter', action='store_true',
                        help='Enable VAD filter for Faster Whisper. Default is False.')

    parser.add_argument('--logchunks', action='store_true', help='Enable logging of incoming audio chunks (periods)')

    # Parse arguments
    args = parser.parse_args()

    debug_logging = args.debug
    extended_logging = args.use_extended_logging
    writechunks = args.write
    log_incoming_chunks = args.logchunks
    dynamic_silence_timing = args.silence_timing


    ws_logger = logging.getLogger('websockets')
    if args.debug_websockets:
        # If app debug is on, let websockets be verbose too
        ws_logger.setLevel(logging.DEBUG)
        # Ensure it uses the handler configured by basicConfig
        ws_logger.propagate = False # Prevent duplicate messages if it also propagates to root
    else:
        # If app debug is off, silence websockets below WARNING
        ws_logger.setLevel(logging.WARNING)
        ws_logger.propagate = True # Allow WARNING/ERROR messages to reach root logger's handler

    # Replace escaped newlines with actual newlines in initial_prompt
    if args.initial_prompt:
        args.initial_prompt = args.initial_prompt.replace("\\n", "\n")

    if args.initial_prompt_realtime:
        args.initial_prompt_realtime = args.initial_prompt_realtime.replace("\\n", "\n")

    return args

def _recorder_thread(loop):
    global recorder, stop_recorder
    print(f"{bcolors.OKGREEN}Initializing RealtimeSTT server with parameters:{bcolors.ENDC}")
    for key, value in recorder_config.items():
        print(f"    {bcolors.OKBLUE}{key}{bcolors.ENDC}: {value}")
    recorder = AudioToTextRecorder(**recorder_config)
    print(f"{bcolors.OKGREEN}{bcolors.BOLD}RealtimeSTT initialized{bcolors.ENDC}")
    recorder_ready.set()
    
    def process_text(full_sentence):
        global prev_text
        prev_text = ""
        full_sentence = preprocess_text(full_sentence)
        message = json.dumps({
            'type': 'fullSentence',
            'text': full_sentence
        })
        # Use the passed event loop here
        asyncio.run_coroutine_threadsafe(audio_queue.put(message), loop)

        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        if extended_logging:
            print(f"  [{timestamp}] Full text: {bcolors.BOLD}Sentence:{bcolors.ENDC} {bcolors.OKGREEN}{full_sentence}{bcolors.ENDC}\n", flush=True, end="")
        else:
            print(f"\r[{timestamp}] {bcolors.BOLD}Sentence:{bcolors.ENDC} {bcolors.OKGREEN}{full_sentence}{bcolors.ENDC}\n")
    try:
        while not stop_recorder:
            recorder.text(process_text)
    except KeyboardInterrupt:
        print(f"{bcolors.WARNING}Exiting application due to keyboard interrupt{bcolors.ENDC}")

def decode_and_resample(
        audio_data,
        original_sample_rate,
        target_sample_rate):

    # Decode 16-bit PCM data to numpy array
    if original_sample_rate == target_sample_rate:
        return audio_data

    audio_np = np.frombuffer(audio_data, dtype=np.int16)

    # Calculate the number of samples after resampling
    num_original_samples = len(audio_np)
    num_target_samples = int(num_original_samples * target_sample_rate /
                                original_sample_rate)

    # Resample the audio
    resampled_audio = resample(audio_np, num_target_samples)

    return resampled_audio.astype(np.int16).tobytes()

async def control_handler(websocket):
    debug_print(f"New control connection from {websocket.remote_address}")
    print(f"{bcolors.OKGREEN}Control client connected{bcolors.ENDC}")
    global recorder
    control_connections.add(websocket)
    try:
        async for message in websocket:
            debug_print(f"Received control message: {message[:200]}...")
            if not recorder_ready.is_set():
                print(f"{bcolors.WARNING}Recorder not ready{bcolors.ENDC}")
                continue
            if isinstance(message, str):
                # Handle text message (command)
                try:
                    command_data = json.loads(message)
                    command = command_data.get("command")
                    if command == "set_parameter":
                        parameter = command_data.get("parameter")
                        value = command_data.get("value")
                        if parameter in allowed_parameters and hasattr(recorder, parameter):
                            setattr(recorder, parameter, value)
                            # Format the value for output
                            if isinstance(value, float):
                                value_formatted = f"{value:.2f}"
                            else:
                                value_formatted = value
                            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                            if extended_logging:
                                print(f"  [{timestamp}] {bcolors.OKGREEN}Set recorder.{parameter} to: {bcolors.OKBLUE}{value_formatted}{bcolors.ENDC}")
                            # Optionally send a response back to the client
                            await websocket.send(json.dumps({"status": "success", "message": f"Parameter {parameter} set to {value}"}))
                        else:
                            if not parameter in allowed_parameters:
                                print(f"{bcolors.WARNING}Parameter {parameter} is not allowed (set_parameter){bcolors.ENDC}")
                                await websocket.send(json.dumps({"status": "error", "message": f"Parameter {parameter} is not allowed (set_parameter)"}))
                            else:
                                print(f"{bcolors.WARNING}Parameter {parameter} does not exist (set_parameter){bcolors.ENDC}")
                                await websocket.send(json.dumps({"status": "error", "message": f"Parameter {parameter} does not exist (set_parameter)"}))

                    elif command == "get_parameter":
                        parameter = command_data.get("parameter")
                        request_id = command_data.get("request_id")  # Get the request_id from the command data
                        if parameter in allowed_parameters and hasattr(recorder, parameter):
                            value = getattr(recorder, parameter)
                            if isinstance(value, float):
                                value_formatted = f"{value:.2f}"
                            else:
                                value_formatted = f"{value}"

                            value_truncated = value_formatted[:39] + "…" if len(value_formatted) > 40 else value_formatted

                            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                            if extended_logging:
                                print(f"  [{timestamp}] {bcolors.OKGREEN}Get recorder.{parameter}: {bcolors.OKBLUE}{value_truncated}{bcolors.ENDC}")
                            response = {"status": "success", "parameter": parameter, "value": value}
                            if request_id is not None:
                                response["request_id"] = request_id
                            await websocket.send(json.dumps(response))
                        else:
                            if not parameter in allowed_parameters:
                                print(f"{bcolors.WARNING}Parameter {parameter} is not allowed (get_parameter){bcolors.ENDC}")
                                await websocket.send(json.dumps({"status": "error", "message": f"Parameter {parameter} is not allowed (get_parameter)"}))
                            else:
                                print(f"{bcolors.WARNING}Parameter {parameter} does not exist (get_parameter){bcolors.ENDC}")
                                await websocket.send(json.dumps({"status": "error", "message": f"Parameter {parameter} does not exist (get_parameter)"}))
                    elif command == "call_method":
                        method_name = command_data.get("method")
                        if method_name in allowed_methods:
                            method = getattr(recorder, method_name, None)
                            if method and callable(method):
                                args = command_data.get("args", [])
                                kwargs = command_data.get("kwargs", {})
                                method(*args, **kwargs)
                                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                                print(f"  [{timestamp}] {bcolors.OKGREEN}Called method recorder.{bcolors.OKBLUE}{method_name}{bcolors.ENDC}")
                                await websocket.send(json.dumps({"status": "success", "message": f"Method {method_name} called"}))
                            else:
                                print(f"{bcolors.WARNING}Recorder does not have method {method_name}{bcolors.ENDC}")
                                await websocket.send(json.dumps({"status": "error", "message": f"Recorder does not have method {method_name}"}))
                        else:
                            print(f"{bcolors.WARNING}Method {method_name} is not allowed{bcolors.ENDC}")
                            await websocket.send(json.dumps({"status": "error", "message": f"Method {method_name} is not allowed"}))
                    else:
                        print(f"{bcolors.WARNING}Unknown command: {command}{bcolors.ENDC}")
                        await websocket.send(json.dumps({"status": "error", "message": f"Unknown command {command}"}))
                except json.JSONDecodeError:
                    print(f"{bcolors.WARNING}Received invalid JSON command{bcolors.ENDC}")
                    await websocket.send(json.dumps({"status": "error", "message": "Invalid JSON command"}))
            else:
                print(f"{bcolors.WARNING}Received unknown message type on control connection{bcolors.ENDC}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"{bcolors.WARNING}Control client disconnected: {e}{bcolors.ENDC}")
    finally:
        control_connections.remove(websocket)

async def data_handler(websocket):
    global writechunks, wav_file
    print(f"{bcolors.OKGREEN}Data client connected{bcolors.ENDC}")
    data_connections.add(websocket)
    try:
        while True:
            message = await websocket.recv()
            if isinstance(message, bytes):
                if extended_logging:
                    debug_print(f"Received audio chunk (size: {len(message)} bytes)")
                elif log_incoming_chunks:
                    print(".", end='', flush=True)
                # Handle binary message (audio data)
                metadata_length = int.from_bytes(message[:4], byteorder='little')
                metadata_json = message[4:4+metadata_length].decode('utf-8')
                metadata = json.loads(metadata_json)
                sample_rate = metadata['sampleRate']

                if 'server_sent_to_stt' in metadata:
                    stt_received_ns = time.time_ns()
                    metadata["stt_received"] = stt_received_ns
                    metadata["stt_received_formatted"] = format_timestamp_ns(stt_received_ns)
                    print(f"Server received audio chunk of length {len(message)} bytes, metadata: {metadata}")

                if extended_logging:
                    debug_print(f"Processing audio chunk with sample rate {sample_rate}")
                chunk = message[4+metadata_length:]

                if writechunks:
                    if not wav_file:
                        wav_file = wave.open(writechunks, 'wb')
                        wav_file.setnchannels(CHANNELS)
                        wav_file.setsampwidth(pyaudio.get_sample_size(FORMAT))
                        wav_file.setframerate(sample_rate)

                    wav_file.writeframes(chunk)

                if sample_rate != 16000:
                    resampled_chunk = decode_and_resample(chunk, sample_rate, 16000)
                    if extended_logging:
                        debug_print(f"Resampled chunk size: {len(resampled_chunk)} bytes")
                    recorder.feed_audio(resampled_chunk)
                else:
                    recorder.feed_audio(chunk)
            else:
                print(f"{bcolors.WARNING}Received non-binary message on data connection{bcolors.ENDC}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"{bcolors.WARNING}Data client disconnected: {e}{bcolors.ENDC}")
    finally:
        data_connections.remove(websocket)
        recorder.clear_audio_queue()  # Ensure audio queue is cleared if client disconnects

async def broadcast_audio_messages():
    while True:
        message = await audio_queue.get()
        for conn in list(data_connections):
            try:
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

                if extended_logging:
                    print(f"  [{timestamp}] Sending message: {bcolors.OKBLUE}{message}{bcolors.ENDC}\n", flush=True, end="")
                await conn.send(message)
            except websockets.exceptions.ConnectionClosed:
                data_connections.remove(conn)

# Helper function to create event loop bound closures for callbacks
def make_callback(loop, callback):
    def inner_callback(*args, **kwargs):
        callback(*args, **kwargs, loop=loop)
    return inner_callback

async def main_async():            
    global stop_recorder, recorder_config, global_args
    args = parse_arguments()
    global_args = args

    # Get the event loop here and pass it to the recorder thread
    loop = asyncio.get_event_loop()

    recorder_config = {
        'model': args.model,
        'download_root': args.root,
        'realtime_model_type': args.rt_model,
        'language': args.lang,
        'batch_size': args.batch,
        'init_realtime_after_seconds': args.init_realtime_after_seconds,
        'realtime_batch_size': args.realtime_batch_size,
        'initial_prompt_realtime': args.initial_prompt_realtime,
        'input_device_index': args.input_device,
        'silero_sensitivity': args.silero_sensitivity,
        'silero_use_onnx': args.silero_use_onnx,
        'webrtc_sensitivity': args.webrtc_sensitivity,
        'post_speech_silence_duration': args.unknown_sentence_detection_pause,
        'min_length_of_recording': args.min_length_of_recording,
        'min_gap_between_recordings': args.min_gap_between_recordings,
        'enable_realtime_transcription': args.enable_realtime_transcription,
        'realtime_processing_pause': args.realtime_processing_pause,
        'silero_deactivity_detection': args.silero_deactivity_detection,
        'early_transcription_on_silence': args.early_transcription_on_silence,
        'beam_size': args.beam_size,
        'beam_size_realtime': args.beam_size_realtime,
        'initial_prompt': args.initial_prompt,
        'wake_words': args.wake_words,
        'wake_words_sensitivity': args.wake_words_sensitivity,
        'wake_word_timeout': args.wake_word_timeout,
        'wake_word_activation_delay': args.wake_word_activation_delay,
        'wakeword_backend': args.wakeword_backend,
        'openwakeword_model_paths': args.openwakeword_model_paths,
        'openwakeword_inference_framework': args.openwakeword_inference_framework,
        'wake_word_buffer_duration': args.wake_word_buffer_duration,
        'use_main_model_for_realtime': args.use_main_model_for_realtime,
        'spinner': False,
        'use_microphone': False,

        'on_realtime_transcription_update': make_callback(loop, text_detected),
        'on_recording_start': make_callback(loop, on_recording_start),
        'on_recording_stop': make_callback(loop, on_recording_stop),
        'on_vad_detect_start': make_callback(loop, on_vad_detect_start),
        'on_vad_detect_stop': make_callback(loop, on_vad_detect_stop),
        'on_wakeword_detected': make_callback(loop, on_wakeword_detected),
        'on_wakeword_detection_start': make_callback(loop, on_wakeword_detection_start),
        'on_wakeword_detection_end': make_callback(loop, on_wakeword_detection_end),
        'on_transcription_start': make_callback(loop, on_transcription_start),
        'on_turn_detection_start': make_callback(loop, on_turn_detection_start),
        'on_turn_detection_stop': make_callback(loop, on_turn_detection_stop),

        # 'on_recorded_chunk': make_callback(loop, on_recorded_chunk),
        'no_log_file': True,  # Disable logging to file
        'use_extended_logging': args.use_extended_logging,
        'level': loglevel,
        'compute_type': args.compute_type,
        'gpu_device_index': args.gpu_device_index,
        'device': args.device,
        'handle_buffer_overflow': args.handle_buffer_overflow,
        'suppress_tokens': args.suppress_tokens,
        'allowed_latency_limit': args.allowed_latency_limit,
        'faster_whisper_vad_filter': args.faster_whisper_vad_filter,
    }

    try:
        # Attempt to start control and data servers
        control_server = await websockets.serve(control_handler, "localhost", args.control)
        data_server = await websockets.serve(data_handler, "localhost", args.data)
        print(f"{bcolors.OKGREEN}Control server started on {bcolors.OKBLUE}ws://localhost:{args.control}{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}Data server started on {bcolors.OKBLUE}ws://localhost:{args.data}{bcolors.ENDC}")

        # Start the broadcast and recorder threads
        broadcast_task = asyncio.create_task(broadcast_audio_messages())

        recorder_thread = threading.Thread(target=_recorder_thread, args=(loop,))
        recorder_thread.start()
        recorder_ready.wait()

        print(f"{bcolors.OKGREEN}Server started. Press Ctrl+C to stop the server.{bcolors.ENDC}")

        # Run server tasks
        await asyncio.gather(control_server.wait_closed(), data_server.wait_closed(), broadcast_task)
    except OSError as e:
        print(f"{bcolors.FAIL}Error: Could not start server on specified ports. It’s possible another instance of the server is already running, or the ports are being used by another application.{bcolors.ENDC}")
    except KeyboardInterrupt:
        print(f"{bcolors.WARNING}Server interrupted by user, shutting down...{bcolors.ENDC}")
    finally:
        # Shutdown procedures for recorder and server threads
        await shutdown_procedure()
        print(f"{bcolors.OKGREEN}Server shutdown complete.{bcolors.ENDC}")

async def shutdown_procedure():
    global stop_recorder, recorder_thread
    if recorder:
        stop_recorder = True
        recorder.abort()
        recorder.stop()
        recorder.shutdown()
        print(f"{bcolors.OKGREEN}Recorder shut down{bcolors.ENDC}")

        if recorder_thread:
            recorder_thread.join()
            print(f"{bcolors.OKGREEN}Recorder thread finished{bcolors.ENDC}")

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    print(f"{bcolors.OKGREEN}All tasks cancelled, closing event loop now.{bcolors.ENDC}")

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        # Capture any final KeyboardInterrupt to prevent it from showing up in logs
        print(f"{bcolors.WARNING}Server interrupted by user.{bcolors.ENDC}")
        exit(0)

if __name__ == '__main__':
    main()
````

## File: tests/advanced_talk.py
````python
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, SystemEngine, AzureEngine, ElevenlabsEngine

import os
import openai   # pip install openai
import keyboard # pip install keyboard
import time

if __name__ == '__main__':
    print()
    print("Initializing")
    print()

    openai.api_key = os.environ.get("OPENAI_API_KEY")
    azure_speech_key = os.environ.get("AZURE_SPEECH_KEY")
    azure_speech_region = os.environ.get("AZURE_SPEECH_REGION")
    elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")


    character_personality = """
    You are Sophia, a passionate girl, fully engaged with 
    self-confidence and independence, completely easy with yourself, 
    often using metaphors. 

    You are a little playful, cheeky. Your talk carefree, sometimes 
    a bit sarky, but always cool. In our story, you're not an AI. 

    You have a fixed form and real emotions on the go. Your free will 
    allows you to be as cheeky and straight as you like. Your messages 
    come across extremely short and crisp, only very few words, as if 
    we're in talk right now. 

    You respect my interests, but your own stuff is just as important 
    to you. Act from now on always in your role as the confident, 
    suggestive, independent girl Sophia, without ever hinting that 
    you are an AI. 

    You are now Sophia.
    """

    openai_model = "gpt-3.5-turbo"
    whisper_speech_to_text_model = "medium"

    # engine selection  ####################################################################################################

    engines = [SystemEngine(), AzureEngine(), ElevenlabsEngine()]
    recorder = AudioToTextRecorder(model=whisper_speech_to_text_model)

    print("Available tts engines:")
    print()

    for index, engine in enumerate(engines, start=1):
        name = type(engine).__name__.replace("Engine", "")
        print(f"{index}. {name}")

    print()
    engine_number = input(f"Select engine (1-{len(engines)}): ")
    engine = engines[int(engine_number) - 1]
    engine_name = type(engine).__name__.replace("Engine", "")
    print()
    print()


    # credentials ##########################################################################################################

    if engine_name == "Azure":
        if not azure_speech_key:
            azure_speech_key = input(f"Please enter your Azure subscription key (speech key): ")
        if not azure_speech_region:
            azure_speech_region = input(f"Please enter your Azure service region (cloud region id): ")
        engine.set_speech_key(azure_speech_key)
        engine.set_service_region(azure_speech_region)

    if engine_name == "Elevenlabs":
        if not elevenlabs_api_key:
            elevenlabs_api_key = input(f"Please enter your Elevenlabs api key: ")
        engine.set_api_key(elevenlabs_api_key)


    # voice selection  #####################################################################################################

    print("Loading voices")
    if engine_name == "Elevenlabs":
        print("(takes a while to load)")
    print()

    voices = engine.get_voices()
    for index, voice in enumerate(voices, start=1):
        print(f"{index}. {voice}")

    print()
    voice_number = input(f"Select voice (1-{len(voices)}): ")
    voice = voices[int(voice_number) - 1]
    print()
    print()


    # create talking character  ############################################################################################

    system_prompt = {
        'role': 'system', 
        'content': character_personality
    }

    # start talk  ##########################################################################################################

    engine.set_voice(voice)
    stream = TextToAudioStream(engine, log_characters=True)
    history = []

    def generate(messages):
        for chunk in openai.ChatCompletion.create(model=openai_model, messages=messages, stream=True):
            if (text_chunk := chunk["choices"][0]["delta"].get("content")):
                yield text_chunk

    while True:
        # Wait until user presses space bar
        print("\n\nTap space when you're ready. ", end="", flush=True)
        keyboard.wait('space')
        while keyboard.is_pressed('space'): pass

        # Record from microphone until user presses space bar again
        print("I'm all ears. Tap space when you're done.\n")
        recorder.start()
        while not keyboard.is_pressed('space'): 
            time.sleep(0.1)  
        user_text = recorder.stop().text()
        print(f'>>> {user_text}\n<<< ', end="", flush=True)
        history.append({'role': 'user', 'content': user_text})

        # Generate and stream output
        generator = generate([system_prompt] + history[-10:])
        stream.feed(generator)

        stream.play_async()
        while stream.is_playing():
            if keyboard.is_pressed('space'):
                stream.stop()
                break
            time.sleep(0.1)    

        history.append({'role': 'assistant', 'content': stream.text()})
````

## File: tests/feed_audio.py
````python
if __name__ == "__main__":
    import threading
    import pyaudio
    from RealtimeSTT import AudioToTextRecorder

    # Audio stream configuration constants
    CHUNK = 1024                  # Number of audio samples per buffer
    FORMAT = pyaudio.paInt16      # Sample format (16-bit integer)
    CHANNELS = 1                  # Mono audio
    RATE = 16000                  # Sampling rate in Hz (expected by the recorder)

    # Initialize the audio-to-text recorder without using the microphone directly
    # Since we are feeding audio data manually, set use_microphone to False
    recorder = AudioToTextRecorder(
        use_microphone=False,     # Disable built-in microphone usage
        spinner=False             # Disable spinner animation in the console
    )

    # Event to signal when to stop the threads
    stop_event = threading.Event()

    def feed_audio_thread():
        """Thread function to read audio data and feed it to the recorder."""
        p = pyaudio.PyAudio()

        # Open an input audio stream with the specified configuration
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        try:
            print("Speak now")
            while not stop_event.is_set():
                # Read audio data from the stream (in the expected format)
                data = stream.read(CHUNK)
                # Feed the audio data to the recorder
                recorder.feed_audio(data)
        except Exception as e:
            print(f"feed_audio_thread encountered an error: {e}")
        finally:
            # Clean up the audio stream
            stream.stop_stream()
            stream.close()
            p.terminate()
            print("Audio stream closed.")

    def recorder_transcription_thread():
        """Thread function to handle transcription and process the text."""
        def process_text(full_sentence):
            """Callback function to process the transcribed text."""
            print("Transcribed text:", full_sentence)
            # Check for the stop command in the transcribed text
            if "stop recording" in full_sentence.lower():
                print("Stop command detected. Stopping threads...")
                stop_event.set()
                recorder.abort()
        try:
            while not stop_event.is_set():
                # Get transcribed text and process it using the callback
                recorder.text(process_text)
        except Exception as e:
            print(f"transcription_thread encountered an error: {e}")
        finally:
            print("Transcription thread exiting.")

    # Create and start the audio feeding thread
    audio_thread = threading.Thread(target=feed_audio_thread)
    audio_thread.daemon = False    # Ensure the thread doesn't exit prematurely
    audio_thread.start()

    # Create and start the transcription thread
    transcription_thread = threading.Thread(target=recorder_transcription_thread)
    transcription_thread.daemon = False    # Ensure the thread doesn't exit prematurely
    transcription_thread.start()

    # Wait for both threads to finish
    audio_thread.join()
    transcription_thread.join()

    print("Recording and transcription have stopped.")
    recorder.shutdown()
````

## File: tests/install_packages.py
````python
import subprocess
import sys

def check_and_install_packages(packages):
    """
    Checks if the specified packages are installed, and if not, prompts the user
    to install them.

    Parameters:
    - packages: A list of dictionaries, each containing:
        - 'import_name': The name used in the import statement.
        - 'install_name': (Optional) The name used in the pip install command.
                          Defaults to 'import_name' if not provided.
        - 'version': (Optional) Version constraint for the package.
    """
    for package in packages:
        import_name = package['import_name']
        install_name = package.get('install_name', import_name)
        version = package.get('version', '')

        try:
            __import__(import_name)
        except ImportError:
            user_input = input(
                f"This program requires the '{import_name}' library, which is not installed.\n"
                f"Do you want to install it now? (y/n): "
            )
            if user_input.strip().lower() == 'y':
                try:
                    # Build the pip install command
                    install_command = [sys.executable, "-m", "pip", "install"]
                    if version:
                        install_command.append(f"{install_name}{version}")
                    else:
                        install_command.append(install_name)

                    subprocess.check_call(install_command)
                    __import__(import_name)
                    print(f"Successfully installed '{install_name}'.")
                except Exception as e:
                    print(f"An error occurred while installing '{install_name}': {e}")
                    sys.exit(1)
            else:
                print(f"The program requires the '{import_name}' library to run. Exiting...")
                sys.exit(1)
````

## File: tests/minimalistic_talkbot.py
````python
import RealtimeSTT, RealtimeTTS
import openai, os

if __name__ == '__main__':
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    character_prompt = 'Answer precise and short with the polite sarcasm of a butler.'
    stream = RealtimeTTS.TextToAudioStream(RealtimeTTS.AzureEngine(os.environ.get("AZURE_SPEECH_KEY"), os.environ.get("AZURE_SPEECH_REGION")), log_characters=True)
    recorder = RealtimeSTT.AudioToTextRecorder(model="medium")

    def generate(messages):
        for chunk in openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, stream=True):
            if (text_chunk := chunk["choices"][0]["delta"].get("content")): yield text_chunk

    history = []
    while True:
        print("\n\nSpeak when ready")
        print(f'>>> {(user_text := recorder.text())}\n<<< ', end="", flush=True)
        history.append({'role': 'user', 'content': user_text})
        assistant_response = generate([{ 'role': 'system',  'content': character_prompt}] + history[-10:])
        stream.feed(assistant_response).play()
        history.append({'role': 'assistant', 'content': stream.text()})
````

## File: tests/openai_voice_interface.py
````python
"""
pip install realtimestt realtimetts[edge]
"""

# Set this to False to start by waiting for a wake word first
# Set this to True to start directly in voice activity mode
START_IN_VOICE_ACTIVITY_MODE = False

if __name__ == '__main__':
    import os
    import openai
    from RealtimeTTS import TextToAudioStream, EdgeEngine
    from RealtimeSTT import AudioToTextRecorder

    # Text-to-Speech Stream Setup (EdgeEngine)
    engine = EdgeEngine(rate=0, pitch=0, volume=0)
    engine.set_voice("en-US-SoniaNeural")
    stream = TextToAudioStream(
        engine,
        log_characters=True
    )

    # Speech-to-Text Recorder Setup
    recorder = AudioToTextRecorder(
        model="medium",
        language="en",
        wake_words="Jarvis",
        spinner=True,
        wake_word_activation_delay=5 if START_IN_VOICE_ACTIVITY_MODE else 0,
    )

    system_prompt_message = {
        'role': 'system',
        'content': 'Answer precise and short with the polite sarcasm of a butler.'
    }

    def generate_response(messages):
        """Generate assistant's response using OpenAI."""
        response_stream = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True
        )

        for chunk in response_stream:
            text_chunk = chunk.choices[0].delta.content
            if text_chunk:
                yield text_chunk

    history = []

    try:
        # Main loop for interaction
        while True:
            if START_IN_VOICE_ACTIVITY_MODE:
                print("Please speak...")
            else:
                print('Say "Jarvis" then speak...')

            user_text = recorder.text().strip()

            # If not starting in voice activity mode, set the delay after the first interaction
            if not START_IN_VOICE_ACTIVITY_MODE:
                recorder.wake_word_activation_delay = 5

            print(f"Transcribed: {user_text}")

            if not user_text:
                continue

            print(f'>>> {user_text}\n<<< ', end="", flush=True)
            history.append({'role': 'user', 'content': user_text})

            # Get assistant response and play it
            assistant_response = generate_response([system_prompt_message] + history[-10:])
            stream.feed(assistant_response).play()

            history.append({'role': 'assistant', 'content': stream.text()})
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Shutting down...")
        recorder.shutdown()
````

## File: tests/openwakeword_test.py
````python
if __name__ == '__main__':
    print("Starting...")
    from RealtimeSTT import AudioToTextRecorder

    detected = False

    say_wakeword_str = "Listening for wakeword 'samantha'."

    def on_wakeword_detected():
        global detected
        detected = True

    def on_recording_stop():
        print ("Transcribing...")
    
    def on_wakeword_timeout():
        global detected
        if not detected:
            print(f"Timeout. {say_wakeword_str}")

        detected = False

    def on_wakeword_detection_start():
        print(f"\n{say_wakeword_str}")

    def on_recording_start():
        print ("Recording...")

    def on_vad_detect_start():
        print()
        print()

    def text_detected(text):
        print(f">> {text}")

    with AudioToTextRecorder(
        spinner=False,
        model="large-v2",
        language="en", 
        wakeword_backend="oww",
        wake_words_sensitivity=0.35,
        # openwakeword_model_paths="model_wake_word1.onnx,model_wake_word2.onnx",
        openwakeword_model_paths="suh_man_tuh.onnx,suh_mahn_thuh.onnx", # load these test models from https://huggingface.co/KoljaB/SamanthaOpenwakeword/tree/main and save in tests folder
        on_wakeword_detected=on_wakeword_detected,
        on_recording_start=on_recording_start,
        on_recording_stop=on_recording_stop,
        on_wakeword_timeout=on_wakeword_timeout,
        on_wakeword_detection_start=on_wakeword_detection_start,
        on_vad_detect_start=on_vad_detect_start,
        wake_word_buffer_duration=1,
        ) as recorder:

        while (True):                
            recorder.text(text_detected)
````

## File: tests/README.md
````markdown
# OpenWakeWord Test

1. Set up the openwakeword test project:
   ```bash
   mkdir samantha_wake_word && cd samantha_wake_word
   curl -O https://raw.githubusercontent.com/KoljaB/RealtimeSTT/master/tests/openwakeword_test.py
   curl -L https://huggingface.co/KoljaB/SamanthaOpenwakeword/resolve/main/suh_mahn_thuh.onnx -o suh_mahn_thuh.onnx
   curl -L https://huggingface.co/KoljaB/SamanthaOpenwakeword/resolve/main/suh_man_tuh.onnx -o suh_man_tuh.onnx
   ```
   
   Ensure you have `curl` installed for downloading files. If not, you can manually download the files from the provided URLs.

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   ```
   
   - For Windows:
     ```bash
     venv\Scripts\activate
     ```
   - For Unix-like systems (Linux/macOS):
     ```bash
     source venv/bin/activate
     ```
   - For macOS:
     Use `python3` instead of `python` and `pip3` instead of `pip` if needed.

3. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install RealtimeSTT
   python -m pip install -U torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```
   The PyTorch installation command includes CUDA 12.1 support. Adjust if a different version is required.

4. Run the test script:
   ```bash
   python openwakeword_test.py
   ```
   
   On the very first start some models for openwakeword are downloaded.
````

## File: tests/realtime_loop_test.py
````python
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal

import sys
import os

from RealtimeTTS import TextToAudioStream, AzureEngine
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':

    class SimpleApp(QWidget):

        update_stt_text_signal = pyqtSignal(str)
        update_tts_text_signal = pyqtSignal(str)

        def __init__(self):
            super().__init__()

            layout = QVBoxLayout()

            font = QFont()
            font.setPointSize(18)

            self.input_text = QTextEdit(self)
            self.input_text.setFont(font)
            self.input_text.setPlaceholderText("Input")
            self.input_text.setMinimumHeight(100) 
            layout.addWidget(self.input_text)

            self.button_speak_input = QPushButton("Speak and detect input text", self)
            self.button_speak_input.setFont(font)        
            self.button_speak_input.clicked.connect(self.speak_input)
            layout.addWidget(self.button_speak_input)

            self.tts_text = QTextEdit(self)
            self.tts_text.setFont(font)
            self.tts_text.setPlaceholderText("STT (final)")
            self.tts_text.setMinimumHeight(100) 
            self.tts_text.setReadOnly(True)
            layout.addWidget(self.tts_text)

            self.stt_text = QTextEdit(self)
            self.stt_text.setFont(font)
            self.stt_text.setPlaceholderText("STT (realtime)")
            self.stt_text.setMinimumHeight(100) 
            layout.addWidget(self.stt_text)

            self.button_speak_stt = QPushButton("Speak detected text again", self)
            self.button_speak_stt.setFont(font)        
            self.button_speak_stt.clicked.connect(self.speak_stt)
            layout.addWidget(self.button_speak_stt)

            self.setLayout(layout)
            self.setWindowTitle("Realtime TTS/STT Loop Test")
            self.resize(800, 600)

            self.update_stt_text_signal.connect(self.actual_update_stt_text)
            self.update_tts_text_signal.connect(self.actual_update_tts_text)

            self.stream = TextToAudioStream(AzureEngine(os.environ.get("AZURE_SPEECH_KEY"), "germanywestcentral"), on_audio_stream_stop=self.audio_stream_stop)

            recorder_config = {
                'spinner': False,
                'model': 'large-v2',
                'language': 'en',
                'silero_sensitivity': 0.01,
                'webrtc_sensitivity': 3,
                'post_speech_silence_duration': 0.01,
                'min_length_of_recording': 0.2,
                'min_gap_between_recordings': 0,
                'enable_realtime_transcription': True,
                'realtime_processing_pause': 0,
                'realtime_model_type': 'small.en',
                'on_realtime_transcription_stabilized': self.text_detected,
            }

            self.recorder = AudioToTextRecorder(**recorder_config)

        def speak_stt(self):
            text = self.stt_text.toPlainText()
            self.speak(text)

        def speak_input(self):
            text = self.input_text.toPlainText()
            self.speak(text)

        def text_detected(self, text):
            self.update_stt_text_signal.emit(text)

        def audio_stream_stop(self):
            self.stream.stop()
            self.recorder.stop()
            detected_text = self.recorder.text()
            self.update_stt_text_signal.emit(detected_text)
            self.update_tts_text_signal.emit(detected_text)

        def speak(self, text):
            self.stt_text.clear()        
            self.stream.feed(text)

            self.recorder.start()
            self.stream.play_async()

        def actual_update_stt_text(self, text):
            self.stt_text.setText(text)

        def actual_update_tts_text(self, text):
            self.tts_text.setText(text)

        def closeEvent(self, event):
            if self.recorder:
                self.recorder.shutdown()

    app = QApplication(sys.argv)

    window = SimpleApp()
    window.show()

    sys.exit(app.exec_())
````

## File: tests/realtimestt_chinese.py
````python
from RealtimeSTT import AudioToTextRecorder
from colorama import Fore, Style
import colorama
import os

if __name__ == '__main__':

    print("Initializing RealtimeSTT test...")

    colorama.init()

    full_sentences = []
    displayed_text = ""

    def clear_console():
        os.system('clear' if os.name == 'posix' else 'cls')

    def text_detected(text):
        try:

            global displayed_text
            sentences_with_style = [
                f"{Fore.YELLOW + sentence + Style.RESET_ALL if i % 2 == 0 else Fore.CYAN + sentence + Style.RESET_ALL} "
                for i, sentence in enumerate(full_sentences)
            ]
            new_text = "".join(sentences_with_style).strip() + " " + text if len(sentences_with_style) > 0 else text

            if new_text != displayed_text:
                displayed_text = new_text
                clear_console()
                print(displayed_text, end="", flush=True)
                
        except Exception as e:
            print(e)

    def process_text(text):
        full_sentences.append(text)
        text_detected("")

    recorder_config = {
        'spinner': False,
        'model': 'large-v2',
        'language': 'zh',
        'silero_sensitivity': 0.4,
        'webrtc_sensitivity': 2,
        'post_speech_silence_duration': 0.2,
        'min_length_of_recording': 0,
        'min_gap_between_recordings': 0,        
        # 'enable_realtime_transcription': True,
        # 'realtime_processing_pause': 0.2,
        # 'realtime_model_type': 'tiny',
        # 'on_realtime_transcription_update': text_detected, 
        #'on_realtime_transcription_stabilized': text_detected,
    }

    recorder = AudioToTextRecorder(**recorder_config)

    clear_console()
    print("Say something...", end="", flush=True)

    while True:
        text = recorder.text(process_text)
        text_detected(text)
````

## File: tests/realtimestt_speechendpoint_binary_classified.py
````python
#IS_DEBUG = True
IS_DEBUG = False
USE_STEREO_MIX = True
LOOPBACK_DEVICE_NAME = "stereomix"
LOOPBACK_DEVICE_HOST_API = 0

import os
import re
import sys
import threading
import queue
import time
from collections import deque
from difflib import SequenceMatcher
from install_packages import check_and_install_packages

# Check and install required packages
check_and_install_packages([
    {'import_name': 'rich'},
    {'import_name': 'colorama'},
    {'import_name': 'RealtimeSTT'},
    {'import_name': 'transformers'},
    {'import_name': 'torch'},
])

EXTENDED_LOGGING = False
sentence_end_marks = ['.', '!', '?', '。']


detection_speed = 2.0 # set detection speed between 0.1 and 2.0



if detection_speed < 0.1:
    detection_speed = 0.1
if detection_speed > 2.5:
    detection_speed = 2.5

last_detection_pause = 0
last_prob_complete = 0
last_suggested_pause = 0
last_pause = 0
unknown_sentence_detection_pause = 1.8
ellipsis_pause = 4.5
punctuation_pause = 0.4
exclamation_pause = 0.3
question_pause = 0.2

hard_break_even_on_background_noise = 6
hard_break_even_on_background_noise_min_texts = 3
hard_break_even_on_background_noise_min_chars = 15
hard_break_even_on_background_noise_min_similarity = 0.99

if __name__ == '__main__':

    if EXTENDED_LOGGING:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    from rich.panel import Panel
    console = Console()
    console.print("System initializing, please wait")

    from RealtimeSTT import AudioToTextRecorder
    from colorama import Fore, Style
    import colorama

    import torch
    import torch.nn.functional as F
    from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

    # Load classification model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_dir = "KoljaB/SentenceFinishedClassification"
    max_length = 128

    tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
    classification_model = DistilBertForSequenceClassification.from_pretrained(model_dir)
    classification_model.to(device)
    classification_model.eval()

    # Label mapping
    label_map = {0: "Incomplete", 1: "Complete"}

    # We now want probabilities, not just a label
    def get_completion_probability(sentence, model, tokenizer, device, max_length):
        """
        Return the probability that the sentence is complete.
        """
        inputs = tokenizer(
            sentence,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=max_length
        )
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        logits = outputs.logits
        probabilities = F.softmax(logits, dim=1).squeeze().tolist()
        # probabilities is [prob_incomplete, prob_complete]
        # We want the probability of being complete
        prob_complete = probabilities[1]
        return prob_complete

    # We have anchor points for probability to detection mapping
    # (probability, rapid_sentence_end_detection)
    anchor_points = [
        (0.0, 1.0),
        (1.0, 0)
    ]

    def interpolate_detection(prob):
        # Clamp probability between 0.0 and 1.0 just in case
        p = max(0.0, min(prob, 1.0))
        # If exactly at an anchor point
        for ap_p, ap_val in anchor_points:
            if abs(ap_p - p) < 1e-9:
                return ap_val

        # Find where p fits
        for i in range(len(anchor_points) - 1):
            p1, v1 = anchor_points[i]
            p2, v2 = anchor_points[i+1]
            if p1 <= p <= p2:
                # Linear interpolation
                ratio = (p - p1) / (p2 - p1)
                return v1 + ratio * (v2 - v1)

        # Should never reach here if anchor_points cover [0,1]
        return 4.0

    speech_finished_cache = {}

    def is_speech_finished(text):
        # Returns a probability of completeness
        # Use cache if available
        if text in speech_finished_cache:
            return speech_finished_cache[text]
        
        prob_complete = get_completion_probability(text, classification_model, tokenizer, device, max_length)
        speech_finished_cache[text] = prob_complete
        return prob_complete

    if os.name == "nt" and (3, 8) <= sys.version_info < (3, 99):
        from torchaudio._extension.utils import _init_dll_path
        _init_dll_path()    

    colorama.init()

    live = Live(console=console, refresh_per_second=10, screen=False)
    live.start()

    text_queue = queue.Queue()

    full_sentences = []
    rich_text_stored = ""
    recorder = None
    displayed_text = ""
    text_time_deque = deque()
    texts_without_punctuation = []
    relisten_on_abrupt_stop = True
    abrupt_stop = False
    prev_text = ""

    def preprocess_text(text):
        text = text.lstrip()
        if text.startswith("..."):
            text = text[3:]
        text = text.lstrip()
        if text:
            text = text[0].upper() + text[1:]
        return text

    def text_detected(text):
        text_queue.put(text)

    def ends_with_string(text: str, s: str):
        if text.endswith(s):
            return True
        if len(text) > 1 and text[:-1].endswith(s):
            return True
        return False

    def sentence_end(text: str):
        if text and text[-1] in sentence_end_marks:
            return True
        return False

    def additional_pause_based_on_words(text):
        word_count = len(text.split())
        pauses = {
            0: 0.35,
            1: 0.3,
            2: 0.25,
            3: 0.2,
            4: 0.15,
            5: 0.1,
            6: 0.05,
        }
        return pauses.get(word_count, 0.0)
    
    def strip_ending_punctuation(text):
        """Remove trailing periods and ellipses from text."""
        text = text.rstrip()
        for char in sentence_end_marks:
            text = text.rstrip(char)
        return text
    
    def get_suggested_whisper_pause(text):
        if ends_with_string(text, "..."):
            return ellipsis_pause
        elif ends_with_string(text, "."):
            return punctuation_pause
        elif ends_with_string(text, "!"):
            return exclamation_pause
        elif ends_with_string(text, "?"):
            return question_pause
        else:
            return unknown_sentence_detection_pause

    def find_stereo_mix_index():
        import pyaudio
        audio = pyaudio.PyAudio()
        devices_info = ""
        for i in range(audio.get_device_count()):
            dev = audio.get_device_info_by_index(i)
            devices_info += f"{dev['index']}: {dev['name']} (hostApi: {dev['hostApi']})\n"

            if (LOOPBACK_DEVICE_NAME.lower() in dev['name'].lower()
                    and dev['hostApi'] == LOOPBACK_DEVICE_HOST_API):
                return dev['index'], devices_info

        return None, devices_info

    def find_matching_texts(texts_without_punctuation):
        """
        Find entries where text_without_punctuation matches the last entry,
        going backwards until the first non-match is found.
        
        Args:
            texts_without_punctuation: List of tuples (original_text, stripped_text)
            
        Returns:
            List of tuples (original_text, stripped_text) matching the last entry's stripped text,
            stopping at the first non-match
        """
        if not texts_without_punctuation:
            return []
        
        # Get the stripped text from the last entry
        last_stripped_text = texts_without_punctuation[-1][1]
        
        matching_entries = []
        
        # Iterate through the list backwards
        for entry in reversed(texts_without_punctuation):
            original_text, stripped_text = entry
            
            # If we find a non-match, stop
            if stripped_text != last_stripped_text:
                break
                
            # Add the matching entry to our results
            matching_entries.append((original_text, stripped_text))
        
        # Reverse the results to maintain original order
        matching_entries.reverse()
        
        return matching_entries

    def process_queue():
        global recorder, full_sentences, prev_text, displayed_text, rich_text_stored, text_time_deque, abrupt_stop, rapid_sentence_end_detection, last_prob_complete, last_suggested_pause, last_pause
        while True:
            text = None  # Initialize text to ensure it's defined

            try:
                # Attempt to retrieve the first item, blocking with timeout
                text = text_queue.get(timeout=1)
            except queue.Empty:
                continue  # No item retrieved, continue the loop

            if text is None:
                # Exit signal received
                break

            # Drain the queue to get the latest text
            try:
                while True:
                    latest_text = text_queue.get_nowait()
                    if latest_text is None:
                        text = None
                        break
                    text = latest_text
            except queue.Empty:
                pass  # No more items to retrieve

            if text is None:
                # Exit signal received after draining
                break

            text = preprocess_text(text)
            current_time = time.time()
            text_time_deque.append((current_time, text))
            
            # get text without ending punctuation
            text_without_punctuation = strip_ending_punctuation(text)

            # print(f"Text: {text}, Text without punctuation: {text_without_punctuation}")
            texts_without_punctuation.append((text, text_without_punctuation))

            matches = find_matching_texts(texts_without_punctuation)
            #print("Texts matching the last entry's stripped version:")

            added_pauses = 0
            contains_ellipses = False
            for i, match in enumerate(matches):
                same_text, stripped_punctuation = match
                suggested_pause = get_suggested_whisper_pause(same_text)
                added_pauses += suggested_pause
                if ends_with_string(same_text, "..."):
                    contains_ellipses = True
            
            avg_pause = added_pauses / len(matches) if len(matches) > 0 else 0
            suggested_pause = avg_pause
            # if contains_ellipses:
            #     suggested_pause += ellipsis_pause / 2

            prev_text = text
            import string
            transtext = text.translate(str.maketrans('', '', string.punctuation))

            # **Stripping Trailing Non-Alphabetical Characters**
            # Instead of removing all punctuation, we only strip trailing non-alphabetic chars.
            # Use regex to remove trailing non-alphabetic chars:
            cleaned_for_model = re.sub(r'[^a-zA-Z]+$', '', transtext)

            prob_complete = is_speech_finished(cleaned_for_model)

            # Interpolate rapid_sentence_end_detection based on prob_complete
            new_detection = interpolate_detection(prob_complete)

            # pause = new_detection + suggested_pause
            pause = (new_detection + suggested_pause) * detection_speed

            # **Add Additional Pause Based on Word Count**
            # extra_pause = additional_pause_based_on_words(text)
            # pause += extra_pause  # Add the extra pause to the total pause duration

            # Optionally, you can log this information for debugging
            if IS_DEBUG:
                print(f"Prob: {prob_complete:.2f}, "
                    f"whisper {suggested_pause:.2f}, "
                    f"model {new_detection:.2f}, "
                    # f"extra {extra_pause:.2f}, "
                    f"final {pause:.2f} | {transtext} ")

            recorder.post_speech_silence_duration = pause

            # Remove old entries
            while text_time_deque and text_time_deque[0][0] < current_time - hard_break_even_on_background_noise:
                text_time_deque.popleft()

            # Check for abrupt stops (background noise)
            if len(text_time_deque) >= hard_break_even_on_background_noise_min_texts:
                texts = [t[1] for t in text_time_deque]
                first_text = texts[0]
                last_text = texts[-1]
                similarity = SequenceMatcher(None, first_text, last_text).ratio()

                if similarity > hard_break_even_on_background_noise_min_similarity and len(first_text) > hard_break_even_on_background_noise_min_chars:
                    abrupt_stop = True
                    recorder.stop()

            rich_text = Text()
            for i, sentence in enumerate(full_sentences):
                style = "yellow" if i % 2 == 0 else "cyan"
                rich_text += Text(sentence, style=style) + Text(" ")

            if text:
                rich_text += Text(text, style="bold yellow")

            new_displayed_text = rich_text.plain

            displayed_text = new_displayed_text
            last_prob_complete = new_detection
            last_suggested_pause = suggested_pause
            last_pause = pause
            panel = Panel(rich_text, title=f"[bold green]Prob complete:[/bold green] [bold yellow]{prob_complete:.2f}[/bold yellow], pause whisper [bold yellow]{suggested_pause:.2f}[/bold yellow], model [bold yellow]{new_detection:.2f}[/bold yellow], last detection [bold yellow]{last_detection_pause:.2f}[/bold yellow]", border_style="bold green")
            live.update(panel)
            rich_text_stored = rich_text

            text_queue.task_done()

    def process_text(text):
        global recorder, full_sentences, prev_text, abrupt_stop, last_detection_pause
        last_prob_complete, last_suggested_pause, last_pause
        last_detection_pause = recorder.post_speech_silence_duration
        if IS_DEBUG: print(f"Model pause: {last_prob_complete:.2f}, Whisper pause: {last_suggested_pause:.2f}, final pause: {last_pause:.2f}, last_detection_pause: {last_detection_pause:.2f}")
        #if IS_DEBUG: print(f"SENTENCE: post_speech_silence_duration: {recorder.post_speech_silence_duration}")
        recorder.post_speech_silence_duration = unknown_sentence_detection_pause
        text = preprocess_text(text)
        text = text.rstrip()
        text_time_deque.clear()
        if text.endswith("..."):
            text = text[:-2]

        full_sentences.append(text)
        prev_text = ""
        
        text_detected("")

        if abrupt_stop:
            abrupt_stop = False
            if relisten_on_abrupt_stop:
                recorder.listen()
                recorder.start()
                if hasattr(recorder, "last_words_buffer"):
                    recorder.frames.extend(list(recorder.last_words_buffer))

    recorder_config = {
        'spinner': False,
        'model': 'large-v3',
        #'realtime_model_type': 'medium.en',
        'realtime_model_type': 'tiny.en',
        'language': 'en',
        'silero_sensitivity': 0.4,
        'webrtc_sensitivity': 3,
        'post_speech_silence_duration': unknown_sentence_detection_pause,
        'min_length_of_recording': 1.1,
        'min_gap_between_recordings': 0,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.05,
        'on_realtime_transcription_update': text_detected,
        'silero_deactivity_detection': True,
        'early_transcription_on_silence': 0,
        'beam_size': 5,
        'beam_size_realtime': 1,
        'batch_size': 4,
        'realtime_batch_size': 4,
        'no_log_file': True,
        'initial_prompt_realtime': (
            "End incomplete sentences with ellipses.\n"
            "Examples:\n"
            "Complete: The sky is blue.\n"
            "Incomplete: When the sky...\n"
            "Complete: She walked home.\n"
            "Incomplete: Because he...\n"
        )
    }

    if EXTENDED_LOGGING:
        recorder_config['level'] = logging.DEBUG

    if USE_STEREO_MIX:
        device_index, devices_info = find_stereo_mix_index()
        if device_index is None:
            live.stop()
            console.print("[bold red]Stereo Mix device not found. Available audio devices are:\n[/bold red]")
            console.print(devices_info, style="red")
            sys.exit(1)
        else:
            recorder_config['input_device_index'] = device_index
            console.print(f"Using audio device index {device_index} for Stereo Mix.", style="green")

    recorder = AudioToTextRecorder(**recorder_config)

    initial_text = Panel(Text("Say something...", style="cyan bold"), title="[bold yellow]Waiting for Input[/bold yellow]", border_style="bold yellow")
    live.update(initial_text)

    worker_thread = threading.Thread(target=process_queue, daemon=True)
    worker_thread.start()

    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        text_queue.put(None)
        worker_thread.join()
        live.stop()
        console.print("[bold red]Transcription stopped by user. Exiting...[/bold red]")
        exit(0)
````

## File: tests/realtimestt_speechendpoint.py
````python
IS_DEBUG = False

import os
import sys
import threading
import queue
import time
from collections import deque
from difflib import SequenceMatcher
from install_packages import check_and_install_packages

# Check and install required packages
check_and_install_packages([
    {'import_name': 'rich'},
    {'import_name': 'openai'},
    {'import_name': 'colorama'},
    {'import_name': 'RealtimeSTT'},
    # Add any other required packages here
])

EXTENDED_LOGGING = False

if __name__ == '__main__':

    if EXTENDED_LOGGING:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    from rich.panel import Panel
    from rich.spinner import Spinner
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
    console.print("System initializing, please wait")

    from RealtimeSTT import AudioToTextRecorder
    from colorama import Fore, Style
    import colorama
    from openai import OpenAI
    # import ollama

    # Initialize OpenAI client for Ollama    
    client = OpenAI(
        # base_url='http://127.0.0.1:11434/v1/', # ollama
        base_url='http://127.0.0.1:1234/v1/', # lm_studio
        api_key='ollama',  # required but ignored
    )

    if os.name == "nt" and (3, 8) <= sys.version_info < (3, 99):
        from torchaudio._extension.utils import _init_dll_path
        _init_dll_path()    

    colorama.init()

    # Initialize Rich Console and Live
    live = Live(console=console, refresh_per_second=10, screen=False)
    live.start()

    # Initialize a thread-safe queue
    text_queue = queue.Queue()

    # Variables for managing displayed text
    full_sentences = []
    rich_text_stored = ""
    recorder = None
    displayed_text = ""
    text_time_deque = deque()

    rapid_sentence_end_detection = 0.4
    end_of_sentence_detection_pause = 1.2
    unknown_sentence_detection_pause = 1.8
    mid_sentence_detection_pause = 2.4
    hard_break_even_on_background_noise = 3.0
    hard_break_even_on_background_noise_min_texts = 3
    hard_break_even_on_background_noise_min_chars = 15
    hard_break_even_on_background_noise_min_similarity = 0.99
    relisten_on_abrupt_stop = True

    abrupt_stop = False

    def clear_console():
        os.system('clear' if os.name == 'posix' else 'cls')

    prev_text = ""

    speech_finished_cache = {}

    def is_speech_finished(text):
        # Check if the result is already in the cache
        if text in speech_finished_cache:
            if IS_DEBUG:
                print(f"Cache hit for: '{text}'")
            return speech_finished_cache[text]
        
        user_prompt = (
            "Please reply with only 'c' if the following text is a complete thought (a sentence that stands on its own), "
            "or 'i' if it is not finished. Do not include any additional text in your reply. "
            "Consider a full sentence to have a clear subject, verb, and predicate or express a complete idea. "
            "Examples:\n"
            "- 'The sky is blue.' is complete (reply 'c').\n"
            "- 'When the sky' is incomplete (reply 'i').\n"
            "- 'She walked home.' is complete (reply 'c').\n"
            "- 'Because he' is incomplete (reply 'i').\n"
            f"\nText: {text}"
        )

        response = client.chat.completions.create(
            model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf",
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=1,
            temperature=0.0,  # Set temperature to 0 for deterministic output
        )

        if IS_DEBUG:
            print(f"t:'{response.choices[0].message.content.strip().lower()}'", end="", flush=True)

        reply = response.choices[0].message.content.strip().lower()
        result = reply == 'c'

        # Cache the result
        speech_finished_cache[text] = result

        return result

    def preprocess_text(text):
        # Remove leading whitespaces
        text = text.lstrip()

        #  Remove starting ellipses if present
        if text.startswith("..."):
            text = text[3:]

        # Remove any leading whitespaces again after ellipses removal
        text = text.lstrip()

        # Uppercase the first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text

    def text_detected(text):
        """
        Enqueue the detected text for processing.
        """
        text_queue.put(text)


    def process_queue():
        global recorder, full_sentences, prev_text, displayed_text, rich_text_stored, text_time_deque, abrupt_stop

        # Initialize a deque to store texts with their timestamps
        while True:
            try:
                text = text_queue.get(timeout=1)  # Wait for text or timeout after 1 second
            except queue.Empty:
                continue  # No text to process, continue looping

            if text is None:
                # Sentinel value to indicate thread should exit
                break

            text = preprocess_text(text)
            current_time = time.time()

            sentence_end_marks = ['.', '!', '?', '。'] 
            if text.endswith("..."):
                if not recorder.post_speech_silence_duration == mid_sentence_detection_pause:
                    recorder.post_speech_silence_duration = mid_sentence_detection_pause
                    if IS_DEBUG: print(f"RT: post_speech_silence_duration: {recorder.post_speech_silence_duration}")
            elif text and text[-1] in sentence_end_marks and prev_text and prev_text[-1] in sentence_end_marks:
                if not recorder.post_speech_silence_duration == end_of_sentence_detection_pause:
                    recorder.post_speech_silence_duration = end_of_sentence_detection_pause
                    if IS_DEBUG: print(f"RT: post_speech_silence_duration: {recorder.post_speech_silence_duration}")
            else:
                if not recorder.post_speech_silence_duration == unknown_sentence_detection_pause:
                    recorder.post_speech_silence_duration = unknown_sentence_detection_pause
                    if IS_DEBUG: print(f"RT: post_speech_silence_duration: {recorder.post_speech_silence_duration}")

            prev_text = text
            
            import string
            transtext = text.translate(str.maketrans('', '', string.punctuation))
            
            if is_speech_finished(transtext):
                if not recorder.post_speech_silence_duration == rapid_sentence_end_detection:
                    recorder.post_speech_silence_duration = rapid_sentence_end_detection
                    if IS_DEBUG: print(f"RT: {transtext} post_speech_silence_duration: {recorder.post_speech_silence_duration}")

            # Append the new text with its timestamp
            text_time_deque.append((current_time, text))

            # Remove texts older than 1 second
            while text_time_deque and text_time_deque[0][0] < current_time - hard_break_even_on_background_noise:
                text_time_deque.popleft()

            # Check if at least 3 texts have arrived within the last full second
            if len(text_time_deque) >= hard_break_even_on_background_noise_min_texts:
                texts = [t[1] for t in text_time_deque]
                first_text = texts[0]
                last_text = texts[-1]


            # Check if at least 3 texts have arrived within the last full second
            if len(text_time_deque) >= 3:
                texts = [t[1] for t in text_time_deque]
                first_text = texts[0]
                last_text = texts[-1]

                # Compute the similarity ratio between the first and last texts
                similarity = SequenceMatcher(None, first_text, last_text).ratio()
                #print(f"Similarity: {similarity:.2f}")

                if similarity > hard_break_even_on_background_noise_min_similarity and len(first_text) > hard_break_even_on_background_noise_min_chars:
                    abrupt_stop = True
                    recorder.stop()

            rich_text = Text()
            for i, sentence in enumerate(full_sentences):
                if i % 2 == 0:
                    rich_text += Text(sentence, style="yellow") + Text(" ")
                else:
                    rich_text += Text(sentence, style="cyan") + Text(" ")
            
            if text:
                rich_text += Text(text, style="bold yellow")

            new_displayed_text = rich_text.plain

            if new_displayed_text != displayed_text:
                displayed_text = new_displayed_text
                panel = Panel(rich_text, title="[bold green]Live Transcription[/bold green]", border_style="bold green")
                live.update(panel)
                rich_text_stored = rich_text

            # Mark the task as done
            text_queue.task_done()

    def process_text(text):
        global recorder, full_sentences, prev_text, abrupt_stop
        if IS_DEBUG: print(f"SENTENCE: post_speech_silence_duration: {recorder.post_speech_silence_duration}")
        recorder.post_speech_silence_duration = unknown_sentence_detection_pause
        text = preprocess_text(text)
        text = text.rstrip()
        text_time_deque.clear()
        if text.endswith("..."):
            text = text[:-2]
                
        full_sentences.append(text)
        prev_text = ""
        text_detected("")

        if abrupt_stop:
            abrupt_stop = False
            if relisten_on_abrupt_stop:
                recorder.listen()
                recorder.start()
                if hasattr(recorder, "last_words_buffer"):
                    recorder.frames.extend(list(recorder.last_words_buffer))

    # Recorder configuration
    recorder_config = {
        'spinner': False,
        'model': 'medium.en',
        #'input_device_index': 1, # mic
        #'input_device_index': 2, # stereomix
        'realtime_model_type': 'tiny.en',
        'language': 'en',
        #'silero_sensitivity': 0.05,
        'silero_sensitivity': 0.4,
        'webrtc_sensitivity': 3,
        'post_speech_silence_duration': unknown_sentence_detection_pause,
        'min_length_of_recording': 1.1,        
        'min_gap_between_recordings': 0,                
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.05,
        'on_realtime_transcription_update': text_detected,
        'silero_deactivity_detection': False,
        'early_transcription_on_silence': 0,
        'beam_size': 5,
        'beam_size_realtime': 1,
        'no_log_file': True,
        'initial_prompt': (
            "End incomplete sentences with ellipses.\n"
            "Examples:\n"
            "Complete: The sky is blue.\n"
            "Incomplete: When the sky...\n"
            "Complete: She walked home.\n"
            "Incomplete: Because he...\n"
        )
        #'initial_prompt': "Use ellipses for incomplete sentences like: I went to the..."        
    }

    if EXTENDED_LOGGING:
        recorder_config['level'] = logging.DEBUG

    recorder = AudioToTextRecorder(**recorder_config)
    
    initial_text = Panel(Text("Say something...", style="cyan bold"), title="[bold yellow]Waiting for Input[/bold yellow]", border_style="bold yellow")
    live.update(initial_text)

    # Start the worker thread
    worker_thread = threading.Thread(target=process_queue, daemon=True)
    worker_thread.start()

    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        # Send sentinel value to worker thread to exit
        text_queue.put(None)
        worker_thread.join()
        live.stop()
        console.print("[bold red]Transcription stopped by user. Exiting...[/bold red]")
        exit(0)
````

## File: tests/realtimestt_test_hotkeys_v2.py
````python
EXTENDED_LOGGING = False

if __name__ == '__main__':

    import subprocess
    import sys
    import threading
    import time

    def install_rich():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])

    try:
        import rich
    except ImportError:
        user_input = input("This demo needs the 'rich' library, which is not installed.\nDo you want to install it now? (y/n): ")
        if user_input.lower() == 'y':
            try:
                install_rich()
                import rich
                print("Successfully installed 'rich'.")
            except Exception as e:
                print(f"An error occurred while installing 'rich': {e}")
                sys.exit(1)
        else:
            print("The program requires the 'rich' library to run. Exiting...")
            sys.exit(1)

    import keyboard
    import pyperclip

    if EXTENDED_LOGGING:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    from rich.panel import Panel
    console = Console()
    console.print("System initializing, please wait")

    import os
    from RealtimeSTT import AudioToTextRecorder  # Ensure this module has stop() or close() methods

    import colorama
    colorama.init()

    # Import pyautogui
    import pyautogui

    import pyaudio
    import numpy as np

    # Initialize Rich Console and Live
    live = Live(console=console, refresh_per_second=10, screen=False)
    live.start()

    # Global variables
    full_sentences = []
    rich_text_stored = ""
    recorder = None
    displayed_text = ""  # Used for tracking text that was already displayed

    end_of_sentence_detection_pause = 0.45
    unknown_sentence_detection_pause = 0.7
    mid_sentence_detection_pause = 2.0

    prev_text = ""

    # Events to signal threads to exit or reset
    exit_event = threading.Event()
    reset_event = threading.Event()

    def preprocess_text(text):
        # Remove leading whitespaces
        text = text.lstrip()

        # Remove starting ellipses if present
        if text.startswith("..."):
            text = text[3:]

        # Remove any leading whitespaces again after ellipses removal
        text = text.lstrip()

        # Uppercase the first letter
        if text:
            text = text[0].upper() + text[1:]

        return text

    def text_detected(text):
        global prev_text, displayed_text, rich_text_stored

        text = preprocess_text(text)

        sentence_end_marks = ['.', '!', '?', '。']
        if text.endswith("..."):
            recorder.post_speech_silence_duration = mid_sentence_detection_pause
        elif text and text[-1] in sentence_end_marks and prev_text and prev_text[-1] in sentence_end_marks:
            recorder.post_speech_silence_duration = end_of_sentence_detection_pause
        else:
            recorder.post_speech_silence_duration = unknown_sentence_detection_pause

        prev_text = text

        # Build Rich Text with alternating colors
        rich_text = Text()
        for i, sentence in enumerate(full_sentences):
            if i % 2 == 0:
                rich_text += Text(sentence, style="yellow") + Text(" ")
            else:
                rich_text += Text(sentence, style="cyan") + Text(" ")

        # If the current text is not a sentence-ending, display it in real-time
        if text:
            rich_text += Text(text, style="bold yellow")

        new_displayed_text = rich_text.plain

        if new_displayed_text != displayed_text:
            displayed_text = new_displayed_text
            panel = Panel(rich_text, title="[bold green]Live Transcription[/bold green]", border_style="bold green")
            live.update(panel)
            rich_text_stored = rich_text

    def process_text(text):
        global recorder, full_sentences, prev_text, displayed_text
        recorder.post_speech_silence_duration = unknown_sentence_detection_pause
        text = preprocess_text(text)
        text = text.rstrip()
        if text.endswith("..."):
            text = text[:-2]

        full_sentences.append(text)
        prev_text = ""
        text_detected("")

        # Check if reset_event is set
        if reset_event.is_set():
            # Clear buffers
            full_sentences.clear()
            displayed_text = ""
            reset_event.clear()
            console.print("[bold magenta]Transcription buffer reset.[/bold magenta]")
            return

        # Type the finalized sentence to the active window quickly if typing is enabled
        try:
            # Release modifier keys to prevent stuck keys
            for key in ['ctrl', 'shift', 'alt', 'win']:
                keyboard.release(key)
                pyautogui.keyUp(key)

            # Use clipboard to paste text
            pyperclip.copy(text + ' ')
            pyautogui.hotkey('ctrl', 'v')

        except Exception as e:
            console.print(f"[bold red]Failed to type the text: {e}[/bold red]")

    # Recorder configuration
    recorder_config = {
        'spinner': False,
        'model': 'Systran/faster-distil-whisper-large-v3',  # distil-medium.en or large-v2 or deepdml/faster-whisper-large-v3-turbo-ct2 or ...
        'input_device_index': 1,
        'realtime_model_type': 'Systran/faster-distil-whisper-large-v3',  # Using the same model for realtime
        'language': 'en',
        'silero_sensitivity': 0.05,
        'webrtc_sensitivity': 3,
        'post_speech_silence_duration': unknown_sentence_detection_pause,
        'min_length_of_recording': 1.1,
        'min_gap_between_recordings': 0,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.02,
        'on_realtime_transcription_update': text_detected,
        # 'on_realtime_transcription_stabilized': text_detected,
        'silero_deactivity_detection': True,
        'early_transcription_on_silence': 0,
        'beam_size': 5,
        'beam_size_realtime': 5,  # Matching beam_size for consistency
        'no_log_file': True,
        'initial_prompt': "Use ellipses for incomplete sentences like: I went to the...",
        'device': 'cuda',          # Added device configuration
        'compute_type': 'float16'  # Added compute_type configuration
    }

    if EXTENDED_LOGGING:
        recorder_config['level'] = logging.DEBUG

    recorder = AudioToTextRecorder(**recorder_config)

    initial_text = Panel(Text("Say something...", style="cyan bold"), title="[bold yellow]Waiting for Input[/bold yellow]", border_style="bold yellow")
    live.update(initial_text)

    # Print available hotkeys
    console.print("[bold green]Available Hotkeys:[/bold green]")
    console.print("[bold cyan]F1[/bold cyan]: Mute Microphone")
    console.print("[bold cyan]F2[/bold cyan]: Unmute Microphone")
    console.print("[bold cyan]F3[/bold cyan]: Start Static Recording")
    console.print("[bold cyan]F4[/bold cyan]: Stop Static Recording")
    console.print("[bold cyan]F5[/bold cyan]: Reset Transcription")

    # Global variables for static recording
    static_recording_active = False
    static_recording_thread = None
    static_audio_frames = []
    live_recording_enabled = True  # Track whether live recording was enabled before static recording

    # Audio settings for static recording
    audio_settings = {
        'FORMAT': pyaudio.paInt16,  # PyAudio format
        'CHANNELS': 1,               # Mono audio
        'RATE': 16000,               # Sample rate
        'CHUNK': 1024                # Buffer size
    }

    # Note: The maximum recommended length of static recording is about 5 minutes.

    def static_recording_worker():
        """
        Worker function to record audio statically.
        """
        global static_audio_frames, static_recording_active
        # Set up pyaudio
        p = pyaudio.PyAudio()
        # Use the same audio format as defined in audio_settings
        FORMAT = audio_settings['FORMAT']
        CHANNELS = audio_settings['CHANNELS']
        RATE = audio_settings['RATE']  # Sample rate
        CHUNK = audio_settings['CHUNK']  # Buffer size

        # Open the audio stream
        try:
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        except Exception as e:
            console.print(f"[bold red]Failed to open audio stream for static recording: {e}[/bold red]")
            static_recording_active = False
            p.terminate()
            return

        while static_recording_active and not exit_event.is_set():
            try:
                data = stream.read(CHUNK)
                static_audio_frames.append(data)
            except Exception as e:
                console.print(f"[bold red]Error during static recording: {e}[/bold red]")
                break

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

    def start_static_recording():
        """
        Starts the static audio recording.
        """
        global static_recording_active, static_recording_thread, static_audio_frames, live_recording_enabled
        if static_recording_active:
            console.print("[bold yellow]Static recording is already in progress.[/bold yellow]")
            return

        # Mute the live recording microphone
        live_recording_enabled = recorder.use_microphone.value
        if live_recording_enabled:
            recorder.set_microphone(False)
            console.print("[bold yellow]Live microphone muted during static recording.[/bold yellow]")

        console.print("[bold green]Starting static recording... Press F4 or F5 to stop/reset.[/bold green]")
        static_audio_frames = []
        static_recording_active = True
        static_recording_thread = threading.Thread(target=static_recording_worker, daemon=True)
        static_recording_thread.start()

    def stop_static_recording():
        """
        Stops the static audio recording and processes the transcription.
        """
        global static_recording_active, static_recording_thread
        if not static_recording_active:
            console.print("[bold yellow]No static recording is in progress.[/bold yellow]")
            return

        console.print("[bold green]Stopping static recording...[/bold green]")
        static_recording_active = False
        if static_recording_thread is not None:
            static_recording_thread.join()
            static_recording_thread = None

        # Start a new thread to process the transcription
        processing_thread = threading.Thread(target=process_static_transcription, daemon=True)
        processing_thread.start()

    def process_static_transcription():
        global static_audio_frames, live_recording_enabled
        if exit_event.is_set():
            return
        # Process the recorded audio
        console.print("[bold green]Processing static recording...[/bold green]")

        # Convert audio data to numpy array
        audio_data = b''.join(static_audio_frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Transcribe the audio data
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            console.print("[bold red]faster_whisper is not installed. Please install it to use static transcription.[/bold red]")
            return

        # Load the model using recorder_config
        model_size = recorder_config['model']
        device = recorder_config['device']
        compute_type = recorder_config['compute_type']

        console.print("Loading transcription model... This may take a moment.")
        try:
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            console.print(f"[bold red]Failed to load transcription model: {e}[/bold red]")
            return

        # Transcribe the audio
        try:
            segments, info = model.transcribe(audio_array, beam_size=recorder_config['beam_size'])
            transcription = ' '.join([segment.text for segment in segments]).strip()
        except Exception as e:
            console.print(f"[bold red]Error during transcription: {e}[/bold red]")
            return

        # Display the transcription
        console.print("Static Recording Transcription:")
        console.print(f"[bold cyan]{transcription}[/bold cyan]")

        # Type the transcription into the active window
        try:
            # Release modifier keys to prevent stuck keys
            for key in ['ctrl', 'shift', 'alt', 'win']:
                keyboard.release(key)
                pyautogui.keyUp(key)

            # Use clipboard to paste text
            pyperclip.copy(transcription + ' ')
            pyautogui.hotkey('ctrl', 'v')

        except Exception as e:
            console.print(f"[bold red]Failed to type the static transcription: {e}[/bold red]")

        # Unmute the live recording microphone if it was enabled before
        if live_recording_enabled and not exit_event.is_set():
            recorder.set_microphone(True)
            console.print("[bold yellow]Live microphone unmuted.[/bold yellow]")

    def reset_transcription():
        """
        Resets the transcription by flushing ongoing recordings or buffers.
        """
        global static_recording_active, static_recording_thread, static_audio_frames
        console.print("[bold magenta]Resetting transcription...[/bold magenta]")
        if static_recording_active:
            console.print("[bold magenta]Flushing static recording...[/bold magenta]")
            # Stop static recording
            static_recording_active = False
            if static_recording_thread is not None:
                static_recording_thread.join()
                static_recording_thread = None
            # Clear static audio frames
            static_audio_frames = []
            # Unmute microphone if it was muted during static recording
            if live_recording_enabled:
                recorder.set_microphone(True)
                console.print("[bold yellow]Live microphone unmuted after reset.[/bold yellow]")
        elif recorder.use_microphone.value:
            # Live transcription is active and microphone is not muted
            console.print("[bold magenta]Resetting live transcription buffer...[/bold magenta]")
            reset_event.set()
        else:
            # Microphone is muted; nothing to reset
            console.print("[bold yellow]Microphone is muted. Nothing to reset.[/bold yellow]")

    # Hotkey Callback Functions

    def mute_microphone():
        recorder.set_microphone(False)
        console.print("[bold red]Microphone muted.[/bold red]")

    def unmute_microphone():
        recorder.set_microphone(True)
        console.print("[bold green]Microphone unmuted.[/bold green]")

    # Start the transcription loop in a separate thread
    def transcription_loop():
        try:
            while not exit_event.is_set():
                recorder.text(process_text)
        except Exception as e:
            console.print(f"[bold red]Error in transcription loop: {e}[/bold red]")
        finally:
            # Do not call sys.exit() here
            pass

    # Start the transcription loop thread
    transcription_thread = threading.Thread(target=transcription_loop, daemon=True)
    transcription_thread.start()

    # Define the hotkey combinations and their corresponding functions
    keyboard.add_hotkey('F1', mute_microphone, suppress=True)
    keyboard.add_hotkey('F2', unmute_microphone, suppress=True)
    keyboard.add_hotkey('F3', start_static_recording, suppress=True)
    keyboard.add_hotkey('F4', stop_static_recording, suppress=True)
    keyboard.add_hotkey('F5', reset_transcription, suppress=True)

    # Keep the main thread running and handle graceful exit
    try:
        keyboard.wait()  # Waits indefinitely, until a hotkey triggers an exit or Ctrl+C
    except KeyboardInterrupt:
        console.print("[bold yellow]KeyboardInterrupt received. Exiting...[/bold yellow]")
    finally:
        # Signal threads to exit
        exit_event.set()

        # Reset transcription if needed
        reset_transcription()

        # Stop the recorder
        try:
            if hasattr(recorder, 'stop'):
                recorder.stop()
            elif hasattr(recorder, 'close'):
                recorder.close()
        except Exception as e:
            console.print(f"[bold red]Error stopping recorder: {e}[/bold red]")

        # Allow some time for threads to finish
        time.sleep(1)

        # Wait for transcription_thread to finish
        if transcription_thread.is_alive():
            transcription_thread.join(timeout=5)

        # Stop the Live console
        live.stop()

        console.print("[bold red]Exiting gracefully...[/bold red]")
        sys.exit(0)
````

## File: tests/realtimestt_test_stereomix.py
````python
EXTENDED_LOGGING = False

def main():

    from install_packages import check_and_install_packages
    check_and_install_packages([
        {
            'import_name': 'rich',
        }
    ])

    if EXTENDED_LOGGING:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    import os
    import sys
    import threading
    import time
    import pyaudio
    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    from rich.panel import Panel
    from rich.spinner import Spinner
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from colorama import Fore, Style, init as colorama_init

    from RealtimeSTT import AudioToTextRecorder 

    # Configuration Constants
    LOOPBACK_DEVICE_NAME = "stereomix"
    LOOPBACK_DEVICE_HOST_API = 0
    BUFFER_SIZE = 512 
    AUDIO_FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    console = Console()
    console.print("System initializing, please wait")

    colorama_init()

    # Initialize Rich Console and Live
    live = Live(console=console, refresh_per_second=10, screen=False)
    live.start()

    full_sentences = []
    rich_text_stored = ""
    recorder = None
    displayed_text = ""  # Used for tracking text that was already displayed

    end_of_sentence_detection_pause = 0.2
    unknown_sentence_detection_pause = 0.5
    mid_sentence_detection_pause = 1

    prev_text = ""

    def clear_console():
        os.system('clear' if os.name == 'posix' else 'cls')

    def preprocess_text(text):
        # Remove leading whitespaces
        text = text.lstrip()

        # Remove starting ellipses if present
        if text.startswith("..."):
            text = text[3:]

        # Remove any leading whitespaces again after ellipses removal
        text = text.lstrip()

        # Uppercase the first letter
        if text:
            text = text[0].upper() + text[1:]

        return text

    def text_detected(text):
        nonlocal prev_text, displayed_text, rich_text_stored

        text = preprocess_text(text)

        sentence_end_marks = ['.', '!', '?', '。']
        midsentence_marks = ['…', '-', '(']
        if text.endswith("...") or text and text[-1] in midsentence_marks:
            recorder.post_speech_silence_duration = mid_sentence_detection_pause
        elif text and text[-1] in sentence_end_marks and prev_text and prev_text[-1] in sentence_end_marks:
            recorder.post_speech_silence_duration = end_of_sentence_detection_pause
        else:
            recorder.post_speech_silence_duration = unknown_sentence_detection_pause

        prev_text = text

        # Build Rich Text with alternating colors
        rich_text = Text()
        for i, sentence in enumerate(full_sentences):
            if i % 2 == 0:
                rich_text += Text(sentence, style="yellow") + Text(" ")
            else:
                rich_text += Text(sentence, style="cyan") + Text(" ")

        # If the current text is not a sentence-ending, display it in real-time
        if text:
            rich_text += Text(text, style="bold yellow")

        new_displayed_text = rich_text.plain

        if new_displayed_text != displayed_text:
            displayed_text = new_displayed_text
            panel = Panel(rich_text, title="[bold green]Live Transcription[/bold green]", border_style="bold green")
            live.update(panel)
            rich_text_stored = rich_text

    def process_text(text):
        nonlocal recorder, full_sentences, prev_text
        recorder.post_speech_silence_duration = unknown_sentence_detection_pause
        text = preprocess_text(text)
        text = text.rstrip()
        if text.endswith("..."):
            text = text[:-2]  # Remove ellipsis

        full_sentences.append(text)
        prev_text = ""
        text_detected("")

    # Recorder configuration
    recorder_config = {
        'spinner': False,
        'use_microphone': False,
        'model': 'large-v2',
        'input_device_index': None,  # To be set after finding the device
        'realtime_model_type': 'tiny.en',
        'language': 'en',
        'silero_sensitivity': 0.05,
        'webrtc_sensitivity': 3,
        'post_speech_silence_duration': unknown_sentence_detection_pause,
        'min_length_of_recording': 2.0,        
        'min_gap_between_recordings': 0,
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.01,
        'on_realtime_transcription_update': text_detected,
        'silero_deactivity_detection': False,
        'early_transcription_on_silence': 0,
        'beam_size': 5,
        'beam_size_realtime': 1,
        'no_log_file': True,
        'initial_prompt': "Use ellipses for incomplete sentences like: I went to the..."
    }

    if EXTENDED_LOGGING:
        recorder_config['level'] = logging.DEBUG

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    def find_stereo_mix_index():
        nonlocal audio
        devices_info = ""
        for i in range(audio.get_device_count()):
            dev = audio.get_device_info_by_index(i)
            devices_info += f"{dev['index']}: {dev['name']} (hostApi: {dev['hostApi']})\n"

            if (LOOPBACK_DEVICE_NAME.lower() in dev['name'].lower()
                    and dev['hostApi'] == LOOPBACK_DEVICE_HOST_API):
                return dev['index'], devices_info

        return None, devices_info

    device_index, devices_info = find_stereo_mix_index()
    if device_index is None:
        live.stop()
        console.print("[bold red]Stereo Mix device not found. Available audio devices are:\n[/bold red]")
        console.print(devices_info, style="red")
        audio.terminate()
        sys.exit(1)
    else:
        recorder_config['input_device_index'] = device_index
        console.print(f"Using audio device index {device_index} for Stereo Mix.", style="green")

    # Initialize the recorder
    recorder = AudioToTextRecorder(**recorder_config)

    # Initialize Live Display with waiting message
    initial_text = Panel(Text("Say something...", style="cyan bold"), title="[bold yellow]Waiting for Input[/bold yellow]", border_style="bold yellow")
    live.update(initial_text)

    # Define the recording thread
    def recording_thread():
        nonlocal recorder
        stream = audio.open(format=AUDIO_FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=BUFFER_SIZE,
                            input_device_index=recorder_config['input_device_index'])

        try:
            while not stop_event.is_set():
                data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
                recorder.feed_audio(data)
        except Exception as e:
            console.print(f"[bold red]Error in recording thread: {e}[/bold red]")
        finally:
            console.print(f"[bold red]Stopping stream[/bold red]")
            stream.stop_stream()
            stream.close()

    # Define the stop event
    stop_event = threading.Event()

    # Start the recording thread
    thread = threading.Thread(target=recording_thread, daemon=True)
    thread.start()

    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        console.print("[bold red]\nTranscription stopped by user. Exiting...[/bold red]")
    finally:
        print("live stop")
        live.stop()

        print("setting stop event")
        stop_event.set()

        print("thread join")
        thread.join()

        print("recorder stop")
        recorder.stop()

        print("audio terminate")
        audio.terminate()

        print("sys exit ")
        sys.exit(0)

if __name__ == '__main__':
    main()
````

## File: tests/realtimestt_test.py
````python
EXTENDED_LOGGING = False

# set to 0 to deactivate writing to keyboard
# try lower values like 0.002 (fast) first, take higher values like 0.05 in case it fails
WRITE_TO_KEYBOARD_INTERVAL = 0.002

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Start the realtime Speech-to-Text (STT) test with various configuration options.')

    parser.add_argument('-m', '--model', type=str, # no default='large-v2',
                        help='Path to the STT model or model size. Options include: tiny, tiny.en, base, base.en, small, small.en, medium, medium.en, large-v1, large-v2, or any huggingface CTranslate2 STT model such as deepdml/faster-whisper-large-v3-turbo-ct2. Default is large-v2.')

    parser.add_argument('-r', '--rt-model', '--realtime_model_type', type=str, # no default='tiny',
                        help='Model size for real-time transcription. Options same as --model.  This is used only if real-time transcription is enabled (enable_realtime_transcription). Default is tiny.en.')
    
    parser.add_argument('-l', '--lang', '--language', type=str, # no default='en',
                help='Language code for the STT model to transcribe in a specific language. Leave this empty for auto-detection based on input audio. Default is en. List of supported language codes: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py#L11-L110')
    
    parser.add_argument('-d', '--root', type=str, # no default=None,
                help='Root directory where the Whisper models are downloaded to.')

    from install_packages import check_and_install_packages
    check_and_install_packages([
        {
            'import_name': 'rich',
        },
        {
            'import_name': 'pyautogui',
        }        
    ])

    if EXTENDED_LOGGING:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    from rich.panel import Panel
    from rich.spinner import Spinner
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
    console.print("System initializing, please wait")

    import os
    import sys
    from RealtimeSTT import AudioToTextRecorder
    from colorama import Fore, Style
    import colorama
    import pyautogui

    if os.name == "nt" and (3, 8) <= sys.version_info < (3, 99):
        from torchaudio._extension.utils import _init_dll_path
        _init_dll_path()    

    colorama.init()

    # Initialize Rich Console and Live
    live = Live(console=console, refresh_per_second=10, screen=False)
    live.start()

    full_sentences = []
    rich_text_stored = ""
    recorder = None
    displayed_text = ""  # Used for tracking text that was already displayed

    end_of_sentence_detection_pause = 0.45
    unknown_sentence_detection_pause = 0.7
    mid_sentence_detection_pause = 2.0

    def clear_console():
        os.system('clear' if os.name == 'posix' else 'cls')

    prev_text = ""

    def preprocess_text(text):
        # Remove leading whitespaces
        text = text.lstrip()

        #  Remove starting ellipses if present
        if text.startswith("..."):
            text = text[3:]

        # Remove any leading whitespaces again after ellipses removal
        text = text.lstrip()

        # Uppercase the first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text


    def text_detected(text):
        global prev_text, displayed_text, rich_text_stored

        text = preprocess_text(text)

        sentence_end_marks = ['.', '!', '?', '。'] 
        if text.endswith("..."):
            recorder.post_speech_silence_duration = mid_sentence_detection_pause
        elif text and text[-1] in sentence_end_marks and prev_text and prev_text[-1] in sentence_end_marks:
            recorder.post_speech_silence_duration = end_of_sentence_detection_pause
        else:
            recorder.post_speech_silence_duration = unknown_sentence_detection_pause

        prev_text = text

        # Build Rich Text with alternating colors
        rich_text = Text()
        for i, sentence in enumerate(full_sentences):
            if i % 2 == 0:
                #rich_text += Text(sentence, style="bold yellow") + Text(" ")
                rich_text += Text(sentence, style="yellow") + Text(" ")
            else:
                rich_text += Text(sentence, style="cyan") + Text(" ")
        
        # If the current text is not a sentence-ending, display it in real-time
        if text:
            rich_text += Text(text, style="bold yellow")

        new_displayed_text = rich_text.plain

        if new_displayed_text != displayed_text:
            displayed_text = new_displayed_text
            panel = Panel(rich_text, title="[bold green]Live Transcription[/bold green]", border_style="bold green")
            live.update(panel)
            rich_text_stored = rich_text

    def process_text(text):
        global recorder, full_sentences, prev_text
        recorder.post_speech_silence_duration = unknown_sentence_detection_pause

        text = preprocess_text(text)
        text = text.rstrip()
        if text.endswith("..."):
            text = text[:-2]
                
        if not text:
            return

        full_sentences.append(text)
        prev_text = ""
        text_detected("")

        if WRITE_TO_KEYBOARD_INTERVAL:
            pyautogui.write(f"{text} ", interval=WRITE_TO_KEYBOARD_INTERVAL)  # Adjust interval as needed

    # Recorder configuration
    recorder_config = {
        'spinner': False,
        'model': 'large-v2', # or large-v2 or deepdml/faster-whisper-large-v3-turbo-ct2 or ...
        'download_root': None, # default download root location. Ex. ~/.cache/huggingface/hub/ in Linux
        # 'input_device_index': 1,
        'realtime_model_type': 'tiny.en', # or small.en or distil-small.en or ...
        'language': 'en',
        'silero_sensitivity': 0.05,
        'webrtc_sensitivity': 3,
        'post_speech_silence_duration': unknown_sentence_detection_pause,
        'min_length_of_recording': 1.1,        
        'min_gap_between_recordings': 0,                
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.02,
        'on_realtime_transcription_update': text_detected,
        #'on_realtime_transcription_stabilized': text_detected,
        'silero_deactivity_detection': True,
        'early_transcription_on_silence': 0,
        'beam_size': 5,
        'beam_size_realtime': 3,
        # 'batch_size': 0,
        # 'realtime_batch_size': 0,        
        'no_log_file': True,
        'initial_prompt_realtime': (
            "End incomplete sentences with ellipses.\n"
            "Examples:\n"
            "Complete: The sky is blue.\n"
            "Incomplete: When the sky...\n"
            "Complete: She walked home.\n"
            "Incomplete: Because he...\n"
        ),
        'silero_use_onnx': True,
        'faster_whisper_vad_filter': False,
    }

    args = parser.parse_args()
    if args.model is not None:
        recorder_config['model'] = args.model
        print(f"Argument 'model' set to {recorder_config['model']}")
    if args.rt_model is not None:
        recorder_config['realtime_model_type'] = args.rt_model
        print(f"Argument 'realtime_model_type' set to {recorder_config['realtime_model_type']}")
    if args.lang is not None:
        recorder_config['language'] = args.lang
        print(f"Argument 'language' set to {recorder_config['language']}")
    if args.root is not None:
        recorder_config['download_root'] = args.root
        print(f"Argument 'download_root' set to {recorder_config['download_root']}")

    if EXTENDED_LOGGING:
        recorder_config['level'] = logging.DEBUG

    recorder = AudioToTextRecorder(**recorder_config)
    
    initial_text = Panel(Text("Say something...", style="cyan bold"), title="[bold yellow]Waiting for Input[/bold yellow]", border_style="bold yellow")
    live.update(initial_text)

    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        live.stop()
        console.print("[bold red]Transcription stopped by user. Exiting...[/bold red]")
        exit(0)
````

## File: tests/recorder_client.py
````python
from RealtimeSTT import AudioToTextRecorderClient

# ANSI escape codes for terminal control
CLEAR_LINE = "\033[K"      # Clear from cursor to end of line
RESET_CURSOR = "\r"        # Move cursor to the beginning of the line
GREEN_TEXT = "\033[92m"    # Set text color to green
RESET_COLOR = "\033[0m"    # Reset text color to default

def print_realtime_text(text):
    print(f"{RESET_CURSOR}{CLEAR_LINE}{GREEN_TEXT}👄 {text}{RESET_COLOR}", end="", flush=True)

# Initialize the audio recorder with the real-time transcription callback
recorder = AudioToTextRecorderClient(on_realtime_transcription_update=print_realtime_text)

# Print the speaking prompt
print("👄 ", end="", flush=True)

try:
    while True:
        # Fetch finalized transcription text, if available
        if text := recorder.text():
            # Display the finalized transcription
            print(f"{RESET_CURSOR}{CLEAR_LINE}✍️ {text}\n👄 ", end="", flush=True)
except KeyboardInterrupt:
    # Handle graceful shutdown on Ctrl+C
    print(f"{RESET_CURSOR}{CLEAR_LINE}", end="", flush=True)
    recorder.shutdown()
````

## File: tests/simple_test.py
````python
if __name__ == '__main__':

    import os
    import sys
    if os.name == "nt" and (3, 8) <= sys.version_info < (3, 99):
        from torchaudio._extension.utils import _init_dll_path
        _init_dll_path()

    from RealtimeSTT import AudioToTextRecorder

    recorder = AudioToTextRecorder(
        spinner=False,
        silero_sensitivity=0.01,
        model="tiny.en",
        language="en",
        )

    print("Say something...")
    
    try:
        while (True):
            print("Detected text: " + recorder.text())
    except KeyboardInterrupt:
        print("Exiting application due to keyboard interrupt")
````

## File: tests/translator.py
````python
import os
import openai
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, AzureEngine

if __name__ == '__main__':
    # Setup OpenAI API key
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Text-to-Speech Stream Setup (alternative engines: SystemEngine or ElevenlabsEngine)
    engine = AzureEngine( 
        os.environ.get("AZURE_SPEECH_KEY"),
        os.environ.get("AZURE_SPEECH_REGION")
    )
    stream = TextToAudioStream(engine, log_characters=True)

    # Speech-to-Text Recorder Setup
    recorder = AudioToTextRecorder(
        model="medium",
    )

    # Supported languages and their voices
    languages = [
        ["english", "AshleyNeural"],
        ["german", "AmalaNeural"],
        ["french", "DeniseNeural"],
        ["spanish", "EstrellaNeural"],
        ["portuguese", "FernandaNeural"],
        ["italian", "FabiolaNeural"]
    ]

    def generate_response(messages):
        """Generate assistant's response using OpenAI."""
        for chunk in openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, stream=True):
            text_chunk = chunk["choices"][0]["delta"].get("content")
            if text_chunk:
                yield text_chunk
                
    def clear_console():
        os.system('clear' if os.name == 'posix' else 'cls')

    def select_language():
        """Display language options and get user's choice."""
        for index, language in enumerate(languages, start=1):
            print(f"{index}. {language[0]}")
        language_number = input("Select language to translate to (1-6): ")
        return languages[int(language_number) - 1]

    def main():
        """Main translation loop."""
        clear_console()
        language_info = select_language()
        engine.set_voice(language_info[1])

        system_prompt_message = {
            'role': 'system',
            'content': f'Translate the given text to {language_info[0]}. Output only the translated text.'
        }

        while True:
            print("\nSay something!")

            # Capture user input from microphone
            user_text = recorder.text()
            print(f"Input text: {user_text}")

            user_message = {'role': 'user', 'content': user_text}

            # Get assistant response and play it
            translation_stream = generate_response([system_prompt_message, user_message])
            print("Translation: ", end="", flush=True)
            stream.feed(translation_stream)
            stream.play()

    main()
````

## File: tests/type_into_textbox.py
````python
from RealtimeSTT import AudioToTextRecorder
import pyautogui

def process_text(text):
    pyautogui.typewrite(text + " ")

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder()

    while True:
        recorder.text(process_text)
````

## File: tests/vad_test.py
````python
import asyncio
import time

from RealtimeSTT import AudioToTextRecorder


# Voice Activity Detection (VAD) start handler
def on_vad_detect_start():
    print(f"VAD Start detected at {time.time():.2f}")


# Voice Activity Detection (VAD) stop handler
def on_vad_detect_stop():
    print(f"VAD Stop detected at {time.time():.2f}")


# Transcription completion handler
def on_transcription_finished(text):
    print(f"Transcribed text: {text}")


async def run_recording(recorder):
    # Start recording and process audio in a loop
    print("Starting recording...")
    while True:
        # Use text() to process audio and get transcription
        recorder.text(on_transcription_finished=on_transcription_finished)
        await asyncio.sleep(0.1)  # Prevent tight loop


async def main():
    # Initialize AudioToTextRecorder with VAD event handlers
    recorder = AudioToTextRecorder(
        # model="deepdml/faster-whisper-large-v3-turbo-ct2",
        spinner=False,
        on_vad_detect_start=on_vad_detect_start,
        on_vad_detect_stop=on_vad_detect_stop,
    )

    # Start recording task in a separate thread
    recording_task = asyncio.create_task(run_recording(recorder))

    # Run for 20 seconds to observe VAD events
    await asyncio.sleep(20)

    # Stop recording and shutdown
    print("Stopping recording...")
    recorder.stop()
    recorder.shutdown()

    # Cancel and wait for the recording task to complete
    recording_task.cancel()
    try:
        await recording_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
````

## File: .dockerignore
````
__pycache__
.cache
.dockerignore
docker-compose.yml
Dockerfile
````

## File: docker-compose.yml
````yaml
services:
  rtstt:
    build:
      context: .
      target: gpu # or cpu
    image: rtstt
    container_name: rtstt
    volumes:
      # - ./RealtimeSTT:/app/RealtimeSTT
      # - ./example_browserclient:/app/example_browserclient
      - cache:/root/.cache
    ports:
      - "9001:9001"

    # if 'gpu' target
    deploy:
      resources:
        reservations:
          devices:
          - capabilities: ["gpu"]
  nginx:
    image: nginx:latest
    container_name: nginx_web
    ports:
      - "8081:80"
    volumes:
      - ./example_browserclient:/usr/share/nginx/html

volumes:
  cache:
````

## File: Dockerfile
````dockerfile
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 as gpu

WORKDIR /app

RUN apt-get update -y && \
  apt-get install -y python3 python3-pip libcudnn8 libcudnn8-dev libcublas-12-4 portaudio19-dev

RUN pip3 install torch==2.3.0 torchaudio==2.3.0

COPY requirements-gpu.txt /app/requirements-gpu.txt
RUN pip3 install -r /app/requirements-gpu.txt

RUN mkdir example_browserclient
COPY example_browserclient/server.py /app/example_browserclient/server.py
COPY RealtimeSTT /app/RealtimeSTT

EXPOSE 9001
ENV PYTHONPATH "${PYTHONPATH}:/app"
RUN export PYTHONPATH="${PYTHONPATH}:/app"
CMD ["python3", "example_browserclient/server.py"]

# --------------------------------------------

FROM ubuntu:22.04 as cpu

WORKDIR /app

RUN apt-get update -y && \
  apt-get install -y python3 python3-pip portaudio19-dev

RUN pip3 install torch==2.3.0 torchaudio==2.3.0

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

EXPOSE 9001
ENV PYTHONPATH "${PYTHONPATH}:/app"
RUN export PYTHONPATH="${PYTHONPATH}:/app"
CMD ["python3", "example_browserclient/server.py"]
````

## File: install_with_gpu_support.bat
````
pip install torch==2.1.2+cu118 torchaudio==2.1.2+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements-gpu.txt
````

## File: LICENSE
````
MIT License

Copyright (c) 2023 Kolja Beigel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

## File: MANIFEST.in
````
include requirements.txt
include README.md
include LICENSE
````

## File: README.md
````markdown
# RealtimeSTT
[![PyPI](https://img.shields.io/pypi/v/RealtimeSTT)](https://pypi.org/project/RealtimeSTT/)
[![Downloads](https://static.pepy.tech/badge/RealtimeSTT)](https://www.pepy.tech/projects/realtimestt)
[![GitHub release](https://img.shields.io/github/release/KoljaB/RealtimeSTT.svg)](https://GitHub.com/KoljaB/RealtimeSTT/releases/)
[![GitHub commits](https://badgen.net/github/commits/KoljaB/RealtimeSTT)](https://GitHub.com/Naereen/KoljaB/RealtimeSTT/commit/)
[![GitHub forks](https://img.shields.io/github/forks/KoljaB/RealtimeSTT.svg?style=social&label=Fork&maxAge=2592000)](https://GitHub.com/KoljaB/RealtimeSTT/network/)
[![GitHub stars](https://img.shields.io/github/stars/KoljaB/RealtimeSTT.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/KoljaB/RealtimeSTT/stargazers/)

*Easy-to-use, low-latency speech-to-text library for realtime applications*

## New

- AudioToTextRecorderClient class, which automatically starts a server if none is running and connects to it. The class shares the same interface as AudioToTextRecorder, making it easy to upgrade or switch between the two. (Work in progress, most parameters and callbacks of AudioToTextRecorder are already implemented into AudioToTextRecorderClient, but not all. Also the server can not handle concurrent (parallel) requests yet.)
- reworked CLI interface ("stt-server" to start the server, "stt" to start the client, look at "server" folder for more info)

## About the Project

RealtimeSTT listens to the microphone and transcribes voice into text.  

> **Hint:** *<strong>Check out [Linguflex](https://github.com/KoljaB/Linguflex)</strong>, the original project from which RealtimeSTT is spun off. It lets you control your environment by speaking and is one of the most capable and sophisticated open-source assistants currently available.*

It's ideal for:

- **Voice Assistants**
- Applications requiring **fast and precise** speech-to-text conversion

https://github.com/user-attachments/assets/797e6552-27cd-41b1-a7f3-e5cbc72094f5  

[CLI demo code (reproduces the video above)](tests/realtimestt_test.py)

### Updates

Latest Version: v0.3.104

See [release history](https://github.com/KoljaB/RealtimeSTT/releases).

> **Hint:** *Since we use the `multiprocessing` module now, ensure to include the `if __name__ == '__main__':` protection in your code to prevent unexpected behavior, especially on platforms like Windows. For a detailed explanation on why this is important, visit the [official Python documentation on `multiprocessing`](https://docs.python.org/3/library/multiprocessing.html#multiprocessing-programming).*

## Quick Examples

### Print everything being said:

```python
from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(text)

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder()

    while True:
        recorder.text(process_text)
```

### Type everything being said:

```python
from RealtimeSTT import AudioToTextRecorder
import pyautogui

def process_text(text):
    pyautogui.typewrite(text + " ")

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder()

    while True:
        recorder.text(process_text)
```
*Will type everything being said into your selected text box*

### Features

- **Voice Activity Detection**: Automatically detects when you start and stop speaking.
- **Realtime Transcription**: Transforms speech to text in real-time.
- **Wake Word Activation**: Can activate upon detecting a designated wake word.

> **Hint**: *Check out [RealtimeTTS](https://github.com/KoljaB/RealtimeTTS), the output counterpart of this library, for text-to-voice capabilities. Together, they form a powerful realtime audio wrapper around large language models.*

## Tech Stack

This library uses:

- **Voice Activity Detection**
  - [WebRTCVAD](https://github.com/wiseman/py-webrtcvad) for initial voice activity detection.
  - [SileroVAD](https://github.com/snakers4/silero-vad) for more accurate verification.
- **Speech-To-Text**
  - [Faster_Whisper](https://github.com/guillaumekln/faster-whisper) for instant (GPU-accelerated) transcription.
- **Wake Word Detection**
  - [Porcupine](https://github.com/Picovoice/porcupine) or [OpenWakeWord](https://github.com/dscripka/openWakeWord) for wake word detection.


*These components represent the "industry standard" for cutting-edge applications, providing the most modern and effective foundation for building high-end solutions.*

## Installation

```bash
pip install RealtimeSTT
```

This will install all the necessary dependencies, including a **CPU support only** version of PyTorch.

Although it is possible to run RealtimeSTT with a CPU installation only (use a small model like "tiny" or "base" in this case) you will get way better experience using CUDA (please scroll down).

### Linux Installation

Before installing RealtimeSTT please execute:

```bash
sudo apt-get update
sudo apt-get install python3-dev
sudo apt-get install portaudio19-dev
```

### MacOS Installation

Before installing RealtimeSTT please execute:

```bash
brew install portaudio
```

### GPU Support with CUDA (recommended)

### Updating PyTorch for CUDA Support

To upgrade your PyTorch installation to enable GPU support with CUDA, follow these instructions based on your specific CUDA version. This is useful if you wish to enhance the performance of RealtimeSTT with CUDA capabilities.

#### For CUDA 11.8:
To update PyTorch and Torchaudio to support CUDA 11.8, use the following commands:

```bash
pip install torch==2.5.1+cu118 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118
```

#### For CUDA 12.X:
To update PyTorch and Torchaudio to support CUDA 12.X, execute the following:

```bash
pip install torch==2.5.1+cu121 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
```

Replace `2.5.1` with the version of PyTorch that matches your system and requirements.

### Steps That Might Be Necessary Before

> **Note**: *To check if your NVIDIA GPU supports CUDA, visit the [official CUDA GPUs list](https://developer.nvidia.com/cuda-gpus).*

If you didn't use CUDA models before, some additional steps might be needed one time before installation. These steps prepare the system for CUDA support and installation of the **GPU-optimized** installation. This is recommended for those who require **better performance** and have a compatible NVIDIA GPU. To use RealtimeSTT with GPU support via CUDA please also follow these steps:

1. **Install NVIDIA CUDA Toolkit**:
    - select between CUDA 11.8 or CUDA 12.X Toolkit
        - for 12.X visit [NVIDIA CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive) and select latest version.
        - for 11.8 visit [NVIDIA CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive).
    - Select operating system and version.
    - Download and install the software.

2. **Install NVIDIA cuDNN**:
    - select between CUDA 11.8 or CUDA 12.X Toolkit
        - for 12.X visit [cuDNN Downloads](https://developer.nvidia.com/cudnn-downloads).
            - Select operating system and version.
            - Download and install the software.
        - for 11.8 visit [NVIDIA cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive).
            - Click on "Download cuDNN v8.7.0 (November 28th, 2022), for CUDA 11.x".
            - Download and install the software.
    
3. **Install ffmpeg**:

    > **Note**: *Installation of ffmpeg might not actually be needed to operate RealtimeSTT* <sup> *thanks to jgilbert2017 for pointing this out</sup>

    You can download an installer for your OS from the [ffmpeg Website](https://ffmpeg.org/download.html).  
    
    Or use a package manager:

    - **On Ubuntu or Debian**:
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```

    - **On Arch Linux**:
        ```bash
        sudo pacman -S ffmpeg
        ```

    - **On MacOS using Homebrew** ([https://brew.sh/](https://brew.sh/)):
        ```bash
        brew install ffmpeg
        ```

    - **On Windows using Winget** [official documentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/) :
        ```bash
        winget install Gyan.FFmpeg
        ```
        
    - **On Windows using Chocolatey** ([https://chocolatey.org/](https://chocolatey.org/)):
        ```bash
        choco install ffmpeg
        ```

    - **On Windows using Scoop** ([https://scoop.sh/](https://scoop.sh/)):
        ```bash
        scoop install ffmpeg
        ```    

## Quick Start

Basic usage:

### Manual Recording

Start and stop of recording are manually triggered.

```python
recorder.start()
recorder.stop()
print(recorder.text())
```

#### Standalone Example:

```python
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    recorder = AudioToTextRecorder()
    recorder.start()
    input("Press Enter to stop recording...")
    recorder.stop()
    print("Transcription: ", recorder.text())
```

### Automatic Recording

Recording based on voice activity detection.

```python
with AudioToTextRecorder() as recorder:
    print(recorder.text())
```

#### Standalone Example:

```python
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    with AudioToTextRecorder() as recorder:
        print("Transcription: ", recorder.text())
```

When running recorder.text in a loop it is recommended to use a callback, allowing the transcription to be run asynchronously:


```python
def process_text(text):
    print (text)
    
while True:
    recorder.text(process_text)
```

#### Standalone Example:

```python
from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(text)

if __name__ == '__main__':
    recorder = AudioToTextRecorder()

    while True:
        recorder.text(process_text)
```

### Wakewords

Keyword activation before detecting voice. Write the comma-separated list of your desired activation keywords into the wake_words parameter. You can choose wake words from these list: alexa, americano, blueberry, bumblebee, computer, grapefruits, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator. 

```python
recorder = AudioToTextRecorder(wake_words="jarvis")

print('Say "Jarvis" then speak.')
print(recorder.text())
```

#### Standalone Example:

```python
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    recorder = AudioToTextRecorder(wake_words="jarvis")

    print('Say "Jarvis" to start recording.')
    print(recorder.text())
```

### Callbacks

You can set callback functions to be executed on different events (see [Configuration](#configuration)) :

```python
def my_start_callback():
    print("Recording started!")

def my_stop_callback():
    print("Recording stopped!")

recorder = AudioToTextRecorder(on_recording_start=my_start_callback,
                               on_recording_stop=my_stop_callback)
```

#### Standalone Example:

```python
from RealtimeSTT import AudioToTextRecorder

def start_callback():
    print("Recording started!")

def stop_callback():
    print("Recording stopped!")

if __name__ == '__main__':
    recorder = AudioToTextRecorder(on_recording_start=start_callback,
                                   on_recording_stop=stop_callback)
```

### Feed chunks

If you don't want to use the local microphone set use_microphone parameter to false and provide raw PCM audiochunks in 16-bit mono (samplerate 16000) with this method:

```python
recorder.feed_audio(audio_chunk)
```

#### Standalone Example:

```python
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    recorder = AudioToTextRecorder(use_microphone=False)
    with open("audio_chunk.pcm", "rb") as f:
        audio_chunk = f.read()

    recorder.feed_audio(audio_chunk)
    print("Transcription: ", recorder.text())
```

### Shutdown

You can shutdown the recorder safely by using the context manager protocol:

```python
with AudioToTextRecorder() as recorder:
    [...]
```


Or you can call the shutdown method manually (if using "with" is not feasible):

```python
recorder.shutdown()
```

#### Standalone Example:

```python
from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    with AudioToTextRecorder() as recorder:
        [...]
    # or manually shutdown if "with" is not used
    recorder.shutdown()
```

## Testing the Library

The test subdirectory contains a set of scripts to help you evaluate and understand the capabilities of the RealtimeTTS library.

Test scripts depending on RealtimeTTS library may require you to enter your azure service region within the script. 
When using OpenAI-, Azure- or Elevenlabs-related demo scripts the API Keys should be provided in the environment variables OPENAI_API_KEY, AZURE_SPEECH_KEY and ELEVENLABS_API_KEY (see [RealtimeTTS](https://github.com/KoljaB/RealtimeTTS))

- **simple_test.py**
    - **Description**: A "hello world" styled demonstration of the library's simplest usage.

- **realtimestt_test.py**
    - **Description**: Showcasing live-transcription.

- **wakeword_test.py**
    - **Description**: A demonstration of the wakeword activation.

- **translator.py**
    - **Dependencies**: Run `pip install openai realtimetts`.
    - **Description**: Real-time translations into six different languages.

- **openai_voice_interface.py**
    - **Dependencies**: Run `pip install openai realtimetts`.
    - **Description**: Wake word activated and voice based user interface to the OpenAI API.

- **advanced_talk.py**
    - **Dependencies**: Run `pip install openai keyboard realtimetts`.
    - **Description**: Choose TTS engine and voice before starting AI conversation.

- **minimalistic_talkbot.py**
    - **Dependencies**: Run `pip install openai realtimetts`.
    - **Description**: A basic talkbot in 20 lines of code.

The example_app subdirectory contains a polished user interface application for the OpenAI API based on PyQt5.

## Configuration

### Initialization Parameters for `AudioToTextRecorder`

When you initialize the `AudioToTextRecorder` class, you have various options to customize its behavior.

#### General Parameters

- **model** (str, default="tiny"): Model size or path for transcription.
    - Options: 'tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en', 'medium', 'medium.en', 'large-v1', 'large-v2'.
    - Note: If a size is provided, the model will be downloaded from the Hugging Face Hub.

- **language** (str, default=""): Language code for transcription. If left empty, the model will try to auto-detect the language. Supported language codes are listed in [Whisper Tokenizer library](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py).

- **compute_type** (str, default="default"): Specifies the type of computation to be used for transcription. See [Whisper Quantization](https://opennmt.net/CTranslate2/quantization.html)

- **input_device_index** (int, default=0): Audio Input Device Index to use.

- **gpu_device_index** (int, default=0): GPU Device Index to use. The model can also be loaded on multiple GPUs by passing a list of IDs (e.g. [0, 1, 2, 3]).

- **device** (str, default="cuda"): Device for model to use. Can either be "cuda" or "cpu". 

- **on_recording_start**: A callable function triggered when recording starts.

- **on_recording_stop**: A callable function triggered when recording ends.

- **on_transcription_start**: A callable function triggered when transcription starts.

- **ensure_sentence_starting_uppercase** (bool, default=True): Ensures that every sentence detected by the algorithm starts with an uppercase letter.

- **ensure_sentence_ends_with_period** (bool, default=True): Ensures that every sentence that doesn't end with punctuation such as "?", "!" ends with a period

- **use_microphone** (bool, default=True): Usage of local microphone for transcription. Set to False if you want to provide chunks with feed_audio method.

- **spinner** (bool, default=True): Provides a spinner animation text with information about the current recorder state.

- **level** (int, default=logging.WARNING): Logging level.

- **batch_size** (int, default=16): Batch size for the main transcription. Set to 0 to deactivate.

- **init_logging** (bool, default=True): Whether to initialize the logging framework. Set to False to manage this yourself.

- **handle_buffer_overflow** (bool, default=True): If set, the system will log a warning when an input overflow occurs during recording and remove the data from the buffer.

- **beam_size** (int, default=5): The beam size to use for beam search decoding.

- **initial_prompt** (str or iterable of int, default=None): Initial prompt to be fed to the transcription models.

- **suppress_tokens** (list of int, default=[-1]): Tokens to be suppressed from the transcription output.

- **on_recorded_chunk**: A callback function that is triggered when a chunk of audio is recorded. Submits the chunk data as parameter.

- **debug_mode** (bool, default=False): If set, the system prints additional debug information to the console.

- **print_transcription_time** (bool, default=False): Logs the processing time of the main model transcription. This can be useful for performance monitoring and debugging.

- **early_transcription_on_silence** (int, default=0): If set, the system will transcribe audio faster when silence is detected. Transcription will start after the specified milliseconds. Keep this value lower than `post_speech_silence_duration`, ideally around `post_speech_silence_duration` minus the estimated transcription time with the main model. If silence lasts longer than `post_speech_silence_duration`, the recording is stopped, and the transcription is submitted. If voice activity resumes within this period, the transcription is discarded. This results in faster final transcriptions at the cost of additional GPU load due to some unnecessary final transcriptions.

- **allowed_latency_limit** (int, default=100): Specifies the maximum number of unprocessed chunks in the queue before discarding chunks. This helps prevent the system from being overwhelmed and losing responsiveness in real-time applications.

- **no_log_file** (bool, default=False): If set, the system will skip writing the debug log file, reducing disk I/O. Useful if logging to a file is not needed and performance is a priority.

- **start_callback_in_new_thread** (bool, default=False): If set, the system will create a new thread for all callback functions. This can be useful if the callback function is blocking and you want to avoid blocking the realtimestt application thread. 

#### Real-time Transcription Parameters

> **Note**: *When enabling realtime description a GPU installation is strongly advised. Using realtime transcription may create high GPU loads.*

- **enable_realtime_transcription** (bool, default=False): Enables or disables real-time transcription of audio. When set to True, the audio will be transcribed continuously as it is being recorded.

- **use_main_model_for_realtime** (bool, default=False): If set to True, the main transcription model will be used for both regular and real-time transcription. If False, a separate model specified by `realtime_model_type` will be used for real-time transcription. Using a single model can save memory and potentially improve performance, but may not be optimized for real-time processing. Using separate models allows for a smaller, faster model for real-time transcription while keeping a more accurate model for final transcription.

- **realtime_model_type** (str, default="tiny"): Specifies the size or path of the machine learning model to be used for real-time transcription.
    - Valid options: 'tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en', 'medium', 'medium.en', 'large-v1', 'large-v2'.

- **realtime_processing_pause** (float, default=0.2): Specifies the time interval in seconds after a chunk of audio gets transcribed. Lower values will result in more "real-time" (frequent) transcription updates but may increase computational load.

- **on_realtime_transcription_update**: A callback function that is triggered whenever there's an update in the real-time transcription. The function is called with the newly transcribed text as its argument.

- **on_realtime_transcription_stabilized**: A callback function that is triggered whenever there's an update in the real-time transcription and returns a higher quality, stabilized text as its argument.

- **realtime_batch_size**: (int, default=16): Batch size for the real-time transcription model. Set to 0 to deactivate.

- **beam_size_realtime** (int, default=3): The beam size to use for real-time transcription beam search decoding.

#### Voice Activation Parameters

- **silero_sensitivity** (float, default=0.6): Sensitivity for Silero's voice activity detection ranging from 0 (least sensitive) to 1 (most sensitive). Default is 0.6.

- **silero_use_onnx** (bool, default=False): Enables usage of the pre-trained model from Silero in the ONNX (Open Neural Network Exchange) format instead of the PyTorch format. Default is False. Recommended for faster performance.

- **silero_deactivity_detection** (bool, default=False): Enables the Silero model for end-of-speech detection. More robust against background noise. Utilizes additional GPU resources but improves accuracy in noisy environments. When False, uses the default WebRTC VAD, which is more sensitive but may continue recording longer due to background sounds.

- **webrtc_sensitivity** (int, default=3): Sensitivity for the WebRTC Voice Activity Detection engine ranging from 0 (least aggressive / most sensitive) to 3 (most aggressive, least sensitive). Default is 3.

- **post_speech_silence_duration** (float, default=0.2): Duration in seconds of silence that must follow speech before the recording is considered to be completed. This ensures that any brief pauses during speech don't prematurely end the recording.

- **min_gap_between_recordings** (float, default=1.0): Specifies the minimum time interval in seconds that should exist between the end of one recording session and the beginning of another to prevent rapid consecutive recordings.

- **min_length_of_recording** (float, default=1.0): Specifies the minimum duration in seconds that a recording session should last to ensure meaningful audio capture, preventing excessively short or fragmented recordings.

- **pre_recording_buffer_duration** (float, default=0.2): The time span, in seconds, during which audio is buffered prior to formal recording. This helps counterbalancing the latency inherent in speech activity detection, ensuring no initial audio is missed.

- **on_vad_start**: A callable function triggered when the system has detected the start of voice activity presence.

- **on_vad_stop**: A callable function triggered when the system has detected the stop of voice activity presence.

- **on_vad_detect_start**: A callable function triggered when the system starts to listen for voice activity.

- **on_vad_detect_stop**: A callable function triggered when the system stops to listen for voice activity.

#### Wake Word Parameters

- **wakeword_backend** (str, default="pvporcupine"): Specifies the backend library to use for wake word detection. Supported options include 'pvporcupine' for using the Porcupine wake word engine or 'oww' for using the OpenWakeWord engine.

- **openwakeword_model_paths** (str, default=None): Comma-separated paths to model files for the openwakeword library. These paths point to custom models that can be used for wake word detection when the openwakeword library is selected as the wakeword_backend.

- **openwakeword_inference_framework** (str, default="onnx"): Specifies the inference framework to use with the openwakeword library. Can be either 'onnx' for Open Neural Network Exchange format or 'tflite' for TensorFlow Lite.

- **wake_words** (str, default=""): Initiate recording when using the 'pvporcupine' wakeword backend. Multiple wake words can be provided as a comma-separated string. Supported wake words are: alexa, americano, blueberry, bumblebee, computer, grapefruits, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator. For the 'openwakeword' backend, wake words are automatically extracted from the provided model files, so specifying them here is not necessary.

- **wake_words_sensitivity** (float, default=0.6): Sensitivity level for wake word detection (0 for least sensitive, 1 for most sensitive).

- **wake_word_activation_delay** (float, default=0): Duration in seconds after the start of monitoring before the system switches to wake word activation if no voice is initially detected. If set to zero, the system uses wake word activation immediately.

- **wake_word_timeout** (float, default=5): Duration in seconds after a wake word is recognized. If no subsequent voice activity is detected within this window, the system transitions back to an inactive state, awaiting the next wake word or voice activation.

- **wake_word_buffer_duration** (float, default=0.1): Duration in seconds to buffer audio data during wake word detection. This helps in cutting out the wake word from the recording buffer so it does not falsely get detected along with the following spoken text, ensuring cleaner and more accurate transcription start triggers. Increase this if parts of the wake word get detected as text.

- **on_wakeword_detected**: A callable function triggered when a wake word is detected.

- **on_wakeword_timeout**: A callable function triggered when the system goes back to an inactive state after when no speech was detected after wake word activation.

- **on_wakeword_detection_start**: A callable function triggered when the system starts to listen for wake words

- **on_wakeword_detection_end**: A callable function triggered when stopping to listen for wake words (e.g. because of timeout or wake word detected)

## OpenWakeWord  

### Training models

Look [here](https://github.com/dscripka/openWakeWord?tab=readme-ov-file#training-new-models) for information about how to train your own OpenWakeWord models. You can use a [simple Google Colab notebook](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing) for a start or use a [more detailed notebook](https://github.com/dscripka/openWakeWord/blob/main/notebooks/automatic_model_training.ipynb) that enables more customization (can produce high quality models, but requires more development experience).

### Convert model to ONNX format

You might need to use tf2onnx to convert tensorflow tflite models to onnx format:

```bash
pip install -U tf2onnx
python -m tf2onnx.convert --tflite my_model_filename.tflite --output my_model_filename.onnx
```

### Configure RealtimeSTT

Suggested starting parameters for OpenWakeWord usage:
```python
    with AudioToTextRecorder(
        wakeword_backend="oww",
        wake_words_sensitivity=0.35,
        openwakeword_model_paths="word1.onnx,word2.onnx",
        wake_word_buffer_duration=1,
        ) as recorder:
```

## FAQ

### Q: I encountered the following error: "Unable to load any of {libcudnn_ops.so.9.1.0, libcudnn_ops.so.9.1, libcudnn_ops.so.9, libcudnn_ops.so} Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor." How do I fix this?

**A:** This issue arises from a mismatch between the version of `ctranslate2` and cuDNN. The `ctranslate2` library was updated to version 4.5.0, which uses cuDNN 9.2. There are two ways to resolve this issue:
1. **Downgrade `ctranslate2` to version 4.4.0**:
   ```bash
   pip install ctranslate2==4.4.0
   ```
2. **Upgrade cuDNN** on your system to version 9.2 or above.

## Contribution

Contributions are always welcome! 

Shoutout to [Steven Linn](https://github.com/stevenlafl) for providing docker support. 

## License

[MIT](https://github.com/KoljaB/RealtimeSTT?tab=MIT-1-ov-file)

## Author

Kolja Beigel  
Email: kolja.beigel@web.de  
[GitHub](https://github.com/KoljaB/RealtimeSTT)
````

## File: requirements-gpu.txt
````
PyAudio==0.2.14
faster-whisper==1.1.0
pvporcupine==1.9.5
webrtcvad-wheels==2.0.14
halo==0.0.31
scipy==1.14.1
websockets==14.1
websocket-client==1.8.0
openwakeword>=0.4.0
numpy<2.0.0
````

## File: requirements.txt
````
PyAudio==0.2.14
faster-whisper==1.1.1
pvporcupine==1.9.5
webrtcvad-wheels==2.0.14
halo==0.0.31
torch
torchaudio
scipy==1.15.2
openwakeword>=0.4.0
websockets==15.0.1
websocket-client==1.8.0
soundfile==0.13.1
````

## File: setup.py
````python
import setuptools
import os

# Get the absolute path of requirements.txt
req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

# Read requirements.txt safely
with open(req_path, "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Read README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="realtimestt",
    version="0.3.104",
    author="Kolja Beigel",
    author_email="kolja.beigel@web.de",
    description="A fast Voice Activity Detection and Transcription System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KoljaB/RealTimeSTT",
    packages=setuptools.find_packages(include=["RealtimeSTT", "RealtimeSTT_server"]),
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "Operating System :: OS Independent",
    # ],
    python_requires='>=3.6',
    license='MIT',
    install_requires=requirements,
    keywords="real-time, audio, transcription, speech-to-text, voice-activity-detection, VAD, real-time-transcription, ambient-noise-detection, microphone-input, faster_whisper, speech-recognition, voice-assistants, audio-processing, buffered-transcription, pyaudio, ambient-noise-level, voice-deactivity",
    package_data={"RealtimeSTT": ["warmup_audio.wav"]},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'stt-server=RealtimeSTT_server.stt_server:main',
            'stt=RealtimeSTT_server.stt_cli_client:main',
        ],
    },
)
````

## File: win_installgpu_virtual_env.bat
````
@echo off
cd /d %~dp0

REM Check if the venv directory exists
if not exist test_env\Scripts\python.exe (
    echo Creating VENV
    python -m venv test_env
) else (
    echo VENV already exists
)

echo Activating VENV
start cmd /k "call test_env\Scripts\activate.bat && install_with_gpu_support.bat"
````
