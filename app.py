import streamlit as st
import os
import tempfile

def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per la registrazione audio.
    """
    return """
    <canvas id="waveCanvas" width="600" height="200" style="border:1px solid #ccc; margin-bottom: 20px;"></canvas>
    <div style="margin-bottom: 20px;">
      <button id="startBtn">Start Recording</button>
      <button id="pauseBtn" disabled>Pause</button>
      <button id="resumeBtn" disabled>Resume</button>
      <button id="stopBtn" disabled>Stop</button>
    </div>
    <audio id="audioPlayback" controls style="display: none; margin-top: 20px;"></audio>

    <script>
      const startBtn = document.getElementById('startBtn');
      const pauseBtn = document.getElementById('pauseBtn');
      const resumeBtn = document.getElementById('resumeBtn');
      const stopBtn = document.getElementById('stopBtn');
      const audioPlayback = document.getElementById('audioPlayback');
      const waveCanvas = document.getElementById('waveCanvas');
      const canvasCtx = waveCanvas.getContext('2d');

      let mediaRecorder;
      let audioChunks = [];
      let stream;
      let audioContext;
      let analyser;
      let dataArray;
      let animationId;

      function drawWaveform() {
        analyser.getByteTimeDomainData(dataArray);
        canvasCtx.fillStyle = 'white';
        canvasCtx.fillRect(0, 0, waveCanvas.width, waveCanvas.height);
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'blue';
        canvasCtx.beginPath();

        const sliceWidth = waveCanvas.width / analyser.fftSize;
        let x = 0;

        for (let i = 0; i < analyser.fftSize; i++) {
          const v = dataArray[i] / 128.0;
          const y = (v * waveCanvas.height) / 2;

          if (i === 0) {
            canvasCtx.moveTo(x, y);
          } else {
            canvasCtx.lineTo(x, y);
          }

          x += sliceWidth;
        }

        canvasCtx.lineTo(waveCanvas.width, waveCanvas.height / 2);
        canvasCtx.stroke();

        animationId = requestAnimationFrame(drawWaveform);
      }

      startBtn.addEventListener('click', async () => {
        audioChunks = [];
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new AudioContext();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 2048;
        dataArray = new Uint8Array(analyser.fftSize);

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunks.push(event.data);
        };

mediaRecorder.onstop = () => {
  const audioBlob = new Blob(audioChunks, { type: 'audio/ogg; codecs=opus' });
  const audioURL = URL.createObjectURL(audioBlob);
  audioPlayback.src = audioURL;
  audioPlayback.style.display = 'block';

  // Invia il file al backend
  const formData = new FormData();
  formData.append('file', audioBlob, 'recorded_audio.ogg');

  fetch('/upload-audio', {
    method: 'POST',
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log('File salvato con successo:', data);
      // Puoi aggiornare l'interfaccia Streamlit qui
    })
    .catch((error) => {
      console.error('Errore durante l\'upload del file:', error);
    });
};

        mediaRecorder.start();
        drawWaveform();

        startBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
      });

      pauseBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.pause();
          pauseBtn.disabled = true;
          resumeBtn.disabled = false;
          cancelAnimationFrame(animationId);
        }
      });

      resumeBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'paused') {
          mediaRecorder.resume();
          resumeBtn.disabled = true;
          pauseBtn.disabled = false;
          drawWaveform();
        }
      });

      stopBtn.addEventListener('click', () => {
        if (mediaRecorder) {
          mediaRecorder.stop();
          stream.getTracks().forEach((track) => track.stop());
          startBtn.disabled = false;
          pauseBtn.disabled = true;
          resumeBtn.disabled = true;
          stopBtn.disabled = true;
        }
      });
    </script>
    """

# Funzione per salvare il file temporaneamente
def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name

# Layout Streamlit
st.title("Audio Recorder")

st.components.v1.html(get_audio_recorder_html(), height=500)

# Placeholder per il caricamento
uploaded_file = st.file_uploader("Carica un file audio salvato", type=["ogg"])

if uploaded_file:
    temp_path = save_uploaded_file(uploaded_file)
    st.success(f"File salvato temporaneamente in: {temp_path}")

    # Puoi usare temp_path come input per altre funzioni
    st.write("Percorso del file temporaneo:", temp_path)

