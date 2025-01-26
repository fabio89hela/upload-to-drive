def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per registrare l'audio e inviarlo al backend Streamlit.
    """
    return """
    <div style="text-align: center; margin-top: 20px;">
      <button id="startBtn" style="margin-right: 10px; padding: 10px 20px; font-size: 16px;">Start Recording</button>
      <button id="stopBtn" style="padding: 10px 20px; font-size: 16px;" disabled>Stop Recording</button>
    </div>
    <p id="statusMsg" style="margin-top: 20px; font-size: 14px; color: green; text-align: center;"></p>

    <script>
      let mediaRecorder;
      let audioChunks = [];

      const startBtn = document.getElementById("startBtn");
      const stopBtn = document.getElementById("stopBtn");
      const statusMsg = document.getElementById("statusMsg");

      startBtn.addEventListener("click", async () => {
        // Richiedi permesso per il microfono e inizializza la registrazione
        statusMsg.textContent = "Recording..."; // Messaggio di stato
        startBtn.disabled = true;
        stopBtn.disabled = false;

        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(stream);

          mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
              audioChunks.push(event.data);
            }
          };

          mediaRecorder.start();
        } catch (error) {
          statusMsg.textContent = "Errore: impossibile accedere al microfono.";
          console.error("Errore durante la registrazione:", error);
        }
      });

      stopBtn.addEventListener("click", async () => {
        // Ferma la registrazione
        stopBtn.disabled = true;
        startBtn.disabled = false;

        statusMsg.textContent = "Processing audio..."; // Messaggio di stato

        mediaRecorder.stop();

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          const reader = new FileReader();

          reader.onloadend = () => {
            const base64data = reader.result.split(",")[1]; // Estrai il contenuto Base64

            // Invia il file audio al backend Streamlit
            fetch("/_stcore/send_audio_blob", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ audio_blob: base64data }),
            }).then((response) => {
              if (response.ok) {
                statusMsg.textContent = "Audio inviato con successo al backend!";
              } else {
                statusMsg.textContent = "Errore durante l'invio dell'audio.";
              }
            }).catch((error) => {
              console.error("Errore durante l'invio dell'audio:", error);
              statusMsg.textContent = "Errore durante l'invio dell'audio.";
            });
          };

          reader.readAsDataURL(audioBlob); // Leggi il Blob audio
        };
      });
    </script>
    """
