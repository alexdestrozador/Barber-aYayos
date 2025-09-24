document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('container');
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');

    if (registerBtn && loginBtn && container) {
        registerBtn.addEventListener('click', () => {
            container.classList.add("active");
        });

        loginBtn.addEventListener('click', () => {
            container.classList.remove("active");
        });
    }

    const formRegistro = document.getElementById('form-registro');

    if (formRegistro) {
        formRegistro.addEventListener('submit', function(event) {
            let valid = true;

            // Limpiar errores anteriores
            document.querySelectorAll('.error-msg').forEach(e => {
                e.textContent = '';
                e.style.display = 'none';
                e.classList.remove('visible-error');
            });

            // Obtener valores
            const usernameInput = document.getElementById('login-username');
            const username = usernameInput ? usernameInput.value.trim() : '';
            const nombre = document.getElementById('reg-nombre').value.trim();
            const correo = document.getElementById('reg-correo').value.trim();
            const telefono = document.getElementById('reg-telefono').value.trim();
            const password = document.getElementById('reg-password').value.trim();

            // Mostrar error
            function mostrarError(id, mensaje) {
                const errorElem = document.getElementById(id);
                if (errorElem) {
                    errorElem.textContent = mensaje;
                    errorElem.style.display = 'block';
                    errorElem.classList.add('visible-error');

                    setTimeout(() => {
                        if (errorElem.classList.contains('visible-error')) {
                            errorElem.style.display = 'none';
                            errorElem.classList.remove('visible-error');
                        }
                    }, 5000);
                }
            }

            // Validaciones
            if (username.length < 4 || username.length > 30) {
                mostrarError('error-username', "Debe tener entre 4 y 30 caracteres.");
                valid = false;
            }

            if (nombre.length < 3) {
                mostrarError('error-nombre', "El nombre debe tener al menos 3 caracteres.");
                valid = false;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(correo)) {
                mostrarError('error-correo', "Correo electrónico inválido.");
                valid = false;
            }

            const telefonoRegex = /^\d{7,15}$/;
            if (!telefonoRegex.test(telefono)) {
                mostrarError('error-telefono', "Teléfono inválido (de 7 a 15 dígitos).");
                valid = false;
            }

            const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
            if (!passwordRegex.test(password)) {
                mostrarError('error-password', "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y símbolos.");
                valid = false;
            }

            if (!valid) {
                event.preventDefault(); // Bloquear envío si hay errores
            }
        });
    }
});
