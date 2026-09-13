document.addEventListener('DOMContentLoaded', () => {
    auth.redirectIfNotAuthenticated();

    const user = auth.getUser();
    if (!user) {
        fetchCurrentUser();
    } else {
        updateUserUI(user);
    }

    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const overlay = document.getElementById('sidebarOverlay');
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    const logoutBtn = document.getElementById('logoutBtn');

    let currentPage = 'dashboard';
    let studentsPage = 1;
    let studentsLimit = 50;
    let currentSearch = '';
    let currentFilter = '';
    let currentBatchFilter = '';
    let currentSortBy = 'created_at';
    let currentSortOrder = 1;
    let deleteStudentId = null;
    let editStudentId = null;
    let userToEdit = null;

    function fetchCurrentUser() {
        auth.fetchWithAuth('/api/admin/users')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data.users.length > 0) {
                    const currentUser = data.data.users.find(u => u.username === getUsernameFromToken());
                    if (currentUser) {
                        auth.setUser(currentUser);
                        updateUserUI(currentUser);
                    }
                }
            })
            .catch(() => {});
    }

    function getUsernameFromToken() {
        const token = auth.getToken();
        if (!token) return null;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.sub;
        } catch {
            return null;
        }
    }

    function updateUserUI(user) {
        document.getElementById('userName').textContent = user.username;
        const roleBadge = document.getElementById('userRole');
        roleBadge.textContent = user.role;
        roleBadge.className = `role-badge ${user.role}`;

        const usersNavItem = document.getElementById('usersNavItem');
        if (user.role === 'admin') {
            usersNavItem.style.display = 'block';
        } else {
            usersNavItem.style.display = 'none';
        }
    }

    function showPage(pageName) {
        pages.forEach(page => {
            page.style.display = page.id === `${pageName}Page` ? 'block' : 'none';
        });
        navLinks.forEach(link => {
            link.classList.toggle('active', link.dataset.page === pageName);
        });
        currentPage = pageName;
        sidebar.classList.remove('open');
        overlay.classList.remove('active');

        if (pageName === 'dashboard') {
            loadStats();
        } else if (pageName === 'students') {
            loadStudents();
        } else if (pageName === 'users') {
            loadUsers();
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            showPage(link.dataset.page);
        });
    });

    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    });

    overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
    });

    logoutBtn.addEventListener('click', () => {
        auth.logout();
    });

    async function loadStats() {
        try {
            const response = await auth.fetchWithAuth('/api/admin/students/stats');
            const data = await response.json();
            if (data.success) {
                document.getElementById('statTotal').textContent = data.data.total;
                document.getElementById('statKCET').textContent = data.data.kcet;
                document.getElementById('statNEET').textContent = data.data.neet;
                document.getElementById('statNUCAT').textContent = data.data.nucat;
                document.getElementById('statManagement').textContent = data.data.management;
                document.getElementById('statFTB').textContent = data.data.ftb;
                document.getElementById('statBatch1').textContent = data.data.batch_1;
                document.getElementById('statBatch2').textContent = data.data.batch_2;
                document.getElementById('statBatch3').textContent = data.data.batch_3;
            }
        } catch (error) {
            showToast('Failed to load statistics', 'error');
        }
    }

    async function loadStudents() {
        const tbody = document.getElementById('studentsTableBody');
        const emptyState = document.getElementById('emptyState');
        const table = document.getElementById('studentsTable');
        const pagination = document.getElementById('pagination');

        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">Loading...</td></tr>';
        emptyState.style.display = 'none';
        table.style.display = 'table';
        pagination.style.display = 'flex';

        try {
            const params = new URLSearchParams({
                page: studentsPage,
                limit: studentsLimit,
                sort_by: currentSortBy,
                sort_order: currentSortOrder
            });
            if (currentSearch) params.append('search', currentSearch);
            if (currentFilter) params.append('admission_through', currentFilter);
            if (currentBatchFilter) params.append('batch', currentBatchFilter);

            const response = await auth.fetchWithAuth(`/api/admin/students?${params}`);
            const data = await response.json();

            if (data.success) {
                renderStudents(data.data.students);
                updatePagination(data.data.page, data.data.pages, data.data.total);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            tbody.innerHTML = '';
            table.style.display = 'none';
            pagination.style.display = 'none';
            emptyState.style.display = 'flex';
            emptyState.querySelector('h3').textContent = 'Error loading students';
            emptyState.querySelector('p').textContent = error.message;
            showToast('Failed to load students', 'error');
        }
    }

    function renderStudents(students) {
        const tbody = document.getElementById('studentsTableBody');
        if (students.length === 0) {
            tbody.innerHTML = '';
            document.getElementById('studentsTable').style.display = 'none';
            document.getElementById('pagination').style.display = 'none';
            document.getElementById('emptyState').style.display = 'flex';
            return;
        }

        document.getElementById('studentsTable').style.display = 'table';
        document.getElementById('pagination').style.display = 'flex';
        document.getElementById('emptyState').style.display = 'none';

        tbody.innerHTML = students.map((student, index) => {
            const admissionClass = `badge-${student.admission_through.toLowerCase()}`;
            let batchClass = '';
            if (student.batch === 'FTB') batchClass = 'badge-ftb';
            else if (student.batch === 'Batch - 1') batchClass = 'badge-batch-1';
            else if (student.batch === 'Batch - 2') batchClass = 'badge-batch-2';
            else if (student.batch === 'Batch - 3') batchClass = 'badge-batch-3';
            const createdAt = new Date(student.created_at).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });
            return `
                <tr>
                    <td>${(studentsPage - 1) * studentsLimit + index + 1}</td>
                    <td>${escapeHtml(student.name)}</td>
                    <td><span class="badge ${batchClass}">${escapeHtml(student.batch)}</span></td>
                    <td>${escapeHtml(student.course)}</td>
                    <td>${escapeHtml(student.college)}</td>
                    <td><span class="badge ${admissionClass}">${student.admission_through}</span></td>
                    <td>${createdAt}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn view" data-id="${student.id}" title="View">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                    <circle cx="12" cy="12" r="3"/>
                                </svg>
                            </button>
                            <button class="action-btn edit" data-id="${student.id}" title="Edit">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                </svg>
                            </button>
                            <button class="action-btn delete" data-id="${student.id}" title="Delete">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        tbody.querySelectorAll('.action-btn.view').forEach(btn => {
            btn.addEventListener('click', () => viewStudent(btn.dataset.id));
        });
        tbody.querySelectorAll('.action-btn.edit').forEach(btn => {
            btn.addEventListener('click', () => openEditModal(btn.dataset.id));
        });
        tbody.querySelectorAll('.action-btn.delete').forEach(btn => {
            btn.addEventListener('click', () => openDeleteModal(btn.dataset.id));
        });
    }

    function updatePagination(page, pages, total) {
        document.getElementById('pageInfo').textContent = `Page ${page} of ${pages} (${total} total)`;
        document.getElementById('prevPage').disabled = page <= 1;
        document.getElementById('nextPage').disabled = page >= pages;
    }

    document.getElementById('prevPage').addEventListener('click', () => {
        if (studentsPage > 1) {
            studentsPage--;
            loadStudents();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        studentsPage++;
        loadStudents();
    });

    document.getElementById('refreshBtn').addEventListener('click', loadStats);
    document.getElementById('refreshStudentsBtn').addEventListener('click', () => {
        studentsPage = 1;
        loadStudents();
    });

    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentSearch = e.target.value.trim();
            studentsPage = 1;
            loadStudents();
        }, 300);
    });

    document.getElementById('filterSelect').addEventListener('change', (e) => {
        currentFilter = e.target.value;
        studentsPage = 1;
        loadStudents();
    });

    document.getElementById('batchFilterSelect').addEventListener('change', (e) => {
        currentBatchFilter = e.target.value;
        studentsPage = 1;
        loadStudents();
    });

    document.getElementById('exportAllPdfBtn').addEventListener('click', () => exportPdf());
    document.getElementById('exportFilteredPdfBtn').addEventListener('click', () => exportPdf(currentSearch, currentFilter, currentBatchFilter));

    function exportPdf(search = null, filter = null, batch = null) {
        const btn = search ? document.getElementById('exportFilteredPdfBtn') : document.getElementById('exportAllPdfBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> Generating...';
        btn.disabled = true;

        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (filter) params.append('admission_through', filter);
        if (batch) params.append('batch', batch);

        auth.fetchWithAuth(`/api/admin/students/export/pdf?${params}`)
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401) {
                        auth.logout();
                        return;
                    }
                    if (response.status === 403) {
                        throw new Error('Permission denied');
                    }
                    throw new Error('Failed to generate PDF');
                }
                return response.blob();
            })
            .then(blob => {
                if (!blob) return; // auth.logout already handled redirect
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `student_records_${new Date().toISOString().split('T')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showToast('PDF downloaded successfully', 'success');
            })
            .catch(error => {
                if (error.message !== 'Permission denied' || !error.message.startsWith('Failed to generate')) {
                    showToast(error.message, 'error');
                } else {
                    showToast('Failed to generate PDF', 'error');
                }
            })
            .finally(() => {
                const btn = document.getElementById('exportAllPdfBtn') || document.getElementById('exportFilteredPdfBtn');
                if (btn) {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }
            });
    }

    function viewStudent(id) {
        window.location.href = `/student-details?id=${id}`;
    }

    const editModal = document.getElementById('editModal');
    const closeEditModal = document.getElementById('closeEditModal');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const editForm = document.getElementById('editForm');
    const saveEditBtn = document.getElementById('saveEditBtn');

    function openEditModal(id) {
        editStudentId = id;
        auth.fetchWithAuth(`/api/admin/students/${id}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const student = data.data;
                    document.getElementById('editStudentId').value = student.id;
                    document.getElementById('editName').value = student.name;
                    document.getElementById('editBatch').value = student.batch;
                    document.getElementById('editCourse').value = student.course;
                    document.getElementById('editCollege').value = student.college;
                    document.getElementById('editAdmissionThrough').value = student.admission_through;
                    clearEditErrors();
                    editModal.classList.add('active');
                }
            })
            .catch(() => showToast('Failed to load student details', 'error'));
    }

    function closeEditModalHandler() {
        editModal.classList.remove('active');
        editStudentId = null;
    }

    closeEditModal.addEventListener('click', closeEditModalHandler);
    cancelEditBtn.addEventListener('click', closeEditModalHandler);
    editModal.querySelector('.modal-overlay').addEventListener('click', closeEditModalHandler);

    function clearEditErrors() {
        ['editNameError', 'editBatchError', 'editCourseError', 'editCollegeError', 'editAdmissionError'].forEach(id => {
            document.getElementById(id).textContent = '';
        });
        ['editName', 'editBatch', 'editCourse', 'editCollege', 'editAdmissionThrough'].forEach(id => {
            document.getElementById(id).classList.remove('input-error');
        });
    }

    function showEditError(fieldId, message) {
        document.getElementById(fieldId).textContent = message;
        document.getElementById(fieldId.replace('Error', '')).classList.add('input-error');
    }

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!editStudentId) return;

        clearEditErrors();

        const data = {
            name: document.getElementById('editName').value.trim(),
            batch: document.getElementById('editBatch').value,
            course: document.getElementById('editCourse').value.trim(),
            college: document.getElementById('editCollege').value.trim(),
            admission_through: document.getElementById('editAdmissionThrough').value
        };

        let isValid = true;
        if (!data.name) { showEditError('editNameError', 'Name is required'); isValid = false; }
        if (!data.batch) { showEditError('editBatchError', 'Batch is required'); isValid = false; }
        if (!['FTB', 'Batch - 1', 'Batch - 2', 'Batch - 3'].includes(data.batch)) { showEditError('editBatchError', 'Invalid batch selection'); isValid = false; }
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
            const response = await auth.fetchWithAuth(`/api/admin/students/${editStudentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                showToast('Student updated successfully', 'success');
                closeEditModalHandler();
                loadStudents();
                if (currentPage === 'dashboard') loadStats();
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

    const deleteModal = document.getElementById('deleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    function openDeleteModal(id) {
        deleteStudentId = id;
        auth.fetchWithAuth(`/api/admin/students/${id}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('deleteStudentName').textContent = data.data.name;
                    deleteModal.classList.add('active');
                }
            });
    }

    function closeDeleteModal() {
        deleteModal.classList.remove('active');
        deleteStudentId = null;
    }

    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    deleteModal.querySelector('.modal-overlay').addEventListener('click', closeDeleteModal);

    confirmDeleteBtn.addEventListener('click', async () => {
        if (!deleteStudentId) return;

        const btnText = confirmDeleteBtn.querySelector('.btn-text');
        const btnLoading = confirmDeleteBtn.querySelector('.btn-loading');
        confirmDeleteBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-flex';

        try {
            const response = await auth.fetchWithAuth(`/api/admin/students/${deleteStudentId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            if (result.success) {
                showToast('Student deleted successfully', 'success');
                closeDeleteModal();
                loadStudents();
                if (currentPage === 'dashboard') loadStats();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            confirmDeleteBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    });

    async function loadUsers() {
        if (!auth.getUser() || auth.getUser().role !== 'admin') return;

        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px;">Loading...</td></tr>';

        try {
            const response = await auth.fetchWithAuth('/api/auth/users');
            const data = await response.json();
            if (data.success) {
                renderUsers(data.data.users);
            }
        } catch (error) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--danger);">Failed to load users</td></tr>';
        }
    }

    function renderUsers(users) {
        const tbody = document.getElementById('usersTableBody');
        const currentUsername = auth.getUser()?.username;
        tbody.innerHTML = users.map(user => {
            const createdAt = new Date(user.created_at).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric'
            });
            const isCurrent = user.username === currentUsername;
            return `
                <tr>
                    <td>${escapeHtml(user.username)}${isCurrent ? ' (you)' : ''}</td>
                    <td><span class="badge badge-${user.role === 'admin' ? 'management' : 'kcet'}">${user.role}</span></td>
                    <td><span class="badge ${user.is_active ? 'badge-neet' : 'badge-management'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>${createdAt}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn edit" data-id="${user.id}" ${isCurrent ? 'disabled' : ''} title="Edit">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                </svg>
                            </button>
                            <button class="action-btn delete" data-id="${user.id}" ${isCurrent ? 'disabled' : ''} title="Delete">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        tbody.querySelectorAll('.action-btn.edit:not(:disabled)').forEach(btn => {
            btn.addEventListener('click', () => openUserModal(btn.dataset.id));
        });
        tbody.querySelectorAll('.action-btn.delete:not(:disabled)').forEach(btn => {
            btn.addEventListener('click', () => openDeleteUserModal(btn.dataset.id));
        });
    }

    const userModal = document.getElementById('userModal');
    const closeUserModal = document.getElementById('closeUserModal');
    const cancelUserBtn = document.getElementById('cancelUserBtn');
    const userForm = document.getElementById('userForm');
    const saveUserBtn = document.getElementById('saveUserBtn');
    const addUserBtn = document.getElementById('addUserBtn');
    const userModalTitle = document.getElementById('userModalTitle');
    const userIdInput = document.getElementById('userId');
    const userActiveGroup = document.getElementById('userActiveGroup');
    const userPasswordInput = document.getElementById('userPassword');
    const passwordHint = document.getElementById('passwordHint');
    const toggleUserPassword = document.getElementById('toggleUserPassword');
    const userEyeOpen = toggleUserPassword.querySelector('.eye-open');
    const userEyeClosed = toggleUserPassword.querySelector('.eye-closed');

    function openUserModal(id = null) {
        userToEdit = id;
        clearUserErrors();
        userForm.reset();

        if (id) {
            userModalTitle.textContent = 'Edit User';
            userIdInput.value = id;
            userActiveGroup.style.display = 'block';
            userPasswordInput.required = false;
            passwordHint.textContent = 'Leave blank to keep current password';
        } else {
            userModalTitle.textContent = 'Add User';
            userIdInput.value = '';
            userActiveGroup.style.display = 'none';
            userPasswordInput.required = true;
            passwordHint.textContent = 'Minimum 6 characters';
        }
        userModal.classList.add('active');
    }

    function closeUserModalHandler() {
        userModal.classList.remove('active');
        userToEdit = null;
    }

    closeUserModal.addEventListener('click', closeUserModalHandler);
    cancelUserBtn.addEventListener('click', closeUserModalHandler);
    userModal.querySelector('.modal-overlay').addEventListener('click', closeUserModalHandler);

    toggleUserPassword.addEventListener('click', () => {
        const isPassword = userPasswordInput.type === 'password';
        userPasswordInput.type = isPassword ? 'text' : 'password';
        userEyeOpen.style.display = isPassword ? 'none' : 'block';
        userEyeClosed.style.display = isPassword ? 'block' : 'none';
    });

    function clearUserErrors() {
        ['userUsernameError', 'userPasswordError'].forEach(id => document.getElementById(id).textContent = '');
        ['userUsername', 'userPassword'].forEach(id => document.getElementById(id).classList.remove('input-error'));
    }

    function showUserError(fieldId, message) {
        document.getElementById(fieldId).textContent = message;
        document.getElementById(fieldId.replace('Error', '')).classList.add('input-error');
    }

    userForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearUserErrors();

        const data = {
            username: document.getElementById('userUsername').value.trim(),
            password: document.getElementById('userPassword').value,
            role: document.getElementById('userRole').value,
            is_active: document.getElementById('userActive').checked
        };

        let isValid = true;
        if (!data.username) { showUserError('userUsernameError', 'Username is required'); isValid = false; }
        if (!userToEdit && !data.password) { showUserError('userPasswordError', 'Password is required'); isValid = false; }
        if (data.password && data.password.length < 6) { showUserError('userPasswordError', 'Password must be at least 6 characters'); isValid = false; }

        if (!isValid) return;

        if (userToEdit && !data.password) {
            delete data.password;
        }

        const btnText = saveUserBtn.querySelector('.btn-text');
        const btnLoading = saveUserBtn.querySelector('.btn-loading');
        saveUserBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-flex';

        try {
            const url = userToEdit ? `/api/auth/users/${userToEdit}` : '/api/auth/users';
            const method = userToEdit ? 'PUT' : 'POST';
            const response = await auth.fetchWithAuth(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                showToast(userToEdit ? 'User updated successfully' : 'User created successfully', 'success');
                closeUserModalHandler();
                loadUsers();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            saveUserBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    });

    function openDeleteUserModal(id) {
        if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            deleteUser(id);
        }
    }

    async function deleteUser(id) {
        try {
            const response = await auth.fetchWithAuth(`/api/auth/users/${id}`, { method: 'DELETE' });
            const result = await response.json();
            if (result.success) {
                showToast('User deleted successfully', 'success');
                loadUsers();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            showToast(error.message, 'error');
        }
    }

    addUserBtn.addEventListener('click', () => openUserModal());

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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
            <span class="toast-message">${escapeHtml(message)}</span>
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

    showPage('dashboard');
});