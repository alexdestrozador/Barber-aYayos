 document.addEventListener("DOMContentLoaded", function () {
        const checkboxes = document.querySelectorAll(".dia-checkbox");

        checkboxes.forEach(function (checkbox) {
            checkbox.addEventListener("change", function () {
                const dia = checkbox.value;
                const inputInicio = document.getElementById("hora_inicio_" + dia);
                const inputFin = document.getElementById("hora_fin_" + dia);

                if (checkbox.checked) {
                    inputInicio.removeAttribute("disabled");
                    inputFin.removeAttribute("disabled");
                } else {
                    inputInicio.setAttribute("disabled", "disabled");
                    inputFin.setAttribute("disabled", "disabled");
                }
            });

            // Activar si el checkbox está marcado al cargar (por si se regresa con error)
            if (checkbox.checked) {
                const dia = checkbox.value;
                document.getElementById("hora_inicio_" + dia).removeAttribute("disabled");
                document.getElementById("hora_fin_" + dia).removeAttribute("disabled");
            }
        });
    });