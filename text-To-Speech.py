from altair import Encoding
import streamlit as st
import numpy as np
import requests
import openai
from translate import Translator
from googletrans import Translator
from GoogleNews import GoogleNews
from elevenlabs import generate, voices, set_api_key, UnauthenticatedRateLimitError
from configparser import ConfigParser

config = ConfigParser()
language = ['fr', 'it', 'en', 'hi', 'de']
translation = ""

try:
    config.read("config.ini")
    elevenLabs_api_key = config["API"]["ELEVENLABS_API_KEY"]
    openai_api_key = config["API"]["OPENAI_API_KEY"]
    news_api_key = config["API"]["NEWS_API_KEY"]
    news_data_api_key = config["API"]["NEWS_DATA_API_KEY"]
    set_api_key(elevenLabs_api_key)
    openai.api_key = openai_api_key
except:
    raise SystemExit()

def chatGPT(vocab):
    chat_log = []
    user_msg = "What is the definition about " + vocab + "and give me an example"
    chat_log.append({"role" : "user", "content" : user_msg})
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = chat_log 
    )
    content = response['choices'][0]['message']['content']
    return content

def news():

    main_url = "https://newsapi.org/v2/top-headlines?sources=bbc-news&pageSize=5&apiKey="+news_api_key
    news = requests.get(main_url).json()
    articles = news["articles"]
    
    return articles

def display_new(articles):
    tabs = st.tabs(["news1","news2","news3","news4","news5"])
    
    for i in range(5):
        with tabs[i]:
            st.subheader(":blue[" + articles[i]['title'] + "]")
            st.image(articles[i]['urlToImage'], width=500)
            st.caption(articles[i]['description'])
            st.caption(articles[i]['content'])
            st.markdown(articles[i]['url'], unsafe_allow_html=True)    

def translate(input_text, tl):
    translator = Translator()
    translation = translator.translate(input_text, dest=tl)
    return translation.text

def pad_buffer(audio):
    buffer_size = len(audio)
    element_size = np.dtype(np.int16).itemsize
    if buffer_size % element_size != 0:
        audio = audio + b'\0' * (element_size - buffer_size % element_size)
    return audio

def generate_voice(text, voice_name, model_name):
    audio = generate(
        text[:250],
        voice = voice_name,
        model = model_name
    )
    audio_data = np.frombuffer(pad_buffer(audio), dtype=np.int16)
    audio_bytes = audio_data.tobytes()
    return audio_bytes

st.title("Glossika AI Discussion - Anna")
articles = news()
display_new(articles)
st.divider()
description = """Please select a sentence from the news article provided below and indicate your interest in learning the pronunciation of that particular sentence."""
st.info(description)

input_text = st.text_area(
    "Text-To-Speech (250 characters max)",
    value="",
    max_chars=250
)

tl = st.selectbox(
    "Target Language",
    options = [lan for lan in language],
    index=0
)

translation = input_text
translation = translate(input_text, tl)

st.text_area(
    "Translaton",
    value=translation,
    max_chars=250
)

all_voices = voices()
input_voice = st.selectbox(
    "Voice",
    options = [voice.name for voice in all_voices],
    index = 0
)

input_model = st.radio(
    "Model", 
    options=["eleven_monolingual_v1", "eleven_multilingual_v1"],
    index=0
)

if st.button("Generate Voice"):
    print(translation)
    try:
        audio = generate_voice(translation, input_voice, input_model)
        st.audio(audio, format='audio/wav')
    except UnauthenticatedRateLimitError:
        st.error("You've reached the free tier limit!")
    except Exception as e:
        st.error(str(Encoding))


input_vocabulary = st.text_input(
    "Vocabulary:",
    value=""
)

content = ""
if st.button("See the definition and example"):
    st.markdown(chatGPT(input_vocabulary))


