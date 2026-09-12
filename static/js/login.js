document.addEventListener('DOMContentLoaded', () => {
    auth.redirectIfAuthenticated();

    const form = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoading = loginBtn.querySelector('.btn-loading');
    const errorAlert = document.getElementById('loginError');
    const errorText = document.getElementById('loginErrorText');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const eyeOpen = togglePassword.querySelector('.eye-open');
    const eyeClosed = togglePassword.querySelector('.eye-closed');

    const fields = {
        username: { input: document.getElementById('username'), error: document.getElementById('usernameError') },
        password: { input: document.getElementById('password'), error: document.getElementById('passwordError') }
    };

    function showError(fieldName, message) {
        const field = fields[fieldName];
        if (field) {
            field.input.classList.add('input-error');
            field.error.textContent = message;
        }
    }

    function clearError(fieldName) {
        const field = fields[fieldName];
        if (field) {
            field.input.classList.remove('input-error');
            field.error.textContent = '';
        }
    }

    function clearAllErrors() {
        Object.keys(fields).forEach(clearError);
    }

    function setLoading(loading) {
        loginBtn.disabled = loading;
        btnText.style.display = loading ? 'none' : 'inline';
        btnLoading.style.display = loading ? 'inline-flex' : 'none';
    }

    function showErrorAlert(message) {
        errorText.textContent = message;
        errorAlert.style.display = 'flex';
    }

    function hideErrorAlert() {
        errorAlert.style.display = 'none';
    }

    togglePassword.addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        eyeOpen.style.display = isPassword ? 'none' : 'block';
        eyeClosed.style.display = isPassword ? 'block' : 'none';
    });

    async function login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'Login failed');
        }

        return result;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        clearAllErrors();
        hideErrorAlert();

        const username = fields.username.input.value.trim();
        const password = fields.password.input.value;

        if (!username) {
            showError('username', 'Username is required');
            return;
        }

        if (!password) {
            showError('password', 'Password is required');
            return;
        }

        setLoading(true);

        try {
            const result = await login(username, password);
            auth.setToken(result.access_token);
            window.location.href = '/dashboard';
        } catch (error) {
            showErrorAlert(error.message);
        } finally {
            setLoading(false);
        }
    });

    Object.values(fields).forEach(field => {
        field.input.addEventListener('input', () => clearError(
            Object.keys(fields).find(key => fields[key] === field)
        ));
    });
});