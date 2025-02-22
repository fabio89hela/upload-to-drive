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

    # **Generazione dinamica dei registratori**
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

    # **Aggiungere il pulsante per scaricare tutte le trascrizioni**
    html_content += """
    <div style="text-align:center; margin-top:20px;">
        <button id="downloadAllBtn" class="custom-button">Scarica Tutte le Trascrizioni</button>
    </div>

    <script>
        function downloadAllTranscriptions() {
            let allTranscriptions = "";
            let allAudioLinks = [];
            
            for (let i = 0; i < """ + str(n) + """; i++) {
                let transcriptionText = document.getElementById(`transcription-${i}`).value;
                let audioLink = document.getElementById(`downloadLink-${i}`).href;

                allTranscriptions += `Registrazione ${i+1}:\\n` + transcriptionText + "\\n\\n";
                if (audioLink && audioLink !== "about:blank") {
                    allAudioLinks.push(audioLink);
                }
            }

            // **Mostrare il contenuto in un alert**
            alert("Contenuto del file:\\n" + allTranscriptions);

            // **Salva il testo delle trascrizioni in localStorage per Streamlit**
            localStorage.setItem("combined_transcriptions", allTranscriptions);

            // **Creare un file di testo con le trascrizioni**
            let blob = new Blob([allTranscriptions], { type: "text/plain" });
            let a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = "trascrizioni.txt";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // **Scaricare tutti gli audio registrati**
            allAudioLinks.forEach(link => {
                let audioA = document.createElement("a");
                audioA.href = link;
                audioA.download = link.split('/').pop();
                document.body.appendChild(audioA);
                audioA.click();
                document.body.removeChild(audioA);
            });

            parent.window.token = allTranscriptions;  // Passa il testo a Streamlit
        }

        // **Aggiungere l'evento al pulsante dopo il caricamento**
        document.addEventListener("DOMContentLoaded", function() {
            document.getElementById("downloadAllBtn").addEventListener("click", downloadAllTranscriptions);
        });
    </script>
    </body>
    </html>
    """
    return html_content
