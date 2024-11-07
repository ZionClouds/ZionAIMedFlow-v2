// SpeechToText.tsx
import { createSignal, onMount, onCleanup } from 'solid-js'
import * as SpeechSDK from 'microsoft-cognitiveservices-speech-sdk';




const App = () => {
  const [transcript, setTranscript] = createSignal<string>('')
  const [isListening, setIsListening] = createSignal<boolean>(false)
  const [lastUpdate, setLastUpdate] = createSignal<Date | null>(null)

  const subscriptionKey = 'b04cbdc36763482884bc5a09309541e6';
  const region = 'centralus';


  const updateTranscriptPeriodically = () => {
    const intervalId = setInterval(() => {
      const currentTranscript = transcript();
      console.log(`Current Transcript: ${currentTranscript}`);
      setLastUpdate(new Date());
    }, 5000);
    onCleanup(() => clearInterval(intervalId));
  };
  updateTranscriptPeriodically();

  const muteMicrophone = () => {
    const audioTracks = navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => stream.getAudioTracks())
      .catch(error => {
        console.error('Error accessing audio tracks:', error);
        return [];
      });

    audioTracks.then(tracks => {
      tracks.forEach(track => track.enabled = false);
      console.log('Microphone muted');
    });
  };

  const unmuteMicrophone = () => {
    const audioTracks = navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => stream.getAudioTracks())
      .catch(error => {
        console.error('Error accessing audio tracks:', error);
        return [];
      });

    audioTracks.then(tracks => {
      tracks.forEach(track => track.enabled = true);
      console.log('Microphone unmuted');
    });
  };


  const startRecognition = () => {
    const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(subscriptionKey, region);
    const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
    const recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);

    recognizer.recognizing = (_, e) => {
      console.log(`RECOGNIZING: Text=${e.result.text}`);
    };

    recognizer.recognized = (_, e) => {
      if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
        console.log(`RECOGNIZED: Text=${e.result.text}`);
        const newText = transcript() + e.result.text + "\n"
        setTranscript(newText)
      } else if (e.result.reason === SpeechSDK.ResultReason.NoMatch) {
        console.log('NOMATCH: Speech could not be recognized.');
      }
    };

    recognizer.canceled = (_, e) => {
      console.log(`CANCELED: Reason=${e.reason}`);
      if (e.reason === SpeechSDK.CancellationReason.Error) {
        console.log(`CANCELED: ErrorCode=${e.errorCode}`);
        console.log(`CANCELED: ErrorDetails=${e.errorDetails}`);
      }
      recognizer.stopContinuousRecognitionAsync();
      setIsListening(false);
    };

    recognizer.sessionStopped = (s, e) => {
      console.log('Session stopped.', s, e);
      recognizer.stopContinuousRecognitionAsync();
      setIsListening(false);
    };

    recognizer.startContinuousRecognitionAsync();
    setIsListening(true);
  };

  const stopRecognition = () => {
    setIsListening(false);
    muteMicrophone();
  };


  onMount(() => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
          console.log('Microphone access granted');
        })
        .catch((error) => {
          console.error('Microphone access denied', error);
        });
    } else {
      console.error('getUserMedia not supported on your browser!');
    }
  });

  return (
    <div>
      <h1>Azure Speech-to-Text</h1>
      <button class={'bg-blue-600 text-white p-2 ' + (isListening() ? 'animate-pulse' : '')} onClick={() => { isListening() ? stopRecognition() : startRecognition() }}>
        {isListening() ? 'Stop Listening' : 'Start Listening'}
      </button>
      <div class="flex bg-slate-50">
        <div class="w-1/2 flex flex-col p-2">
          <p>Transcript:</p>
          <textarea class='w-full' readOnly rows={10} value={transcript()} />
        </div>
        <div class="w-1/2 flex flex-col p-2">
          <p>Summary:</p>
          <textarea class='w-full' readOnly rows={10} value={transcript()} />
          <p>Last update: {lastUpdate()?.toLocaleTimeString()}</p>
        </div>
      </div>


    </div>
  );
};

export default App;