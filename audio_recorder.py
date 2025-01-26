def get_audio_recorder_html():
    """
    Genera il codice HTML e JavaScript per registrare l'audio e inviarlo al backend Streamlit.
    """
    return """
    <script>
      const startBtn = document.createElement("button");
      const stopBtn = document.createElement("button");

      startBtn.textContent = "Start Recording";
      stopBtn.textContent = "Stop Recording";

      startBtn.style.marginRight = "10px";

      document.body.appendChild(startBtn);
      document.body.appendChild(stopBtn);

      let mediaRecorder;
      let audioChunks = [];

      startBtn.addEventListener("click", async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          const reader = new FileReader();

          reader.onloadend = () => {
            const base64data = reader.result.split(",")[1];
            // Invia il file al backend Streamlit
            fetch("/_stcore/send_audio_blob", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ audio_blob: base64data }),
            }).then(response => {
              if (response.ok) {
                alert("Audio inviato con successo al backend!");
              } else {
                alert("Errore durante l'invio dell'audio al backend.");
              }
            });
          };

          reader.readAsDataURL(audioBlob);
        });

        mediaRecorder.start();
        audioChunks = [];
      });

      stopBtn.addEventListener("click", () => {
        if (mediaRecorder) {
          mediaRecorder.stop();
        }
      });
    </script>
    """
