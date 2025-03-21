async function writeNFC() {
    let plataform = document.getElementById("plataform").value;
    let music_service = document.getElementById("spotify_service").value != "" ? document.getElementById("spotify_service").value : document.getElementById("apple_service").value;
    let tag = document.getElementById("nfc-message").value;

    message = '' + plataform + ':' + music_service + ':' + tag;

    if (!message) {
        alert("Ingresa un mensaje para escribir en NFC.");
        return;
    }

    let response = await fetch("/write_nfc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    });
    let result = await response.json();
    // alert(result.message);
    let box_message = document.getElementById("box-message");
    // Guarda el contenido original
    let mensajeOriginal = box_message.innerHTML;

    // Cambia el mensaje con el nuevo contenido
    box_message.innerHTML = '<p>' + result.message + '</p>';

    tag = "";

    // Después de 5 segundos, restaurar el mensaje original
    setTimeout(() => {
        box_message.innerHTML = mensajeOriginal;        
    }, 2000);
}

function changePlataform (){
    let select = document.getElementById("plataform");
    let spotify_service = document.getElementById("spotify_service");
    let apple_service = document.getElementById("apple_service");
    let selected = select.value;

    if(selected === "applemusic"){
        spotify_service.value = "";
        document.querySelector('.apple').style.display = 'block';
        document.querySelector('.spotify').style.display = 'none';
    } else {
        apple_service.value = "";
        document.querySelector('.apple').style.display = 'none';
        document.querySelector('.spotify').style.display = 'block';
    }
}

function  changeSonos() {
    const select = document.getElementById("sonos");
    const selectedUrl = select.value;
    window.location.href = selectedUrl; // Esto redirige la página
}

window.addEventListener("beforeunload", function(event) {
    navigator.sendBeacon("/remove_lock");
});