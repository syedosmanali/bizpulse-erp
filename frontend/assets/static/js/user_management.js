/**
 * User Management JavaScript
 * Handles all user management operations
 */

let users = [];
let roles = [];
let currentEditUserId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 User Management Dashboard Loading...');
    initializeSystem();
    loadUsers();
    loadRoles();
    setupEventListeners();
});

async function initializeSystem() {
    try {
        console.log('🔧 Initializing user management system...');
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        const response = await fetch('/api/user-management/initialize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        const data = await response.json();
        console.log('Initialize response:', data);
        
        if (!data.success) {
            console.warn('System initialization warning:', data.error);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.warn('System initialization timed out');
        } else {
            console.error('Error initializing system:', error);
        }
    }
}

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchUsers').addEventListener('input', filterUsers);
    document.getElementById('filterRole').addEventListener('change', filterUsers);
    document.getElementById('filterStatus').addEventListener('change', filterUsers);
}

// Section Management
function showSection(section) {
    console.log(`🔄 showSection called with: ${section}`);
    
    // Hide all sections
    document.getElementById('users-section').style.display = 'none';
    document.getElementById('roles-section').style.display = 'none';
    document.getElementById('permissions-section').style.display = 'none';
    document.getElementById('activity-section').style.display = 'none';
    
    // Show selected section
    const sectionElement = document.getElementById(section + '-section');
    if (sectionElement) {
        sectionElement.style.display = 'block';
        console.log(`✅ Showing ${section}-section`);
    } else {
        console.error(`❌ Section element not found: ${section}-section`);
    }
    
    // Update active nav
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Load section data
    if (section === 'activity') {
        loadActivity();
    } else if (section === 'permissions') {
        console.log('📋 Loading permissions...');
        loadPermissions();
    }
}

