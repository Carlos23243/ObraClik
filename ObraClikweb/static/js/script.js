/**
 * ObraClick - Script Principal Unificado
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavegacionHero();
    initRegistroForm();
    initPedidosPanel();
    initFiltroServicios();
    initModuloNosotros();
});

/* ==========================================
   1. NAVEGACIÓN Y MENÚ FLOTANTE
   ========================================== */
function initNavegacionHero() {
    const toggleBtn = document.getElementById('toggleDropdownBtn');
    const dropdownPanel = document.getElementById('userDropdownPanel');
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');

    if (!toggleBtn || !dropdownPanel) return;

    toggleBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        dropdownPanel.classList.toggle('d-none');
    });

    document.addEventListener('click', (event) => {
        if (!dropdownPanel.contains(event.target) && !toggleBtn.contains(event.target)) {
            dropdownPanel.classList.add('d-none');
        }
    });

    if (searchForm) {
        searchForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const query = searchInput ? searchInput.value.trim() : '';
            if (query && dropdownPanel) {
                dropdownPanel.classList.add('d-none');
            }
        });
    }
}


/* ==========================================
   3. PÁGINA DE REGISTRO DE USUARIO (AJAX)
   ========================================== */
function initRegistroForm() {
    const registroForm = document.getElementById('registroForm');
    if (!registroForm) return;

    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const alertBox = document.getElementById('registroAlert');

    function mostrarAlertaRegistro(mensaje, tipo = 'danger') {
        if (!alertBox) {
            alert(mensaje);
            return;
        }
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

    registroForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (passwordInput && confirmPasswordInput && passwordInput.value !== confirmPasswordInput.value) {
            mostrarAlertaRegistro('Las contraseñas no coinciden. Por favor, verícalas.', 'warning');
            confirmPasswordInput.focus();
            return;
        }

        if (passwordInput && passwordInput.value.length < 6) {
            mostrarAlertaRegistro('La contraseña debe tener al menos 6 caracteres.', 'warning');
            passwordInput.focus();
            return;
        }

        const submitBtn = document.getElementById('btnRegistro') || registroForm.querySelector('button[type="submit"]');
        const textoOriginal = submitBtn ? submitBtn.innerHTML : 'REGISTRARSE';

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-2"></i>GUARDANDO DATOS...';
        }

        try {
            const formData = new FormData(registroForm);
            const response = await fetch(registroForm.action || '/registro', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            const data = await response.json().catch(() => null);

            if (!data) {
                throw new Error("Respuesta del servidor no válida.");
            }

            if (data.success) {
                mostrarAlertaRegistro(data.message || '¡Registro completado con éxito!', 'success');
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/login';
                }, 1200);
            } else {
                mostrarAlertaRegistro(data.message || 'Error al procesar el registro.', 'danger');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = textoOriginal;
                }
            }
        } catch (error) {
            console.error('Error Registro:', error);
            mostrarAlertaRegistro('Ocurrió un error de conexión con el servidor MySQL.', 'danger');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = textoOriginal;
            }
        }
    });
}

/* ==========================================
   4. FILTRADO DE SERVICIOS / ESPECIALISTAS
   ========================================== */
function initFiltroServicios() {
    const searchInput = document.getElementById('searchProfiles') || document.getElementById('searchInput');
    const profileCards = document.querySelectorAll('.profile-card');

    if (!searchInput || profileCards.length === 0) return;

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();

        profileCards.forEach(card => {
            const titleElement = card.querySelector('.profile-title') || card;
            const titleText = titleElement.textContent.toLowerCase();

            const container = card.closest('.col-12, .col-md-6, .col-lg-4') || card;

            if (titleText.includes(searchTerm)) {
                container.style.display = '';
            } else {
                container.style.display = 'none';
            }
        });
    });
}

/* ==========================================
   5. PANEL DE PEDIDOS Y NOSOTROS
   ========================================== */
function initPedidosPanel() {
    const pedidosTabContainer = document.getElementById('pedidosTab');
    if (!pedidosTabContainer) return;

    const tabButtons = pedidosTabContainer.querySelectorAll('button[data-bs-toggle="pill"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', (event) => {
            console.log(`Pestaña activa: ${event.target.getAttribute('data-bs-target')}`);
        });
    });
}

function initModuloNosotros() {
    const categoryLinks = document.querySelectorAll('.sub-nav-categories .nav-link');
    categoryLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            categoryLinks.forEach(item => item.classList.remove('active'));
            link.classList.add('active');
        });
    });
}