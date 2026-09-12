document.addEventListener('DOMContentLoaded', () => {
    auth.redirectIfNotAuthenticated();

    const urlParams = new URLSearchParams(window.location.search);
    const studentId = urlParams.get('id');

    if (!studentId) {
        window.location.href = '/dashboard';
        return;
    }

    const editBtn = document.getElementById('editBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    const pdfBtn = document.getElementById('pdfBtn');
    const editModal = document.getElementById('editModal');
    const closeEditModal = document.getElementById('closeEditModal');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const editForm = document.getElementById('editForm');
    const saveEditBtn = document.getElementById('saveEditBtn');
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const cancelDeleteConfirmBtn = document.getElementById('cancelDeleteConfirmBtn');
    const confirmDeleteConfirmBtn = document.getElementById('confirmDeleteConfirmBtn');

    loadStudent();

    async function loadStudent() {
        try {
            const response = await auth.fetchWithAuth(`/api/admin/students/${studentId}`);
            const data = await response.json();
            if (data.success) {
                renderStudent(data.data);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            showToast('Failed to load student details', 'error');
            setTimeout(() => window.location.href = '/dashboard', 2000);
        }
    }

    function renderStudent(student) {
        document.getElementById('studentName').textContent = student.name;
        document.getElementById('studentInitial').textContent = student.name.charAt(0).toUpperCase();
        document.getElementById('studentId').textContent = student.id;
        document.getElementById('studentCourse').textContent = student.course;
        document.getElementById('studentCollege').textContent = student.college;
        document.getElementById('studentAdmissionThrough').textContent = student.admission_through;
        document.getElementById('studentAdmissionThroughDetail').textContent = student.admission_through;
        document.getElementById('studentAdmissionThrough').className = `badge badge-${student.admission_through.toLowerCase()}`;
        
        const createdAt = new Date(student.created_at).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        document.getElementById('studentCreatedAt').textContent = createdAt;

        const updatedAt = new Date(student.updated_at).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        document.getElementById('studentUpdatedAt').textContent = updatedAt;
    }

    editBtn.addEventListener('click', () => openEditModal());
    deleteBtn.addEventListener('click', () => openDeleteModal());
    pdfBtn.addEventListener('click', downloadPdf);

    function openEditModal() {
        auth.fetchWithAuth(`/api/admin/students/${studentId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const student = data.data;
                    document.getElementById('editStudentId').value = student.id;
                    document.getElementById('editName').value = student.name;
                    document.getElementById('editCourse').value = student.course;
                    document.getElementById('editCollege').value = student.college;
                    document.getElementById('editAdmissionThrough').value = student.admission_through;
                    clearEditErrors();
                    editModal.classList.add('active');
                }
            });
    }

    function closeEditModalHandler() {
        editModal.classList.remove('active');
    }

    closeEditModal.addEventListener('click', closeEditModalHandler);
    cancelEditBtn.addEventListener('click', closeEditModalHandler);
    editModal.querySelector('.modal-overlay').addEventListener('click', closeEditModalHandler);

    function clearEditErrors() {
        ['editNameError', 'editCourseError', 'editCollegeError', 'editAdmissionError'].forEach(id => {
            document.getElementById(id).textContent = '';
        });
        ['editName', 'editCourse', 'editCollege', 'editAdmissionThrough'].forEach(id => {
            document.getElementById(id).classList.remove('input-error');
        });
    }

    function showEditError(fieldId, message) {
        document.getElementById(fieldId).textContent = message;
        document.getElementById(fieldId.replace('Error', '')).classList.add('input-error');
    }

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearEditErrors();

        const data = {
            name: document.getElementById('editName').value.trim(),
            course: document.getElementById('editCourse').value.trim(),
            college: document.getElementById('editCollege').value.trim(),
            admission_through: document.getElementById('editAdmissionThrough').value
        };

        let isValid = true;
        if (!data.name) { showEditError('editNameError', 'Name is required'); isValid = false; }
        if (!data.course) { showEditError('editCourseError', 'Course is required'); isValid = false; }
        if (!data.college) { showEditError('editCollegeError', 'College is required'); isValid = false; }
        if (!['KCET', 'NEET', 'NUCAT', 'MANAGEMENT'].includes(data.admission_through)) {
            showEditError('editAdmissionError', 'Invalid admission method'); isValid = false;
        }

        if (!isValid) return;

        const btnText = saveEditBtn.querySelector('.btn-text');
        const btnLoading = saveEditBtn.querySelector('.btn-loading');
        saveEditBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-flex';

        try {
            const response = await auth.fetchWithAuth(`/api/admin/students/${studentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                showToast('Student updated successfully', 'success');
                closeEditModalHandler();
                loadStudent();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            saveEditBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    });

    function openDeleteModal() {
        auth.fetchWithAuth(`/api/admin/students/${studentId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('deleteConfirmName').textContent = data.data.name;
                    deleteConfirmModal.classList.add('active');
                }
            });
    }

    function closeDeleteModal() {
        deleteConfirmModal.classList.remove('active');
    }

    cancelDeleteConfirmBtn.addEventListener('click', closeDeleteModal);
    deleteConfirmModal.querySelector('.modal-overlay').addEventListener('click', closeDeleteModal);

    confirmDeleteConfirmBtn.addEventListener('click', async () => {
        const btnText = confirmDeleteConfirmBtn.querySelector('.btn-text');
        const btnLoading = confirmDeleteConfirmBtn.querySelector('.btn-loading');
        confirmDeleteConfirmBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-flex';

        try {
            const response = await auth.fetchWithAuth(`/api/admin/students/${studentId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            if (result.success) {
                showToast('Student deleted successfully', 'success');
                closeDeleteModal();
                setTimeout(() => window.location.href = '/dashboard', 1000);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            confirmDeleteConfirmBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    });

    async function downloadPdf() {
        const originalText = pdfBtn.innerHTML;
        pdfBtn.innerHTML = '<span class="spinner"></span> Generating...';
        pdfBtn.disabled = true;

        try {
            const response = await auth.fetchWithAuth(`/api/admin/students/${studentId}/pdf`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `student_${document.getElementById('studentName').textContent.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showToast('PDF downloaded successfully', 'success');
        } catch (error) {
            showToast('Failed to generate PDF', 'error');
        } finally {
            pdfBtn.innerHTML = originalText;
            pdfBtn.disabled = false;
        }
    }

    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
            error: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
            warning: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            info: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>'
        };

        toast.innerHTML = `
            ${icons[type]}
            <span class="toast-message">${message}</span>
            <button class="toast-close">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        `;

        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'toastIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
});