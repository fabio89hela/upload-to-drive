def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per registrare l'audio e salvarlo come file WAV.
    
    Utilizza l'API `MediaRecorder` per registrare l'audio e converte il flusso in un file .wav.
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
      // Elementi HTML per controllare la registrazione
      const startBtn = document.getElementById('startBtn');  // Bottone per iniziare la registrazione
      const pauseBtn = document.getElementById('pauseBtn');  // Bottone per mettere in pausa
      const resumeBtn = document.getElementById('resumeBtn');  // Bottone per riprendere la registrazione
      const stopBtn = document.getElementById('stopBtn');  // Bottone per fermare la registrazione
      const audioPlayback = document.getElementById('audioPlayback');  // Player per riprodurre l'audio registrato
      const waveCanvas = document.getElementById('waveCanvas');  // Canvas per mostrare l'onda audio
      const canvasCtx = waveCanvas.getContext('2d');  // Contesto 2D per disegnare sul canvas

      // Variabili per la gestione della registrazione
      let mediaRecorder;  // Oggetto MediaRecorder per gestire il flusso audio
      let audioChunks = [];  // Array per memorizzare i segmenti audio registrati
      let stream;  // Flusso audio acquisito dal microfono
      let audioContext;  // API Web Audio per analizzare l'audio
      let analyser;  // Analizzatore per visualizzare l'onda audio
      let dataArray;  // Array per memorizzare i dati audio analizzati
      let animationId;  // ID per il rendering dell'animazione dell'onda

      // Funzione per disegnare l'onda audio in tempo reale
      function drawWaveform() {
        analyser.getByteTimeDomainData(dataArray);  // Ottieni i dati audio analizzati
        canvasCtx.fillStyle = 'white';  // Sfondo bianco
        canvasCtx.fillRect(0, 0, waveCanvas.width, waveCanvas.height);  // Pulisci il canvas
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'blue';  // Colore dell'onda audio
        canvasCtx.beginPath();

        const sliceWidth = waveCanvas.width / analyser.fftSize;  // Larghezza di ogni segmento
        let x = 0;

        // Disegna ogni segmento dell'onda
        for (let i = 0; i < analyser.fftSize; i++) {
          const v = dataArray[i] / 128.0;  // Normalizza i dati
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

        // Richiama la funzione per il prossimo frame
        animationId = requestAnimationFrame(drawWaveform);
      }

      // Avvia la registrazione
      startBtn.addEventListener('click', async () => {
        audioChunks = [];  // Resetta l'array dei segmenti audio
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });  // Richiedi il microfono
        audioContext = new AudioContext();  // Crea un nuovo contesto audio
        analyser = audioContext.createAnalyser();  // Crea un analizzatore audio
        const source = audioContext.createMediaStreamSource(stream);  // Collega il flusso audio al contesto
        source.connect(analyser);  // Connetti l'analizzatore
        analyser.fftSize = 2048;  // Imposta la dimensione del buffer
        dataArray = new Uint8Array(analyser.fftSize);  // Crea l'array per i dati audio

        mediaRecorder = new MediaRecorder(stream);  // Crea un oggetto MediaRecorder

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunks.push(event.data);  // Aggiungi i dati registrati all'array
        };

        mediaRecorder.onstop = () => {
          // Quando la registrazione si ferma, converte i dati in un file WAV
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });  // Crea un file WAV
          const audioURL = URL.createObjectURL(audioBlob);  // Crea un URL per il file WAV
          audioPlayback.src = audioURL;  // Imposta il file WAV nel player audio
          audioPlayback.style.display = 'block';  // Mostra il player
        };

        mediaRecorder.start();  // Avvia la registrazione
        drawWaveform();  // Avvia il disegno dell'onda audio

        // Aggiorna lo stato dei pulsanti
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
      });

      // Metti in pausa la registrazione
      pauseBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.pause();  // Metti in pausa la registrazione
          pauseBtn.disabled = true;
          resumeBtn.disabled = false;
          cancelAnimationFrame(animationId);  // Ferma il rendering dell'onda
        }
      });

      // Riprendi la registrazione
      resumeBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'paused') {
          mediaRecorder.resume();  // Riprendi la registrazione
          resumeBtn.disabled = true;
          pauseBtn.disabled = false;
          drawWaveform();  // Riprendi il disegno dell'onda
        }
      });

      // Ferma la registrazione
      stopBtn.addEventListener('click', () => {
        if (mediaRecorder) {
          mediaRecorder.stop();  // Ferma la registrazione
          stream.getTracks().forEach((track) => track.stop());  // Ferma il microfono
          startBtn.disabled = false;
          pauseBtn.disabled = true;
          resumeBtn.disabled = true;
          stopBtn.disabled = true;
        }
      });
    </script>
    """
