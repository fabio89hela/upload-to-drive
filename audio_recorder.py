def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per registrare l'audio, 
    salvare il file come WAV e permettere il download.
    """
    return """
    <!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrazione Audio</title>
    <style>
        .custom-button {
            background-color: white;
            color: #34637D;
            border: 1px solid #34637D;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            font-family: Arial, sans-serif;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
            display: inline-block;
            text-decoration: none;
        }

        .custom-button:hover {
            border:1px solid #FBB614;
            color:#FBB614;
        }

        .custom-button:disabled {
            color: #adb5bd;
            border-color: #dee2e6;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
<canvas id="waveCanvas" width="600" height="200" style="border:1px solid #ccc; margin-bottom: 20px;"></canvas>
    <div style="margin-bottom: 20px;">
      <button class="custom-button" id="startBtn">Avvia registrazione</button>
      <button class="custom-button" id="pauseBtn" disabled>Pausa</button>
      <button class="custom-button" id="resumeBtn" disabled>Riprendi</button>
      <button class="custom-button" id="stopBtn" disabled>Ferma registrazione</button>
      <a id="downloadLink" style="display:none; margin-top: 20px;">Download Audio</a>
    </div>
    <audio id="audioPlayback" controls style="display: none; margin-top: 20px;"></audio>

    <script>
      const startBtn = document.getElementById('startBtn');
      const pauseBtn = document.getElementById('pauseBtn');
      const resumeBtn = document.getElementById('resumeBtn');
      const stopBtn = document.getElementById('stopBtn');
      const audioPlayback = document.getElementById('audioPlayback');
      const downloadLink = document.getElementById('downloadLink');
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
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          const audioURL = URL.createObjectURL(audioBlob);

          // Mostra l'audio nel player
          audioPlayback.src = audioURL;
          audioPlayback.style.display = 'block';

          // Imposta il link per il download
          downloadLink.href = audioURL;
          downloadLink.download = "recording.wav";
          downloadLink.style.display = 'block';
          downloadLink.textContent = "Download Audio";

          cancelAnimationFrame(animationId);  // Ferma il rendering dell'onda
        };

        mediaRecorder.start();
        drawWaveform();  // Avvia il rendering dell'onda

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
</body>
</html>
    """
