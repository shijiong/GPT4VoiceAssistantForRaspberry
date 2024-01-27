import os
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
import time

# Set up OpenAI API credentials
client = AzureOpenAI(
  azure_endpoint = "https://yourresource.openai.azure.com/", 
  api_key="your_apikey",  
  api_version="your_api_version"
)

# Set up Azure Speech-to-Text and Text-to-Speech credentials
speech_key = "your_speech_key"
service_region = "your_service_region"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Set up Azure Text-to-Speech language 
speech_config.speech_synthesis_language = "zh-CN"
# Set up Azure Speech-to-Text language recognition
speech_config.speech_recognition_language = "zh-CN"

# Set up the voice configuration
speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Creates an instance of a keyword recognition model. Update this to
# point to the location of your keyword recognition model.
model = speechsdk.KeywordRecognitionModel("your_keyword_model.table")
# The phrase your keyword recognition model triggers on.
keyword = "小智"
# Create a local keyword recognizer with the default microphone device for input.
keyword_recognizer = speechsdk.KeywordRecognizer()
done = False

# Set up the audio configuration
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
# Create a speech recognizer and start the recognition
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# Define the speech-to-text function
def speech_to_text():

    print("请跟我聊点什么吧...")

    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "对不起，我没有听懂"
    elif result.reason == speechsdk.ResultReason.Canceled:
        return "语音识别取消."

# Define the text-to-speech function
def text_to_speech(text):
    try:
        result = speech_synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Text-to-speech conversion successful.")
            return True
        else:
            print(f"Error synthesizing audio: {result}")
            return False
    except Exception as ex:
        print(f"Error synthesizing audio: {ex}")
        return False

# Define the Azure OpenAI language generation function
def generate_text(prompt):
    response = client.chat.completions.create(
        model="your_model_id",
        messages=[
            #{"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "system", "content": "你是一名人工智能助手，请帮助我们寻找需要的信息."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content

def recognized_cb(evt):
    # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
    # and there is no timeout. The recognizer runs until a keyword phrase
    # is detected or recognition is canceled (by stop_recognition_async()
    # or due to the end of an input file or stream).
    result = evt.result
    if result.reason == speechsdk.ResultReason.RecognizedKeyword:
        print("RECOGNIZED KEYWORD: {}".format(result.text))
    global done
    done = True

def canceled_cb(evt):
    result = evt.result
    if result.reason == speechsdk.ResultReason.Canceled:
        print('CANCELED: {}'.format(result.cancellation_details.reason))
    global done
    done = True

# Connect callbacks to the events fired by the keyword recognizer.
keyword_recognizer.recognized.connect(recognized_cb)
keyword_recognizer.canceled.connect(canceled_cb)

# Main program loop
while True:

    # Start keyword recognition.
    result_future = keyword_recognizer.recognize_once_async(model)

    while True:
        print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
        result = result_future.get()

        # Read result audio (incl. the keyword).
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
           print("Keyword recognized")
           break
        else:
           print("Keyword not recognized")

    # Get input from user using speech-to-text
    user_input = speech_to_text()
    print(f"You said: {user_input}")

    # Generate a response using OpenAI
    prompt = f"Q: {user_input}\nA:"
    response = generate_text(prompt)
    #response = user_input
    print(f"AI says: {response}")

    # Convert the response to speech using text-to-speech
    text_to_speech(response)