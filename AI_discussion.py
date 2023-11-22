import gradio as gr
import openai
import winsound
from elevenlabslib import *
from elevenlabslib import ElevenLabsUser
from pydub import AudioSegment
from pydub.playback import play
import io
from configparser import ConfigParser

config = ConfigParser()

try:
    config.read("config.ini")
except:
    print(config["API"]["OPENAI_API_KEY"])
    raise SystemExit()

openai.api_key = config["API"]["OPENAI_API_KEY"]
api_key = config["API"]["ELEVENLABS_API_KEY"]
user = ElevenLabsUser(api_key)

messages = ["You are an advisor. Please respond to all input in 50 words or less."]

def transcribe(audio):
    global messages

    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    messages.append(f"\nUser: {transcript['text']}")

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=messages[-1],
        max_tokens=80,
        n=1,
        stop=None,
        temperature=0.5,
    )

    system_message = response["choices"][0]["text"]
    messages.append(f"{system_message}")

    test_msg = "123456789"

    voice = user.get_voices_by_name("Bella")[0]
    audio = voice.generate_audio_bytes(test_msg)

    audio = AudioSegment.from_file(io.BytesIO(audio), format="mp3")
    audio.export("output.wav", format="wav")

    winsound.PlaySound("output.wav", winsound.SND_FILENAME)

    chat_transcript = "\n".join(messages)
    return chat_transcript

iface = gr.Interface(
    fn=transcribe,
    inputs=gr.Audio(source="microphone", type="filepath", placeholder="Please start speaking..."),
    outputs="text",
    title="🤖 My Desktop ChatGPT Assistant 🤖",
    description="🌟 Please ask me your question and I will respond both verbally and in text to you...",
)

iface.launch()