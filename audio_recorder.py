def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per registrare un file audio in formato MP3.
    Questo codice utilizza l'API MediaRecorder del browser e converte l'output in MP3.
    """
    return """
    <!-- Canvas per visualizzare l'onda audio -->
    <canvas id="waveCanvas" width="600" height="200" style="border:1px solid #ccc; margin-bottom: 20px;"></canvas>

    <!-- Pulsanti di controllo per la registrazione -->
    <div style="margin-bottom: 20px;">
      <button id="startBtn">Start Recording</button>
      <button id="pauseBtn" disabled>Pause</button>
      <button id="resumeBtn" disabled>Resume</button>
      <button id="stopBtn" disabled>Stop</button>
    </div>

    <!-- Player per riprodurre l'audio registrato -->
    <audio id="audioPlayback" controls style="display: none; margin-top: 20px;"></audio>

    <!-- Includi la libreria lamejs per la conversione in MP3 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lamejs/1.2.0/lame.min.js"></script>

    <script>
      // Elementi della pagina HTML
      const startBtn = document.getElementById('startBtn');
      const pauseBtn = document.getElementById('pauseBtn');
      const resumeBtn = document.getElementById('resumeBtn');
      const stopBtn = document.getElementById('stopBtn');
      const audioPlayback = document.getElementById('audioPlayback');
      const waveCanvas = document.getElementById('waveCanvas');
      const canvasCtx = waveCanvas.getContext('2d');

      // Variabili per la registrazione e l'analisi audio
      let mediaRecorder;
      let audioChunks = [];  // Buffer per i dati audio grezzi
      let stream;
      let audioContext;
      let analyser;
      let dataArray;
      let animationId;

      // Funzione per disegnare l'onda audio in tempo reale
      function drawWaveform() {
        analyser.getByteTimeDomainData(dataArray);  // Ottieni dati grezzi dall'analizzatore
        canvasCtx.fillStyle = 'white';
        canvasCtx.fillRect(0, 0, waveCanvas.width, waveCanvas.height);  // Pulisci il canvas
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'blue';
        canvasCtx.beginPath();

        const sliceWidth = waveCanvas.width / analyser.fftSize;  // Larghezza di ogni segmento
        let x = 0;

        for (let i = 0; i < analyser.fftSize; i++) {
          const v = dataArray[i] / 128.0;  // Normalizza il valore (tra 0 e 1)
          const y = (v * waveCanvas.height) / 2;

          if (i === 0) {
            canvasCtx.moveTo(x, y);  // Inizia il disegno
          } else {
            canvasCtx.lineTo(x, y);  // Disegna il segmento successivo
          }

          x += sliceWidth;
        }

        canvasCtx.lineTo(waveCanvas.width, waveCanvas.height / 2);  // Completa la linea
        canvasCtx.stroke();

        animationId = requestAnimationFrame(drawWaveform);  // Chiama la funzione in loop
      }

      // Avvia la registrazione
      startBtn.addEventListener('click', async () => {
        audioChunks = [];  // Svuota i dati audio
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });  // Ottieni il flusso audio dal microfono
        audioContext = new AudioContext();
        analyser = audioContext.createAnalyser();  // Crea l'analizzatore
        const source = audioContext.createMediaStreamSource(stream);  // Collega il microfono all'analizzatore
        source.connect(analyser);
        analyser.fftSize = 2048;  // Imposta la risoluzione FFT
        dataArray = new Uint8Array(analyser.fftSize);  // Buffer per i dati grezzi

        mediaRecorder = new MediaRecorder(stream);

        // Salva i dati audio grezzi quando disponibili
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunks.push(event.data);
        };

        // Quando la registrazione termina
        mediaRecorder.onstop = () => {
          // Concatena i dati audio grezzi in un unico blob
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

          // Converte il blob in MP3 usando lamejs
          const reader = new FileReader();
          reader.onload = function(event) {
            const arrayBuffer = event.target.result;
            const wav = lamejs.WavHeader.readHeader(new DataView(arrayBuffer));  // Leggi l'header WAV
            const samples = new Int16Array(arrayBuffer, wav.dataOffset, wav.dataLen / 2);  // Ottieni i campioni audio
            const mp3Encoder = new lamejs.Mp3Encoder(1, wav.sampleRate, 128);  // Crea un encoder MP3
            const mp3Data = mp3Encoder.encodeBuffer(samples);  // Codifica in MP3
            const mp3Blob = new Blob(mp3Data, { type: 'audio/mp3' });  // Crea il blob MP3

            // Mostra il file MP3 nel player audio
            const mp3URL = URL.createObjectURL(mp3Blob);
            audioPlayback.src = mp3URL;
            audioPlayback.style.display = 'block';
          };
          reader.readAsArrayBuffer(audioBlob);  // Leggi i dati audio come array buffer
        };

        mediaRecorder.start();  // Avvia la registrazione
        drawWaveform();  // Avvia il rendering dell'onda audio

        // Aggiorna lo stato dei pulsanti
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
      });

      // Metti in pausa la registrazione
      pauseBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.pause();
          pauseBtn.disabled = true;
          resumeBtn.disabled = false;
          cancelAnimationFrame(animationId);  // Ferma il rendering dell'onda
        }
      });

      // Riprendi la registrazione
      resumeBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'paused') {
          mediaRecorder.resume();
          resumeBtn.disabled = true;
          pauseBtn.disabled = false;
          drawWaveform();  // Riprendi il rendering dell'onda
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
