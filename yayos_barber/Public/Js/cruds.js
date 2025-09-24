setTimeout(function() {
    const mensaje = document.getElementById('mensaje-exito');
    if (mensaje) {
        mensaje.style.display = 'none';
    }
}, 5000); //Para la validación cuando se envía el formulario de servicios



function validarCampo(input) {
    const errorId = "error-" + input.id;
    const errorMsg = document.getElementById(errorId);

    if (input.id === "duracion") {
    const obligatorioMsg = document.getElementById("error-duracion-obligatorio");
    const invalidoMsg = document.getElementById("error-duracion-invalido");

    if (input.value === "") {
        obligatorioMsg.style.display = "block";
        invalidoMsg.style.display = "none";
    } else if (input.value <= 0) {
        invalidoMsg.style.display = "block";
        obligatorioMsg.style.display = "none";
    } else {
        invalidoMsg.style.display = "none";
        obligatorioMsg.style.display = "none";
    }

    } else if (input.id === "nombre") {
        if (input.value.trim() === "" || input.value.length > 30) {
            errorMsg.textContent = "Llena este campo. ¡Recuerda que es obligatorio y no puede exceder 30 caracteres!";
            errorMsg.style.display = "block";
        } else {
            errorMsg.style.display = "none";
        }

    } else if (input.id === "precio") {
        const valor = parseFloat(input.value);
        if (isNaN(valor) || valor <= 0 || valor > "99999999") {
            errorMsg.textContent = "Ingrese por favor un valor válido";
            errorMsg.style.display = "block";
        } else {
            errorMsg.style.display = "none";
        }

    } else {
        if (input.value.trim() === "") {
            errorMsg.style.display = "block";
        } else {
            errorMsg.style.display = "none";
        }
    }
}



