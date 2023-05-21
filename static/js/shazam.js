document.addEventListener('DOMContentLoaded', function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        const listenBtn = document.getElementById('listen-btn');
        listenBtn.addEventListener('click', () => {
          listen();
        });

        listen();


        mediaRecorder.addEventListener('dataavailable', event => {
          recordedAudio = new Blob([event.data], { type: 'audio/mp3' });
          			var formData = new FormData();
			formData.append('audio', recordedAudio);
			//console.log('sending audio');

			fetch('/upload-audio', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.title && data.subtitle) {
                    const imageUrl = data.image;
                    const myImage = document.getElementById('myImage');
                    myImage.src = imageUrl;
                    myImage.style.display = 'block'; // Display the image
                    document.getElementById('result-text').innerText = data.title + " - " + data.subtitle;
                    withoutPulsing();
                } else {
                    imageElement.style.display = 'none'; // Hide the image element if there is no image
                }
            })
            .catch(function (error) {
                console.error(error);
            });

        });

          function withoutPulsing() {
                document.getElementById('pulse-circle-small').style.display = 'none';
                document.getElementById('pulse-circle-medium').style.display = 'none';
                document.getElementById('pulse-circle-large').style.display = 'none';
                listenBtn.style.display = 'none';
              }

        function listen(){
                 var counter=0;
                    startPulsing();
                    if (mediaRecorder.state !== "recording"){
                     mediaRecorder.start();}

         const intervalId=setInterval(function()
         { if (mediaRecorder.state == "recording")
         {mediaRecorder.stop(); mediaRecorder.start();}
            counter++;
            if (counter === 10) {
                clearInterval(intervalId);
                stopPulsing();
            }
           }, 5000);}

           function stopPulsing(){
                document.getElementById('pulse-circle-small').classList.remove('pulse-circle');
                document.getElementById('pulse-circle-small').classList.add('pulse-circle-stop');
                document.getElementById('pulse-circle-medium').classList.remove('pulse-circle');
                document.getElementById('pulse-circle-medium').classList.add('pulse-circle-stop');
                document.getElementById('pulse-circle-large').classList.remove('pulse-circle');
                document.getElementById('pulse-circle-large').classList.add('pulse-circle-stop');
                document.getElementById('listen-btn').classList.remove('pulse-button');
                document.getElementById('listen-btn').classList.add('pulse-button-stop');
                document.getElementById('listen-btn').innerText = "Sorry, try again";
           }

            function startPulsing(){
                document.getElementById('pulse-circle-small').classList.add('pulse-circle');
                document.getElementById('pulse-circle-small').classList.remove('pulse-circle-stop');
                document.getElementById('pulse-circle-medium').classList.add('pulse-circle');
                document.getElementById('pulse-circle-medium').classList.remove('pulse-circle-stop');
                document.getElementById('pulse-circle-large').classList.add('pulse-circle');
                document.getElementById('pulse-circle-large').classList.remove('pulse-circle-stop');
                document.getElementById('listen-btn').classList.add('pulse-button');
                document.getElementById('listen-btn').classList.remove('pulse-button-stop');
                document.getElementById('listen-btn').innerText = "Listening...";
            }


      })
      .catch(error => {
        console.error('Failed to get media device:', error);
      });
});