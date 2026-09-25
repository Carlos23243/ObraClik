document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    const usuarioInput = document.getElementById('usuario');
    const passwordInput = document.getElementById('password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const alertBox = document.getElementById('loginAlert');

    function mostrarAlerta(mensaje, tipo = 'danger') {
        if (!alertBox) return;
        let icono = tipo === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation';
        alertBox.className = `alert alert-${tipo} alert-dismissible fade show shadow-sm text-start w-100 mb-3`;
        alertBox.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fa-solid ${icono} me-2 fs-5"></i>
                <div>${mensaje}</div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertBox.classList.remove('d-none');
    }

    function ocultarAlerta() {
        if (alertBox) alertBox.classList.add('d-none');
    }

    // Alternar visibilidad de la contraseña
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const esPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', esPassword ? 'text' : 'password');
            const icon = togglePasswordBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-eye');
                icon.classList.toggle('fa-eye-slash');
            }
        });
    }

    // Envío del formulario mediante Fetch / AJAX
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        ocultarAlerta();

        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const textoOriginal = submitBtn ? submitBtn.innerHTML : 'ACCEDER';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-2"></i>VERIFICANDO ACCESO...';
        }

        try {
            const formData = new FormData(loginForm);
            const response = await fetch(loginForm.action || '/login', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            const data = await response.json().catch(() => null);

            if (!data) {
                throw new Error('El servidor respondió con un formato no válido.');
            }

            if (data.success) {
                mostrarAlerta('¡Acceso confirmado! Redirigiendo...', 'success');
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/perfil';
                }, 1000);
            } else {
                mostrarAlerta(data.message || 'Credenciales incorrectas.', 'danger');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = textoOriginal;
                }
            }
        } catch (error) {
            console.error('Error Login:', error);
            mostrarAlerta('Error de conexión o fallo interno en el servidor.', 'danger');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = textoOriginal;
            }
        }
    });
});