// User Management Functions
async function loadUsers() {
    try {
        console.log('🔍 Loading users...');
        showLoading('usersContainer');
        
        const response = await fetch('/api/user-management/users');
        console.log('Users API response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Users data received:', data);
        
        if (data.success) {
            users = data.users || [];
            displayUsers(users);
            console.log(`✅ Loaded ${users.length} users`);
        } else {
            console.error('API returned error:', data.error);
            showError('Failed to load users: ' + (data.error || 'Unknown error'));
            displayUsers([]); // Show empty state
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showError('Failed to load users: ' + error.message);
        displayUsers([]); // Show empty state
    }
}

function displayUsers(userList) {
    const container = document.getElementById('usersContainer');
    
    if (!userList || userList.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No users found</h5>
                    <p class="text-muted">Create your first user to get started</p>
                    <button class="btn btn-primary" onclick="showCreateUserModal()">
                        <i class="fas fa-plus me-2"></i>Add New User
                    </button>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = userList.map(user => `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card user-card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">${user.full_name || 'Unknown User'}</h6>
                        <span class="badge ${user.status === 'active' ? 'bg-success' : 'bg-danger'} status-badge">
                            ${user.status || 'unknown'}
                        </span>
                    </div>
                    
                    <p class="text-muted small mb-1">
                        <i class="fas fa-user me-1"></i>${user.username || 'No username'}
                    </p>
                    
                    <p class="text-muted small mb-1">
                        <i class="fas fa-user-tag me-1"></i>${user.role_name || 'No Role'}
                    </p>
                    
                    <p class="text-muted small mb-1">
                        <i class="fas fa-phone me-1"></i>${user.mobile || 'No phone'}
                    </p>
                    
                    ${user.email ? `
                        <p class="text-muted small mb-1">
                            <i class="fas fa-envelope me-1"></i>${user.email}
                        </p>
                    ` : ''}
                    
                    ${user.department ? `
                        <p class="text-muted small mb-2">
                            <i class="fas fa-building me-1"></i>${user.department}
                        </p>
                    ` : ''}
                    
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <small class="text-muted">
                            ${user.last_login ? 'Last: ' + formatDate(user.last_login) : 'Never logged in'}
                        </small>
                        
                        <div class="btn-group">
                            <button class="btn btn-outline-info btn-action" onclick="viewUser('${user.id}')" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-primary btn-action" onclick="editUser('${user.id}')" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-warning btn-action" onclick="resetPassword('${user.id}')" title="Reset Password">
                                <i class="fas fa-key"></i>
                            </button>
                            <button class="btn btn-outline-${user.status === 'active' ? 'danger' : 'success'} btn-action" 
                                    onclick="${user.status === 'active' ? 'deactivateUser' : 'activateUser'}('${user.id}')" 
                                    title="${user.status === 'active' ? 'Deactivate' : 'Activate'}">
                                <i class="fas fa-${user.status === 'active' ? 'ban' : 'check'}"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-action" onclick="deleteUser('${user.id}')" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function filterUsers() {
    const searchTerm = document.getElementById('searchUsers').value.toLowerCase();
    const roleFilter = document.getElementById('filterRole').value;
    const statusFilter = document.getElementById('filterStatus').value;
    
    let filteredUsers = users.filter(user => {
        const matchesSearch = user.full_name.toLowerCase().includes(searchTerm) ||
                            user.username.toLowerCase().includes(searchTerm) ||
                            user.mobile.includes(searchTerm);
        
        const matchesRole = !roleFilter || user.role_name === roleFilter;
        const matchesStatus = !statusFilter || user.status === statusFilter;
        
        return matchesSearch && matchesRole && matchesStatus;
    });
    
    displayUsers(filteredUsers);
}

// Role Management Functions
async function loadRoles() {
    try {
        console.log('🔄 Loading roles...');
        const response = await fetch('/api/user-management/roles');
        console.log('Roles API response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Roles data received:', data);
        
        if (data.success) {
            roles = data.roles || [];
            displayRoles(roles);
            populateRoleSelects();
            console.log(`✅ Loaded ${roles.length} roles`);
        } else {
            console.error('Failed to load roles:', data.error);
            showError('Failed to load roles: ' + (data.error || 'Unknown error'));
            roles = [];
            displayRoles([]);
            populateRoleSelects();
        }
    } catch (error) {
        console.error('Error loading roles:', error);
        showError('Failed to load roles: ' + error.message);
        roles = [];
        displayRoles([]);
        populateRoleSelects();
    }
}

function displayRoles(roleList) {
    const container = document.getElementById('rolesContainer');
    
    if (roleList.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-user-tag fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No roles found</h5>
                    <p class="text-muted">Create your first custom role to get started</p>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = roleList.map(role => `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card role-card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title">${role.display_name}</h6>
                        <span class="badge ${role.is_system_role ? 'bg-primary' : 'bg-success'}">
                            ${role.is_system_role ? 'System' : 'Custom'}
                        </span>
                    </div>
                    
                    <p class="text-muted small mb-2">${role.role_name}</p>
                    
                    <div class="permissions-list mb-3">
                        ${Object.keys(role.permissions).length > 0 ? 
                            Object.keys(role.permissions).map(module => `
                                <small class="badge bg-light text-dark me-1 mb-1">
                                    ${module}: ${role.permissions[module].join(', ')}
                                </small>
                            `).join('') : 
                            '<small class="text-muted">No permissions defined</small>'
                        }
                    </div>
                    
                    ${!role.is_system_role ? `
                        <div class="mt-auto">
                            <button class="btn btn-outline-primary btn-sm" onclick="editRole('${role.id}')">
                                <i class="fas fa-edit me-1"></i>Edit
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function populateRoleSelects() {
    const selects = document.querySelectorAll('select[name="role_id"]');
    
    selects.forEach(select => {
        select.innerHTML = '<option value="">Select Role</option>' +
            roles.map(role => `<option value="${role.id}">${role.display_name}</option>`).join('');
    });
    
    // Populate filter dropdown
    const filterSelect = document.getElementById('filterRole');
    filterSelect.innerHTML = '<option value="">All Roles</option>' +
        roles.map(role => `<option value="${role.display_name}">${role.display_name}</option>`).join('');
}

// User CRUD Operations
function showCreateUserModal() {
    document.getElementById('createUserForm').reset();
    new bootstrap.Modal(document.getElementById('createUserModal')).show();
}

function viewUser(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;
    
    // Populate view modal
    document.getElementById('view-full-name').textContent = user.full_name || 'Not provided';
    document.getElementById('view-username').textContent = user.username || 'Not provided';
    document.getElementById('view-password').textContent = user.temp_password || 'Not available';
    document.getElementById('view-email').textContent = user.email || 'Not provided';
    document.getElementById('view-mobile').textContent = user.mobile || 'Not provided';
    document.getElementById('view-role').textContent = user.role_name || 'Not assigned';
    document.getElementById('view-department').textContent = user.department || 'Not assigned';
    document.getElementById('view-last-login').textContent = user.last_login ? formatDate(user.last_login) : 'Never logged in';
    document.getElementById('view-created').textContent = user.created_at ? formatDate(user.created_at) : 'Unknown';
    
    // Set status badge
    const statusElement = document.getElementById('view-status');
    statusElement.textContent = user.status || 'unknown';
    statusElement.className = `badge ${user.status === 'active' ? 'bg-success' : 'bg-danger'}`;
    
    // Reset password visibility
    document.getElementById('view-password').style.display = 'none';
    document.getElementById('password-icon').className = 'fas fa-eye';
    document.querySelector('#viewUserModal button[onclick="togglePassword()"]').innerHTML = '<i class="fas fa-eye" id="password-icon"></i> Show Password';
    
    new bootstrap.Modal(document.getElementById('viewUserModal')).show();
}

function togglePassword() {
    const passwordElement = document.getElementById('view-password');
    const iconElement = document.getElementById('password-icon');
    const buttonElement = document.querySelector('#viewUserModal button[onclick="togglePassword()"]');
    
    if (passwordElement.style.display === 'none') {
        passwordElement.style.display = 'inline';
        iconElement.className = 'fas fa-eye-slash';
        buttonElement.innerHTML = '<i class="fas fa-eye-slash" id="password-icon"></i> Hide Password';
    } else {
        passwordElement.style.display = 'none';
        iconElement.className = 'fas fa-eye';
        buttonElement.innerHTML = '<i class="fas fa-eye" id="password-icon"></i> Show Password';
    }
}

async function createUser() {
    const form = document.getElementById('createUserForm');
    const formData = new FormData(form);
    const userData = Object.fromEntries(formData.entries());
    
    console.log('Creating user with data:', userData);
    
    // Validate required fields
    if (!userData.full_name || !userData.mobile || !userData.username || !userData.role_id) {
        showError('Please fill in all required fields');
        return;
    }
    
    try {
        const response = await fetch('/api/user-management/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        console.log('Create user response:', data);
        
        if (data.success) {
            showSuccess(`User created successfully! Username: ${data.username}, Password: ${data.temp_password}`);
            bootstrap.Modal.getInstance(document.getElementById('createUserModal')).hide();
            loadUsers();
        } else {
            if (data.errors) {
                showError('Validation errors: ' + data.errors.join(', '));
            } else {
                showError('Failed to create user: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Error creating user:', error);
        showError('Failed to create user: ' + error.message);
    }
}

function editUser(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;
    
    currentEditUserId = userId;
    const form = document.getElementById('editUserForm');
    
    // Populate form
    form.querySelector('input[name="user_id"]').value = user.id;
    form.querySelector('input[name="full_name"]').value = user.full_name;
    form.querySelector('input[name="mobile"]').value = user.mobile;
    form.querySelector('input[name="email"]').value = user.email || '';
    form.querySelector('input[name="department"]').value = user.department || '';
    form.querySelector('select[name="status"]').value = user.status;
    
    // Set role
    const roleSelect = form.querySelector('select[name="role_id"]');
    const userRole = roles.find(r => r.display_name === user.role_name);
    if (userRole) {
        roleSelect.value = userRole.id;
    }
    
    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

async function updateUser() {
    const form = document.getElementById('editUserForm');
    const formData = new FormData(form);
    const userData = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`/api/user-management/users/${currentEditUserId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('User updated successfully!');
            bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
            loadUsers();
        } else {
            if (data.errors) {
                showError('Validation errors: ' + data.errors.join(', '));
            } else {
                showError('Failed to update user: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Error updating user:', error);
        showError('Failed to update user');
    }
}

async function resetPassword(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;
    
    // Show reset password modal
    document.getElementById('reset-user-id').value = userId;
    document.getElementById('reset-user-name').textContent = `${user.full_name} (${user.username})`;
    document.getElementById('resetToUsername').checked = true;
    document.getElementById('customPasswordDiv').style.display = 'none';
    document.getElementById('customPassword').value = '';
    
    new bootstrap.Modal(document.getElementById('resetPasswordModal')).show();
}

async function confirmPasswordReset() {
    const userId = document.getElementById('reset-user-id').value;
    const resetOption = document.querySelector('input[name="resetOption"]:checked').value;
    const customPassword = document.getElementById('customPassword').value;
    
    let newPassword;
    if (resetOption === 'username') {
        const user = users.find(u => u.id === userId);
        newPassword = user.username;
    } else {
        if (!customPassword.trim()) {
            showError('Please enter a custom password');
            return;
        }
        newPassword = customPassword.trim();
    }
    
    try {
        const response = await fetch(`/api/user-management/users/${userId}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ new_password: newPassword })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Password reset successfully! New password: ${newPassword}`);
            bootstrap.Modal.getInstance(document.getElementById('resetPasswordModal')).hide();
            loadUsers();
        } else {
            showError('Failed to reset password: ' + data.error);
        }
    } catch (error) {
        console.error('Error resetting password:', error);
        showError('Failed to reset password: ' + error.message);
    }
}

// Add event listeners for password reset modal
document.addEventListener('DOMContentLoaded', function() {
    // Show/hide custom password field
    document.querySelectorAll('input[name="resetOption"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const customDiv = document.getElementById('customPasswordDiv');
            if (this.value === 'custom') {
                customDiv.style.display = 'block';
            } else {
                customDiv.style.display = 'none';
            }
        });
    });
});

async function deactivateUser(userId) {
    if (!confirm('Are you sure you want to deactivate this user?')) return;
    
    try {
        const response = await fetch(`/api/user-management/users/${userId}/deactivate`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('User deactivated successfully!');
            loadUsers();
        } else {
            showError('Failed to deactivate user: ' + data.error);
        }
    } catch (error) {
        console.error('Error deactivating user:', error);
        showError('Failed to deactivate user');
    }
}

async function activateUser(userId) {
    try {
        const response = await fetch(`/api/user-management/users/${userId}/activate`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('User activated successfully!');
            loadUsers();
        } else {
            showError('Failed to activate user: ' + data.error);
        }
    } catch (error) {
        console.error('Error activating user:', error);
        showError('Failed to activate user');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;
    
    try {
        const response = await fetch(`/api/user-management/users/${userId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('User deleted successfully!');
            loadUsers();
        } else {
            showError('Failed to delete user: ' + data.error);
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showError('Failed to delete user');
    }
}

// Role Management
function showCreateRoleModal() {
    document.getElementById('createRoleForm').reset();
    new bootstrap.Modal(document.getElementById('createRoleModal')).show();
}

async function createRole() {
    const form = document.getElementById('createRoleForm');
    const formData = new FormData(form);
    
    const roleData = {
        role_name: formData.get('role_name'),
        display_name: formData.get('display_name'),
        permissions: {}
    };
    
    // Build permissions object
    const permissions = formData.getAll('permissions');
    permissions.forEach(perm => {
        const [module, action] = perm.split('.');
        if (!roleData.permissions[module]) {
            roleData.permissions[module] = [];
        }
        roleData.permissions[module].push(action);
    });
    
    try {
        const response = await fetch('/api/user-management/roles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(roleData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Role created successfully!');
            bootstrap.Modal.getInstance(document.getElementById('createRoleModal')).hide();
            loadRoles();
        } else {
            showError('Failed to create role: ' + data.error);
        }
    } catch (error) {
        console.error('Error creating role:', error);
        showError('Failed to create role');
    }
}

// Activity Log
async function loadActivity() {
    try {
        showLoading('activityContainer');
        
        const response = await fetch('/api/user-management/activity');
        const data = await response.json();
        
        if (data.success) {
            displayActivity(data.activities);
        } else {
            showError('Failed to load activity: ' + data.error);
        }
    } catch (error) {
        console.error('Error loading activity:', error);
        showError('Failed to load activity');
    }
}

function displayActivity(activities) {
    const container = document.getElementById('activityContainer');
    
    if (activities.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-history fa-2x text-muted mb-2"></i>
                <p class="text-muted">No activity logs found</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = activities.map(activity => `
        <div class="activity-item mb-3 pb-3">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${activity.user_name || 'Unknown User'}</strong>
                    <span class="text-muted">performed</span>
                    <strong>${activity.action}</strong>
                    <span class="text-muted">in</span>
                    <strong>${activity.module}</strong>
                </div>
                <small class="text-muted">${formatDate(activity.timestamp)}</small>
            </div>
            ${activity.details ? `<p class="text-muted small mb-0 mt-1">${activity.details}</p>` : ''}
        </div>
    `).join('');
}

// Utility Functions
function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
}

function showSuccess(message) {
    // Create and show success toast
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-check-circle me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toast);
    });
}

function showError(message) {
    // Create and show error toast
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-exclamation-circle me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toast);
    });
}

function formatDate(dateString) {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}


// ==================== PERMISSIONS MANAGEMENT ====================

const AVAILABLE_MODULES = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'billing', label: 'Billing' },
    { key: 'sales', label: 'Sales' },
    { key: 'products', label: 'Products' },
    { key: 'customers', label: 'Customers' },
    { key: 'inventory', label: 'Inventory' },
    { key: 'reports', label: 'Reports' },
    { key: 'credit', label: 'Credit' },
    { key: 'invoices', label: 'Invoices' },
    { key: 'eway', label: 'E-Way Bills' },
    { key: 'settings', label: 'Settings' },
    { key: 'user_management', label: 'User Management' },
    { key: 'desktop_app', label: 'Desktop App' }
];

async function loadPermissions() {
    try {
        console.log('🔐 Loading permissions...');
        showLoading('permissionsTableBody');
        
        const response = await fetch('/api/user-management/permissions', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('📊 Response status:', response.status);
        
        if (response.status === 401) {
            // Unauthorized - session expired
            showError('Session expired. Please refresh the page and login again.');
            displayPermissions([]);
            return;
        }
        
        if (response.status === 404) {
            // Endpoint not found - server might need restart
            showError('Server endpoint not found. Please restart the server.');
            displayPermissions([]);
            return;
        }
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Response error:', errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📋 Permissions data:', data);
        
        if (data.success) {
            console.log(`✅ Loaded ${data.permissions.length} users`);
            displayPermissions(data.permissions);
        } else {
            console.error('❌ API returned error:', data.error);
            showError('Failed to load permissions: ' + data.error);
            displayPermissions([]); // Show empty state
        }
    } catch (error) {
        console.error('❌ Error loading permissions:', error);
        showError('Failed to load permissions: ' + error.message);
        displayPermissions([]); // Show empty state
    }
}

function displayPermissions(permissionsData) {
    const thead = document.getElementById('permissionsTableHead');
    const tbody = document.getElementById('permissionsTableBody');
    
    if (!permissionsData || permissionsData.length === 0) {
        thead.innerHTML = `
            <tr>
                <th style="width: 200px;">Module</th>
            </tr>
        `;
        tbody.innerHTML = `
            <tr>
                <td class="text-center py-4">
                    <i class="fas fa-shield-alt fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No users found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    // Build table header with user names as columns
    thead.innerHTML = `
        <tr>
            <th style="width: 200px; position: sticky; left: 0; background: #f8f9fa; z-index: 10;">Module</th>
            ${permissionsData.map(user => `
                <th class="text-center" style="min-width: 120px;">
                    <div style="font-weight: 600; color: #333;">${user.full_name}</div>
                    <div style="font-size: 0.8rem; color: #666;">${user.username}</div>
                </th>
            `).join('')}
        </tr>
    `;
    
    // Build table body with modules as rows
    tbody.innerHTML = AVAILABLE_MODULES.map(module => {
        return `
            <tr>
                <td style="font-weight: 600; position: sticky; left: 0; background: white; z-index: 5;">
                    ${module.label}
                </td>
                ${permissionsData.map(user => {
                    const userPermissions = user.permissions || {};
                    return `
                        <td class="text-center">
                            <div class="form-check form-switch d-flex justify-content-center">
                                <input 
                                    class="form-check-input" 
                                    type="checkbox" 
                                    id="perm_${user.id}_${module.key}"
                                    ${userPermissions[module.key] ? 'checked' : ''}
                                    onchange="togglePermission('${user.id}', '${module.key}', this.checked)"
                                    style="cursor: pointer; width: 40px; height: 20px;">
                            </div>
                        </td>
                    `;
                }).join('')}
            </tr>
        `;
    }).join('');
}

async function togglePermission(userId, moduleKey, enabled) {
    try {
        const response = await fetch('/api/user-management/permissions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                module: moduleKey,
                enabled: enabled
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Permission ${enabled ? 'enabled' : 'disabled'} successfully`);
        } else {
            showError('Failed to update permission: ' + data.error);
            // Revert checkbox state
            document.getElementById(`perm_${userId}_${moduleKey}`).checked = !enabled;
        }
    } catch (error) {
        console.error('Error updating permission:', error);
        showError('Failed to update permission');
        // Revert checkbox state
        document.getElementById(`perm_${userId}_${moduleKey}`).checked = !enabled;
    }
}
