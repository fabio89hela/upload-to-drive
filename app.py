import streamlit as st
from io import BytesIO

# Funzione per gestire la registrazione
def handle_audio_upload():
    # Verifica se è stato inviato un file
    if "file" in st.session_state:
        # Leggi il file audio dalla sessione
        audio_file = st.session_state["file"]

        st.audio(audio_file, format="audio/wav")
        st.success("File registrato caricato con successo!")

def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per registrare l'audio, 
    salvarlo temporaneamente e inviarlo al backend Streamlit.
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

        mediaRecorder.onstop = async () => {
          // Quando la registrazione si ferma
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });  // Crea un file WAV
          const audioURL = URL.createObjectURL(audioBlob);  // Crea un URL per il player
          audioPlayback.src = audioURL;
          audioPlayback.style.display = 'block';

          // Invia il file WAV al backend Streamlit
          const formData = new FormData();
          formData.append("file", audioBlob, "recording.wav");

          await fetch("/", {
            method: "POST",
            body: formData,
          }).then((response) => {
            if (response.ok) {
              console.log("File audio inviato con successo");
            } else {
              console.error("Errore durante l'invio del file audio");
            }
          });
        };

        mediaRecorder.start();  // Avvia la registrazione
        drawWaveform();  // Avvia il rendering dell'onda audio

        // Aggiorna lo stato dei pulsanti
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
      });

      pauseBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.pause();
          pauseBtn.disabled = true;
          resumeBtn.disabled = false;
          cancelAnimationFrame(animationId);  // Ferma il rendering
        }
      });

      resumeBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'paused') {
          mediaRecorder.resume();
          resumeBtn.disabled = true;
          pauseBtn.disabled = false;
          drawWaveform();  // Riprendi il rendering
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

# Configura Streamlit
st.set_page_config(page_title="Registrazione Audio")
st.title("Registrazione Audio in Streamlit")

# Inserisci l'interfaccia HTML per la registrazione
st.components.v1.html(get_audio_recorder_html(), height=500)

# Gestione dell'upload
if st.session_state.get("file"):
    handle_audio_upload()

# Upload manuale (solo test)
uploaded_file = st.file_uploader("Carica un file audio", type=["wav", "mp3"])
if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
