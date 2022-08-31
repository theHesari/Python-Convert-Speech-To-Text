import time
import requests
from api_secrets import API_KEY_ASSEMBLYAI

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
headers = {'authorization': API_KEY_ASSEMBLYAI}
#-----------This wav is included in file folder, 
#-----------feel free to change it with yours;)
filename = "OSR_us_000_0010_8k.wav"


#UPLOAD LOCAL FILE FOR TRASCRIPTION
def upload(filename):
    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data
    upload_response = requests.post(upload_endpoint,
                            headers=headers,
                            data=read_file(filename))

    audio_URL = upload_response.json()['upload_url']
    return audio_URL

#SUBMIT YOUR UPLOAD TO TRANSCRIPTION
def transcribe(audio_url):
    transcribe_request = { "audio_url": audio_url }
    headers = {
        "authorization": API_KEY_ASSEMBLYAI,
        "content-type": "application/json"
    }
    transcribe_response = requests.post(transcript_endpoint, json=transcribe_request, headers=headers)
    transcript_ID = transcribe_response.json()['id']
    return transcript_ID



#POLL

def poll(transcript_ID):
    poll_endpoint = transcript_endpoint + "/" + transcript_ID
    poll_response = requests.get(poll_endpoint, headers=headers)
    return poll_response.json()

def get_transcription_response_url(audio_url):
    transcript_ID = transcribe(audio_url)
    while True:
        data = poll(transcript_ID)
        if data['status'] == "completed":
            return data, None
        elif data['status'] == "error":
            return data, data['error']

        print("Retrying in 30 seconds...")
        time.sleep(30)


#Done with Uploading, Trancrption, and Pollin!! 
#Now let's save our transcription to a text file

def save_transcription(audio_url):
    
    data , error = get_transcription_response_url(audio_url)
    if data:
        text_file = filename + ".txt"
        with open (text_file, "w") as f:
            f.write(data['text'])
        print("Transcription is Done!")
    elif error:
        print("We got an Error!", error)

