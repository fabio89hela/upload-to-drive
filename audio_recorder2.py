import json
def get_audio_recorder_html(n,domande):
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registrazione Audio con Trascrizione</title>
        <style>
            .container {
                font-family:Arial, sans-self;
                margin-bottom: 20px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #d5e4e7;
                color: #34637D;
                align-items:center;
            }
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
                margin-top: 10px;
            }
            .custom-button:hover {
                border: 1px solid #FBB614;
                color: #FBB614;
            }
            .transcription {
                width: 95%;
                max-width:1200px;
                height: 150px;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-family: Arial, sans-serif;
                background-color: white;
                resize: vertical;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
    """
        
    for i in range(n):
        html_content += f"""
        <div class="container">
            <p>"""+str(domande[i])+f"""</p>
            <canvas id="waveCanvas-{i}" width="500" height="100" style="border:1px solid #ccc; margin-bottom: 10px"></canvas>
            <div style="margin-bottom: 15px;">
                <button class="custom-button" id="startBtn-{i}">Avvia</button>
                <button class="custom-button" id="pauseBtn-{i}" disabled>Pausa</button>
                <button class="custom-button" id="resumeBtn-{i}" disabled>Riprendi</button>
                <button class="custom-button" id="stopBtn-{i}" disabled>Ferma</button>
            </div>
            <textarea class="transcription" id="transcription-{i}" placeholder="La trascrizione apparirà qui..." style="color: #34637D; border: 1px solid #34637D;border-radius: 8px;"></textarea>
            <audio id="audioPlayback-{i}" controls style="display: none;"></audio>
            <a id="downloadLink-{i}" style="display:none;">Download Audio</a>
        </div>
        """
        
    js_domande = json.dumps(domande)
    html_content += f"""
    <button class="custom-button" onclick="downloadAllTranscriptions()">Scarica e salva su Drive</button>
    <script>
        let recorders=[];
        let audioBlobs = [];
        let domande = {js_domande};
        """
    html_content += """
        function downloadAllTranscriptions() {
            let allTranscriptions = "";
            let allAudioLinks = [];
            for (let i = 0; i < """ + str(n) + """; i++) {
                let transcriptionText = document.getElementById(`transcription-${i}`).value;
                let audioLink = document.getElementById(`downloadLink-${i}`).href;

                allTranscriptions += domande[i] + ": " + transcriptionText + "\\n\\n";
                if (audioLink && audioLink !== "about:blank") {
                    allAudioLinks.push(audioLink);
                }
            }

            localStorage.setItem("combined_transcriptions", allTranscriptions);
            localStorage.setItem("update_time", new Date().getTime());
            
            let blob = new Blob([allTranscriptions], { type: "text/plain" });
            let a = document.createElement("a");
            let fileURL= URL.createObjectURL(blob);
            a.href = fileURL;
            a.download = "trascrizioni.txt";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // **Scaricare tutti gli audio registrati**
            if (audioBlobs.length > 0) {
                const combinedBlob = new Blob(audioBlobs, { type: "audio/webm" });
                const combinedUrl = URL.createObjectURL(combinedBlob);
                const audioA = document.createElement("a");
                audioA.href = combinedUrl;
                audioA.download = "audio_completo.webm";
                document.body.appendChild(audioA);
                audioA.click();
                document.body.removeChild(audioA);
            }
            
            // **Nuova aggiunta**
            if (audioBlobs.length > 0) {
                const combinedBlob = new Blob(audioBlobs, { type: "audio/webm" });
                const reader = new FileReader();
                reader.onloadend = function () {
                localStorage.setItem("audio_blob_base64", reader.result);
            };
            reader.readAsDataURL(combinedBlob);
}
            
            parent.window.token = allTranscriptions;  // Passa il testo a Streamlit 
        }

        function setupRecorder(index) {
            let startBtn = document.getElementById(`startBtn-${index}`);
            let pauseBtn = document.getElementById(`pauseBtn-${index}`);
            let resumeBtn = document.getElementById(`resumeBtn-${index}`);
            let stopBtn = document.getElementById(`stopBtn-${index}`);
            let audioPlayback = document.getElementById(`audioPlayback-${index}`);
            let downloadLink = document.getElementById(`downloadLink-${index}`);
            let transcriptionDiv = document.getElementById(`transcription-${index}`);
            let waveCanvas = document.getElementById(`waveCanvas-${index}`);
            let canvasCtx = waveCanvas.getContext("2d");

            let mediaRecorder;
            let audioChunks = [];
            let stream;
            let recognition;
            let finalTranscript = "";
            let animationId;

            let audioContext;
            let analyser;
            let dataArray;
            let source;

            function drawWaveform() {
                if (!analyser) return;

                analyser.getByteTimeDomainData(dataArray);
                canvasCtx.fillStyle = "white";
                canvasCtx.fillRect(0, 0, waveCanvas.width, waveCanvas.height);
                canvasCtx.lineWidth = 2;
                canvasCtx.strokeStyle = "blue";
                canvasCtx.beginPath();
                let sliceWidth = waveCanvas.width / analyser.fftSize;
                let x = 0;

                for (let i = 0; i < analyser.fftSize; i++) {
                    let v = dataArray[i] / 128.0;
                    let y = (v * waveCanvas.height) / 2;
                    if (i === 0) canvasCtx.moveTo(x, y);
                    else canvasCtx.lineTo(x, y);
                    x += sliceWidth;
                }
                canvasCtx.stroke();
                animationId = requestAnimationFrame(drawWaveform);
            }

            function startTranscription() {
                recognition = new webkitSpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = "it-IT";

                recognition.onresult = (event) => {
                    let interimTranscript = "";
                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        if (event.results[i].isFinal) {
                            finalTranscript += event.results[i][0].transcript + " ";
                        } else {
                            interimTranscript += event.results[i][0].transcript + " ";
                        }
                    }
                    transcriptionDiv.value = finalTranscript + interimTranscript;
                };

                recognition.start();
            }

            startBtn.addEventListener("click", async () => {
                audioChunks = [];
                stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 2048;
                dataArray = new Uint8Array(analyser.fftSize);
                
                source = audioContext.createMediaStreamSource(stream);
                source.connect(analyser);
                
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = () => {
                    let audioBlob = new Blob(audioChunks, { type: "audio/webm" });  // usa webm per concatenazione semplice
                    audioBlobs[index] = audioBlob;
                    let audioURL = URL.createObjectURL(audioBlob);
                    audioPlayback.src = audioURL;
                    audioPlayback.style.display = "block";
                    downloadLink.href = audioURL;
                    downloadLink.download = `recording-${index}.wav`;
                    downloadLink.style.display = "block";
                    downloadLink.textContent = "Download Audio";
                    cancelAnimationFrame(animationId);
                };

                mediaRecorder.start();
                drawWaveform();
                startTranscription();

                startBtn.disabled = true;
                pauseBtn.disabled = false;
                stopBtn.disabled = false;
            });

            pauseBtn.addEventListener("click", () => {
                if (mediaRecorder.state === "recording") {
                    mediaRecorder.pause();
                    recognition.stop();
                    pauseBtn.disabled = true;
                    resumeBtn.disabled = false;
                    cancelAnimationFrame(animationId);
                }
            });

            resumeBtn.addEventListener("click", () => {
                if (mediaRecorder.state === "paused") {
                    mediaRecorder.resume();
                    startTranscription();
                    resumeBtn.disabled = true;
                    pauseBtn.disabled = false;
                    drawWaveform();
                }
            });

            stopBtn.addEventListener("click", () => {
                mediaRecorder.stop();
                stream.getTracks().forEach((track) => track.stop());
                recognition.stop();
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                resumeBtn.disabled = true;
                stopBtn.disabled = true;
                cancelAnimationFrame(animationId);
            });

            recorders.push({ startBtn, pauseBtn, resumeBtn, stopBtn, mediaRecorder });
        }

        for (let i = 0; i < """ + str(n) + """; i++) {
            setupRecorder(i);
        }
    </script>
    </body>
    </html>
    """
    return html_content
