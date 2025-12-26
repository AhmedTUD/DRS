/**
 * Admin Users Management System
 * Simple and efficient admin user management
 */

class AdminUsersManager {
    constructor() {
        this.admins = [];
        this.currentAdmin = null;
        this.confirmCallback = null;
        
        this.initializeEventListeners();
        this.loadAdmins();
        
        console.log('✅ Admin Users Manager initialized');
    }
    
    initializeEventListeners() {
        // Main actions
        document.getElementById('createAdminBtn').addEventListener('click', this.showCreateAdminModal.bind(this));
        document.getElementById('saveAdminBtn').addEventListener('click', this.saveAdmin.bind(this));
        document.getElementById('searchAdmins').addEventListener('input', this.filterAdmins.bind(this));
        
        // Confirmation
        document.getElementById('confirmActionBtn').addEventListener('click', this.executeConfirmAction.bind(this));
        
        console.log('✅ Event listeners initialized');
    }
    
    async loadAdmins() {
        try {
            const response = await fetch('/admin/api/admin-users');
            if (response.ok) {
                this.admins = await response.json();
                document.getElementById('loadingAdmins').style.display = 'none';
                document.getElementById('adminsList').style.display = 'block';
                this.renderAdmins();
                this.updateAdminCount();
                console.log(`✅ Loaded ${this.admins.length} administrators`);
            } else {
                throw new Error('Failed to load administrators');
            }
        } catch (error) {
            console.error('Error loading administrators:', error);
            this.showError('Failed to load administrators');
            document.getElementById('loadingAdmins').innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <p class="text-danger">Failed to load administrators</p>
                    <button class="btn btn-outline-warning" onclick="adminUsersManager.loadAdmins()">
                        <i class="fas fa-redo me-2"></i>Retry
                    </button>
                </div>
            `;   
     }
    }
    
    renderAdmins() {
        const container = document.getElementById('adminsList');
        
        if (this.admins.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-users-cog fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No administrators found</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.admins.map(admin => `
            <div class="admin-card" data-admin-id="${admin.id}">
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h5 class="card-title mb-1">
                                    <i class="fas fa-user-shield text-primary me-2"></i>
                                    ${admin.employee_name}
                                    ${admin.id === 1 ? '<span class="badge bg-warning ms-2">Super Admin</span>' : ''}
                                </h5>
                                <p class="card-text text-muted mb-1">
                                    <strong>Code:</strong> ${admin.employee_code || 'N/A'}
                                </p>
                                <p class="card-text text-muted mb-0">
                                    <strong>Username:</strong> ${admin.username}
                                </p>
                            </div>
                            <div class="col-md-4 text-end">
                                <div class="btn-group" role="group">
                                    <button class="btn btn-outline-primary btn-sm" 
                                            onclick="adminUsersManager.editAdmin(${admin.id})"
                                            title="Edit Administrator">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    ${admin.id !== 1 ? `
                                        <button class="btn btn-outline-danger btn-sm" 
                                                onclick="adminUsersManager.confirmDeleteAdmin(${admin.id})"
                                                title="Delete Administrator">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    updateAdminCount() {
        document.getElementById('adminCount').textContent = this.admins.length;
    }
    
    filterAdmins() {
        const searchTerm = document.getElementById('searchAdmins').value.toLowerCase();
        const adminCards = document.querySelectorAll('.admin-card');
        
        adminCards.forEach(card => {
            const adminId = parseInt(card.dataset.adminId);
            const admin = this.admins.find(a => a.id === adminId);
            
            if (admin) {
                const searchText = `${admin.employee_name} ${admin.employee_code} ${admin.username}`.toLowerCase();
                const matches = searchText.includes(searchTerm);
                card.style.display = matches ? 'block' : 'none';
            }
        });
    }
    
    showCreateAdminModal() {
        this.currentAdmin = null;
        document.getElementById('adminModalTitle').textContent = 'Create New Administrator';
        document.getElementById('adminForm').reset();
        document.getElementById('passwordGroup').style.display = 'block';
        document.getElementById('password').required = true;
        
        const modal = new bootstrap.Modal(document.getElementById('adminModal'));
        modal.show();
    }
    
    editAdmin(adminId) {
        this.currentAdmin = this.admins.find(admin => admin.id === adminId);
        if (!this.currentAdmin) return;
        
        document.getElementById('adminModalTitle').textContent = 'Edit Administrator';
        document.getElementById('employeeName').value = this.currentAdmin.employee_name;
        document.getElementById('employeeCode').value = this.currentAdmin.employee_code || '';
        document.getElementById('username').value = this.currentAdmin.username;
        document.getElementById('passwordGroup').style.display = 'block';
        document.getElementById('password').required = false;
        document.getElementById('password').value = '';
        
        const modal = new bootstrap.Modal(document.getElementById('adminModal'));
        modal.show();
    }
    
    async saveAdmin() {
        const form = document.getElementById('adminForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const formData = new FormData(form);
        const adminData = {
            employee_name: formData.get('employee_name'),
            employee_code: formData.get('employee_code'),
            username: formData.get('username'),
            password: formData.get('password')
        };
        
        // Validate username uniqueness
        const existingAdmin = this.admins.find(admin => 
            admin.username === adminData.username && 
            (!this.currentAdmin || admin.id !== this.currentAdmin.id)
        );
        
        if (existingAdmin) {
            this.showError('Username already exists');
            return;
        }
        
        try {
            const url = this.currentAdmin 
                ? `/admin/api/admin-users/${this.currentAdmin.id}`
                : '/admin/api/admin-users';
            
            const method = this.currentAdmin ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(adminData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showSuccess(this.currentAdmin ? 'Administrator updated successfully' : 'Administrator created successfully');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('adminModal'));
                modal.hide();
                
                // Reload admins
                await this.loadAdmins();
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to save administrator');
            }
        } catch (error) {
            console.error('Error saving administrator:', error);
            this.showError(error.message || 'Failed to save administrator');
        }
    }
    
    confirmDeleteAdmin(adminId) {
        const admin = this.admins.find(a => a.id === adminId);
        if (!admin) return;
        
        if (admin.id === 1) {
            this.showError('Cannot delete the super administrator');
            return;
        }
        
        document.getElementById('confirmMessage').innerHTML = `
            Are you sure you want to delete administrator <strong>${admin.employee_name}</strong>?
            <br><small class="text-muted">This action cannot be undone.</small>
        `;
        
        this.confirmCallback = () => this.deleteAdmin(adminId);
        
        const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        modal.show();
    }
    
    async deleteAdmin(adminId) {
        try {
            const response = await fetch(`/admin/api/admin-users/${adminId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showSuccess('Administrator deleted successfully');
                await this.loadAdmins();
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to delete administrator');
            }
        } catch (error) {
            console.error('Error deleting administrator:', error);
            this.showError(error.message || 'Failed to delete administrator');
        }
    }
    
    executeConfirmAction() {
        if (this.confirmCallback) {
            this.confirmCallback();
            this.confirmCallback = null;
        }
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmModal'));
        modal.hide();
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminUsersManager = new AdminUsersManager();
});