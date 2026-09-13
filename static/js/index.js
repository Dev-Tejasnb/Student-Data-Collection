document.addEventListener('DOMContentLoaded', () => {
    // Batch Alert Modal
    const batchAlertModal = document.getElementById('batchAlertModal');
    const batchAlertOkBtn = document.getElementById('batchAlertOkBtn');

    function showBatchAlert() {
        batchAlertModal.classList.add('active');
        batchAlertOkBtn.focus();
    }

    function hideBatchAlert() {
        batchAlertModal.classList.remove('active');
    }

    // Show batch alert on page load
    showBatchAlert();

    // Close modal on OK button click
    batchAlertOkBtn.addEventListener('click', hideBatchAlert);

    // Close modal on overlay click
    batchAlertModal.querySelector('.modal-overlay').addEventListener('click', hideBatchAlert);

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && batchAlertModal.classList.contains('active')) {
            hideBatchAlert();
        }
    });

    // Prevent body scroll when modal is open
    const observer = new MutationObserver(() => {
        if (batchAlertModal.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    });
    observer.observe(batchAlertModal, { attributes: true, attributeFilter: ['class'] });

    const form = document.getElementById('studentForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const submitAnotherBtn = document.getElementById('submitAnotherBtn');

    const fields = {
        name: { input: document.getElementById('name'), error: document.getElementById('nameError') },
        batch: { input: document.getElementById('batch'), error: document.getElementById('batchError') },
        course: { input: document.getElementById('course'), error: document.getElementById('courseError') },
        college: { input: document.getElementById('college'), error: document.getElementById('collegeError') },
        admission_through: { input: document.getElementById('admission_through'), error: document.getElementById('admissionError') }
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
        submitBtn.disabled = loading;
        btnText.style.display = loading ? 'none' : 'inline';
        btnLoading.style.display = loading ? 'inline-flex' : 'none';
    }

    function showSuccess() {
        form.style.display = 'none';
        errorMessage.style.display = 'none';
        successMessage.style.display = 'block';
    }

    function showErrorAlert(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'flex';
        successMessage.style.display = 'none';
    }

    function hideMessages() {
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
    }

    function resetForm() {
        form.reset();
        clearAllErrors();
        hideMessages();
        form.style.display = 'block';
    }

    function validateForm() {
        let isValid = true;
        clearAllErrors();

        const name = fields.name.input.value.trim();
        if (!name) {
            showError('name', 'Full name is required');
            isValid = false;
        } else if (name.length > 100) {
            showError('name', 'Name must be less than 100 characters');
            isValid = false;
        }

        const batch = fields.batch.input.value;
        if (!batch) {
            showError('batch', 'Please select a batch');
            isValid = false;
        } else if (!['FTB', 'Batch - 1', 'Batch - 2', 'Batch - 3'].includes(batch)) {
            showError('batch', 'Invalid batch selection');
            isValid = false;
        }

        const course = fields.course.input.value.trim();
        if (!course) {
            showError('course', 'Course is required');
            isValid = false;
        } else if (course.length > 100) {
            showError('course', 'Course must be less than 100 characters');
            isValid = false;
        }

        const college = fields.college.input.value.trim();
        if (!college) {
            showError('college', 'College is required');
            isValid = false;
        } else if (college.length > 200) {
            showError('college', 'College must be less than 200 characters');
            isValid = false;
        }

        const admission = fields.admission_through.input.value;
        if (!admission) {
            showError('admission_through', 'Please select an admission method');
            isValid = false;
        } else if (!['KCET', 'NEET', 'NUCAT', 'MANAGEMENT'].includes(admission)) {
            showError('admission_through', 'Invalid admission method');
            isValid = false;
        }

        return isValid;
    }

    async function submitForm(data) {
        const response = await fetch('/api/students', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const contentType = response.headers.get('content-type') || '';
        let result = {};

        if (contentType.includes('application/json')) {
            result = await response.json();
        } else {
            const text = await response.text();
            result = { message: text };
        }

        if (!response.ok) {
            throw new Error(
                result.message ||
                result.detail ||
                'Failed to submit student details'
            );
        }

        return result;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);
        hideMessages();

        const formData = {
            name: fields.name.input.value.trim(),
            batch: fields.batch.input.value,
            course: fields.course.input.value.trim(),
            college: fields.college.input.value.trim(),
            admission_through: fields.admission_through.input.value
        };

        try {
            await submitForm(formData);
            showSuccess();
        } catch (error) {
            showErrorAlert(error.message);
        } finally {
            setLoading(false);
        }
    });

    submitAnotherBtn.addEventListener('click', resetForm);

    Object.values(fields).forEach(field => {
        field.input.addEventListener('input', () => clearError(
            Object.keys(fields).find(key => fields[key] === field)
        ));
    });
});