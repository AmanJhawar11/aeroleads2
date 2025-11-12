from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)


latest_call_responses = {} 

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Twilio calls this endpoint when the user answers the phone."""
    resp = VoiceResponse()

  
    gather = Gather(input='speech', action='/gather_response', timeout=5, speechTimeout='auto')
    gather.say("Hello! We are calling to get your feedback on the product you ordered recently. Please tell us your thoughts after the beep.", voice='alice')
    
    resp.append(gather)

    
    resp.say("We didn't hear anything. Goodbye!")
    return str(resp)

@app.route("/gather_response", methods=['GET', 'POST'])
def gather_response():
    """Twilio calls this endpoint with the transcribed text."""
    resp = VoiceResponse()
    
    
    user_speech = request.values.get('SpeechResult', None)
    call_sid = request.values.get('CallSid', None)

    if user_speech:
        
        latest_call_responses[call_sid] = user_speech
        resp.say("Thank you for your feedback! Goodbye.")
    else:
        resp.say("I'm sorry, I didn't catch that. Goodbye.")

    return str(resp)


@app.route("/get_response/<call_sid>", methods=['GET'])
def get_response(call_sid):
    return latest_call_responses.get(call_sid, "NO_RESPONSE")

if __name__ == "__main__":
    
    app.run(debug=True, port=5000)