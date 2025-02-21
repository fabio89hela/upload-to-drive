def get_audio_recorder_html(n):
    html_content = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrazione Multipla</title>
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
            transition: all 0.1s ease-in-out;
            display: inline-block;
            text-decoration: none;
        }

        .custom-button:hover {
            border: 1px solid #FBB614;
            color: #FBB614;
        }

        .custom-button:disabled {
            color: #adb5bd;
            border-color: #dee2e6;
            cursor: not-allowed;
        }

        #transcription {
            width: 100%;
            height: 150px;
            overflow-y: auto;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            resize: vertical;
        }

        .record-container {
            margin-bottom: 20px;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 8px;
            background-color: #fff;
        }

        canvas {
            border: 1px solid #ccc;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>

<!-- Textarea visibile sempre in alto -->
<h3>Trascrizione Completa</h3>
<textarea id="transcription" placeholder="Le trascrizioni appariranno qui..."></textarea>

<!-- Contenitore per i registratori -->
<div id="recordingsContainer"></div>

<script>
    let numRecorders = 3;  // Numero di registratori audio
    let transcriptionText = "";  // Memorizza la trascrizione completa

    function createRecorder(index) {
        // Creare il contenitore del registratore
        const container = document.createElement("div");
        container.classList.add("record-container");
        container.innerHTML = `
            <h4>Registratore ${index + 1}</h4>
            <canvas id="waveCanvas${index}" width="600" height="150"></canvas>
            <br>
            <button class="custom-button" id="startBtn${index}">Avvia</button>
            <button class="custom-button" id="stopBtn${index}" disabled>Ferma</button>
            <br><br>
            <audio id="audioPlayback${index}" controls style="display: none;"></audio>
        `;

        document.getElementById("recordingsContainer").appendChild(container);

        // Elementi HTML
        const startBtn = document.getElementById(`startBtn${index}`);
        const stopBtn = document.getElementById(`stopBtn${index}`);
        const audioPlayback = document.getElementById(`audioPlayback${index}`);
        const waveCanvas = document.getElementById(`waveCanvas${index}`);
        const canvasCtx = waveCanvas.getContext("2d");

        let mediaRecorder;
        let audioChunks = [];
        let stream;
        let audioContext;
        let analyser;
        let dataArray;
        let recognition;
        let finalTranscript = "";

        function drawWaveform() {
            analyser.getByteTimeDomainData(dataArray);
            canvasCtx.fillStyle = "white";
            canvasCtx.fillRect(0, 0, waveCanvas.width, waveCanvas.height);
            canvasCtx.lineWidth = 2;
            canvasCtx.strokeStyle = "blue";
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

            requestAnimationFrame(drawWaveform);
        }

        function startTranscription() {
            if (!('webkitSpeechRecognition' in window)) {
                console.log("Il riconoscimento vocale non è supportato su questo browser.");
                return;
            }

            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'it-IT';

            recognition.onresult = (event) => {
                let interimTranscript = "";

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript + " ";
                    } else {
                        interimTranscript += event.results[i][0].transcript + " ";
                    }
                }

                // Aggiunge la trascrizione alla textarea globale con separatore
                transcriptionText += `\n===== INIZIO REGISTRAZIONE ${index + 1} =====\n` + finalTranscript + interimTranscript;
                document.getElementById("transcription").value = transcriptionText;
            };

            recognition.onerror = (event) => {
                console.error("Errore nel riconoscimento vocale: ", event.error);
            };

            recognition.start();
        }

        startBtn.addEventListener("click", async () => {
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
                const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                const audioURL = URL.createObjectURL(audioBlob);

                audioPlayback.src = audioURL;
                audioPlayback.style.display = "block";

                recognition.stop();

                // Aggiungi un marcatore alla trascrizione globale
                transcriptionText += `\n===== FINE REGISTRAZIONE ${index + 1} =====\n`;
            };

            mediaRecorder.start();
            drawWaveform();
            startTranscription();

            startBtn.disabled = true;
            stopBtn.disabled = false;
        });

        stopBtn.addEventListener("click", () => {
            if (mediaRecorder) {
                mediaRecorder.stop();
                stream.getTracks().forEach((track) => track.stop());
                recognition.stop();

                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        });
    }

    // Genera n registratori indipendenti
    for (let i = 0; i < numRecorders; i++) {
        createRecorder(i);
    }
</script>

</body>
</html>
    """
    return html_content
