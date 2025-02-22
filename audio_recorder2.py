def get_audio_recorder_html(n):
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registrazione Audio con Trascrizione</title>
        <style>
            .container {
                margin-bottom: 30px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #f8f9fa;
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
                width: 100%;
                height: 100px;
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
            <h3>Registratore {i+1}</h3>
            <canvas id="waveCanvas-{i}" width="600" height="100" style="border:1px solid #ccc; margin-bottom: 10px;"></canvas>
            <div>
                <button class="custom-button" id="startBtn-{i}">Avvia</button>
                <button class="custom-button" id="pauseBtn-{i}" disabled>Pausa</button>
                <button class="custom-button" id="resumeBtn-{i}" disabled>Riprendi</button>
                <button class="custom-button" id="stopBtn-{i}" disabled>Ferma</button>
            </div>
            <textarea class="transcription" id="transcription-{i}" placeholder="La trascrizione apparirà qui..."></textarea>
            <audio id="audioPlayback-{i}" controls style="display: none;"></audio>
            <a id="downloadLink-{i}" style="display:none;">Download Audio</a>
        </div>
        """

    html_content += """
    <button class="custom-button" onclick="downloadAllTranscriptions()">Scarica Tutte le Trascrizioni</button>

    <script>
        function downloadAllTranscriptions() {
            let allTranscriptions = "";
            let allAudioLinks = [];
            
            for (let i = 0; i < """ + str(n) + """; i++) {
                let transcriptionText = document.getElementById(`transcription-${i}`).value;
                let audioLink = document.getElementById(`downloadLink-${i}`).href;

                allTranscriptions += `Registrazione ${i+1}:\n` + transcriptionText + "\\n\\n";
                if (audioLink && audioLink !== "about:blank") {
                    allAudioLinks.push(audioLink);
                }
            }

            alert("Contenuto del file:\\n" + allTranscriptions);

            localStorage.setItem("combined_transcriptions", allTranscriptions);

            let blob = new Blob([allTranscriptions], { type: "text/plain" });
            let a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = "trascrizioni.txt";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
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

                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    let audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                    let audioURL = URL.createObjectURL(audioBlob);
                    audioPlayback.src = audioURL;
                    audioPlayback.style.display = "block";
                    downloadLink.href = audioURL;
                    downloadLink.download = `recording-${index}.wav`;
                    downloadLink.style.display = "block";
                    downloadLink.textContent = "Download Audio";
                };

                mediaRecorder.start();
                startTranscription();

                startBtn.disabled = true;
                pauseBtn.disabled = false;
                stopBtn.disabled = false;
            });

            stopBtn.addEventListener("click", () => {
                mediaRecorder.stop();
                stream.getTracks().forEach((track) => track.stop());
                recognition.stop();
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                resumeBtn.disabled = true;
                stopBtn.disabled = true;
            });
        }

        for (let i = 0; i < """ + str(n) + """; i++) {
            setupRecorder(i);
        }
    </script>
    </body>
    </html>
    """
    return html_content
