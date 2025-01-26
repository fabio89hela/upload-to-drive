def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per registrare l'audio e inviarlo al backend Streamlit tramite Streamlit Custom Events.
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
          audioChunks = [];
        } catch (error) {
          statusMsg.textContent = "Errore: impossibile accedere al microfono.";
          console.error("Errore durante la registrazione:", error);
        }
      });

      stopBtn.addEventListener("click", async () => {
        statusMsg.textContent = "Processing audio..."; // Messaggio di stato
        stopBtn.disabled = true;
        startBtn.disabled = false;

        mediaRecorder.stop();

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          const reader = new FileReader();

          reader.onloadend = () => {
            const base64data = reader.result.split(",")[1]; // Estrai il contenuto Base64
            // Invia i dati al backend Streamlit usando streamlit-custom-event
            const event = new CustomEvent("streamlit:sendAudio", { detail: base64data });
            document.dispatchEvent(event);
            statusMsg.textContent = "Audio inviato con successo al backend!";
          };

          reader.readAsDataURL(audioBlob); // Leggi il Blob audio
        };
      });
    </script>
    """
