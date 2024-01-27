import os
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI

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

# Define the speech-to-text function
def speech_to_text():
    # Set up the audio configuration
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    # Create a speech recognizer and start the recognition
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
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
    # version 0.x
    # response = openai.ChatCompletion.create(
    #     engine=engine_name,
    #     messages=[
    #         {"role": "system", "content": "You are an AI assistant that helps people find information."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.7,
    #     max_tokens=800,
    #     top_p=0.95,
    #     frequency_penalty=0,
    #     presence_penalty=0,
    #     stop=None
    # )
    # version 1.x
    response = client.chat.completions.create(
        model="your_model_name",
        messages=[
            #{"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "system", "content": "你是一名人工智能助手，请帮助我们寻找需要的信息."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content


# Main program loop
while True:
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