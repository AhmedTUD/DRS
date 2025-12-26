/**
 * Clean Users Management System
 * Simple and efficient user management with regions and branches
 */

class UsersManager {
    constructor() {
        this.users = [];
        this.currentUser = null;
        this.currentUserRegions = [];
        this.editingRegionIndex = -1;
        this.editingBranchIndex = -1;
        this.currentRegionIndex = -1;
        this.confirmCallback = null;
        
        this.initializeEventListeners();
        this.loadUsers();
        
        console.log('✅ Clean Users Manager initialized');
    }
    
    initializeEventListeners() {
        // Main actions
        document.getElementById('createUserBtn').addEventListener('click', this.showCreateUserModal.bind(this));
        document.getElementById('saveUserBtn').addEventListener('click', this.saveUser.bind(this));
        document.getElementById('searchUsers').addEventListener('input', this.filterUsers.bind(this));
        
        // Region management
        document.getElementById('addRegionBtn').addEventListener('click', this.showAddRegionModal.bind(this));
        document.getElementById('saveRegionBtn').addEventListener('click', this.saveRegion.bind(this));
        
        // Branch management
        document.getElementById('saveBranchBtn').addEventListener('click', this.saveBranch.bind(this));
        
        // Confirmation
        document.getElementById('confirmActionBtn').addEventListener('click', this.executeConfirmAction.bind(this));
        
        console.log('✅ Event listeners initialized');
    }
    
    async loadUsers() {
        try {
            const response = await fetch('/admin/api/users');
            if (response.ok) {
                this.users = await response.json();
                this.renderUsers();
                this.updateUserCount();
                console.log(`✅ Loaded ${this.users.length} users`);
            } else {
                throw new Error('Failed to load users');
            }
        } catch (error) {
            console.error('Error loading users:', error);
            this.showError('Failed to load users');
            document.getElementById('loadingUsers').innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <p class="text-danger">Failed to load users</p>
                    <button class="btn btn-outline-primary" onclick="usersManager.loadUsers()">
                        <i class="fas fa-redo me-2"></i>Retry
                    </button>
                </div>
            `;
        }
    }
    
    renderUsers() {
        const container = document.getElementById('usersContainer');
        const loading = document.getElementById('loadingUsers');
        
        if (loading) {
            loading.style.display = 'none';
        }
        
        if (this.users.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-users fa-4x text-muted mb-4"></i>
                    <h4 class="text-muted">No users found</h4>
                    <p class="text-muted">Create your first user to get started.</p>
                    <button class="btn btn-primary btn-lg" onclick="usersManager.showCreateUserModal()">
                        <i class="fas fa-user-plus me-2"></i>Create New User
                    </button>
                </div>
            `;
            return;
        }
        
        const usersHtml = this.users.map(user => this.renderUserCard(user)).join('');
        container.innerHTML = usersHtml;
    }
    
    renderUserCard(user) {
        const regionsCount = user.regions ? user.regions.length : 0;
        const branchesCount = user.regions ? 
            user.regions.reduce((total, region) => total + (region.branches ? region.branches.length : 0), 0) : 0;
        
        return `
            <div class="user-card card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <div class="d-flex align-items-center mb-3">
                                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" 
                                     style="width: 50px; height: 50px;">
                                    <i class="fas fa-user fa-lg"></i>
                                </div>
                                <div>
                                    <h5 class="mb-1">${user.spvr_name}</h5>
                                    <div class="text-muted">
                                        <span class="badge bg-secondary me-2">${user.spvr_code}</span>
                                        <small><i class="fas fa-at me-1"></i>${user.username}</small>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="text-primary">
                                        <i class="fas fa-map-marker-alt fa-lg"></i>
                                    </div>
                                    <small class="text-muted d-block">${regionsCount} Region${regionsCount !== 1 ? 's' : ''}</small>
                                </div>
                                <div class="col-4">
                                    <div class="text-success">
                                        <i class="fas fa-building fa-lg"></i>
                                    </div>
                                    <small class="text-muted d-block">${branchesCount} Shop${branchesCount !== 1 ? 's' : ''}</small>
                                </div>
                                <div class="col-4">
                                    <div class="text-info">
                                        <i class="fas fa-calendar fa-lg"></i>
                                    </div>
                                    <small class="text-muted d-block">${new Date(user.created_at).toLocaleDateString()}</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4 text-end">
                            <div class="btn-group-vertical d-grid gap-2">
                                <button class="btn btn-outline-primary btn-sm" 
                                        onclick="usersManager.showEditUserModal(${user.id})"
                                        title="Edit User">
                                    <i class="fas fa-edit me-2"></i>Edit
                                </button>
                                <button class="btn btn-outline-danger btn-sm" 
                                        onclick="usersManager.deleteUser(${user.id})"
                                        title="Delete User">
                                    <i class="fas fa-trash me-2"></i>Delete
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Regions Preview -->
                    ${regionsCount > 0 ? `
                        <div class="mt-4 pt-3 border-top">
                            <h6 class="text-muted mb-3">
                                <i class="fas fa-map-marker-alt me-2"></i>Regions & Shops
                            </h6>
                            <div class="row">
                                ${user.regions.slice(0, 3).map(region => `
                                    <div class="col-md-4 mb-2">
                                        <div class="bg-light p-2 rounded">
                                            <div class="fw-bold text-success">${region.name}</div>
                                            ${region.branches && region.branches.length > 0 ? `
                                                <div class="mt-1">
                                                    ${region.branches.slice(0, 2).map(branch => `
                                                        <small class="badge bg-primary me-1">${branch.name}</small>
                                                    `).join('')}
                                                    ${region.branches.length > 2 ? `
                                                        <small class="text-muted">+${region.branches.length - 2} more</small>
                                                    ` : ''}
                                                </div>
                                            ` : '<small class="text-muted">No shops</small>'}
                                        </div>
                                    </div>
                                `).join('')}
                                ${regionsCount > 3 ? `
                                    <div class="col-12">
                                        <small class="text-muted">+${regionsCount - 3} more regions...</small>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    showCreateUserModal() {
        this.currentUser = null;
        this.currentUserRegions = [];
        
        document.getElementById('userModalTitle').textContent = 'Create New User';
        document.getElementById('userId').value = '';
        document.getElementById('spvrName').value = '';
        document.getElementById('spvrCode').value = '';
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        document.getElementById('password').required = true;
        document.getElementById('passwordHelp').style.display = 'none';
        
        this.renderRegions();
        this.clearFormErrors();
        
        const modal = new bootstrap.Modal(document.getElementById('userModal'));
        modal.show();
    }
    
    async showEditUserModal(userId) {
        try {
            const response = await fetch(`/admin/api/users/${userId}`);
            if (!response.ok) throw new Error('Failed to load user');
            
            this.currentUser = await response.json();
            this.currentUserRegions = this.currentUser.regions || [];
            

            
            document.getElementById('userModalTitle').textContent = 'Edit User';
            document.getElementById('userId').value = this.currentUser.id;
            document.getElementById('spvrName').value = this.currentUser.spvr_name;
            document.getElementById('spvrCode').value = this.currentUser.spvr_code;
            document.getElementById('username').value = this.currentUser.username;
            document.getElementById('password').value = '';
            document.getElementById('password').required = false;
            document.getElementById('passwordHelp').style.display = 'block';
            
            this.renderRegions();
            this.clearFormErrors();
            
            const modal = new bootstrap.Modal(document.getElementById('userModal'));
            modal.show();
            
        } catch (error) {
            console.error('Error loading user:', error);
            this.showError('Failed to load user details');
        }
    }
    
    renderRegions() {
        const container = document.getElementById('regionsContainer');
        const noMessage = document.getElementById('noRegionsMessage');
        
        if (this.currentUserRegions.length === 0) {
            noMessage.style.display = 'block';
            container.innerHTML = '';
            return;
        }
        
        noMessage.style.display = 'none';
        
        const regionsHtml = this.currentUserRegions.map((region, index) => `
            <div class="region-card p-3 mb-3">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h6 class="mb-1 text-success">
                            <i class="fas fa-map-marker-alt me-2"></i>
                            ${region.name}
                        </h6>
                    </div>
                    <div>
                        <button type="button" class="btn btn-sm btn-outline-primary me-1" 
                                onclick="usersManager.editRegion(${index})" title="Edit Region">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-success me-1" 
                                onclick="usersManager.showAddBranchModal(${index})" title="Add Shop">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="usersManager.deleteRegion(${index})" title="Delete Region">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Branches -->
                <div class="branches-container">
                    ${region.branches && region.branches.length > 0 ? 
                        region.branches.map((branch, branchIndex) => `
                            <div class="branch-item d-flex justify-content-between align-items-center">
                                <div>
                                    <i class="fas fa-building text-primary me-2"></i>
                                    <strong>${branch.name}</strong>
                                    <small class="text-muted ms-2">Code: ${branch.code}</small>
                                    ${branch.governorate ? `<small class="text-muted ms-2">• ${branch.governorate}</small>` : ''}
                                </div>
                                <div>
                                    <button type="button" class="btn btn-sm btn-outline-primary me-1" 
                                            onclick="usersManager.editBranch(${index}, ${branchIndex})" title="Edit Shop">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button type="button" class="btn btn-sm btn-outline-danger" 
                                            onclick="usersManager.deleteBranch(${index}, ${branchIndex})" title="Delete Shop">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        `).join('') : 
                        '<div class="text-muted text-center py-3"><small>No shops in this region</small></div>'
                    }
                </div>
            </div>
        `).join('');
        
        container.innerHTML = regionsHtml;
    }
    
    showAddRegionModal() {
        this.editingRegionIndex = -1;
        document.getElementById('regionModalTitle').textContent = 'Add Region';
        document.getElementById('regionIndex').value = '';
        document.getElementById('regionName').value = '';
        
        this.clearFormErrors('regionForm');
        
        const modal = new bootstrap.Modal(document.getElementById('regionModal'));
        modal.show();
    }
    
    editRegion(index) {
        this.editingRegionIndex = index;
        const region = this.currentUserRegions[index];
        
        document.getElementById('regionModalTitle').textContent = 'Edit Region';
        document.getElementById('regionIndex').value = index;
        document.getElementById('regionName').value = region.name;
        
        this.clearFormErrors('regionForm');
        
        const modal = new bootstrap.Modal(document.getElementById('regionModal'));
        modal.show();
    }
    
    saveRegion() {
        const name = document.getElementById('regionName').value.trim();
        
        if (!name) {
            this.showFieldError('regionName', 'Region name is required');
            return;
        }
        
        if (name.length > 100) {
            this.showFieldError('regionName', 'Region name must be 100 characters or less');
            return;
        }
        
        // Check for duplicate names in current regions
        const existingRegion = this.currentUserRegions.find((region, index) => 
            region.name.toLowerCase() === name.toLowerCase() && index !== this.editingRegionIndex
        );
        
        if (existingRegion) {
            this.showFieldError('regionName', 'Region name already exists for this user');
            return;
        }
        
        if (this.editingRegionIndex >= 0) {
            // Edit existing region
            this.currentUserRegions[this.editingRegionIndex].name = name;
        } else {
            // Add new region
            this.currentUserRegions.push({
                name: name,
                branches: []
            });
        }
        
        this.renderRegions();
        bootstrap.Modal.getInstance(document.getElementById('regionModal')).hide();
    }
    
    deleteRegion(index) {
        const region = this.currentUserRegions[index];
        const branchCount = region.branches ? region.branches.length : 0;
        
        let message = `Delete region "${region.name}"?`;
        if (branchCount > 0) {
            message += ` This will also delete ${branchCount} shop${branchCount !== 1 ? 's' : ''}.`;
        }
        
        this.showConfirmDialog(message, () => {
            this.currentUserRegions.splice(index, 1);
            this.renderRegions();
        });
    }
    
    showAddBranchModal(regionIndex) {
        this.currentRegionIndex = regionIndex;
        this.editingBranchIndex = -1;
        
        document.getElementById('branchModalTitle').textContent = 'Add Shop';
        document.getElementById('branchRegionIndex').value = regionIndex;
        document.getElementById('branchIndex').value = '';
        document.getElementById('branchName').value = '';
        document.getElementById('branchCode').value = '';
        document.getElementById('branchGovernorate').value = '';
        
        this.clearFormErrors('branchForm');
        
        const modal = new bootstrap.Modal(document.getElementById('branchModal'));
        modal.show();
    }
    
    editBranch(regionIndex, branchIndex) {
        this.currentRegionIndex = regionIndex;
        this.editingBranchIndex = branchIndex;
        const branch = this.currentUserRegions[regionIndex].branches[branchIndex];
        
        document.getElementById('branchModalTitle').textContent = 'Edit Shop';
        document.getElementById('branchRegionIndex').value = regionIndex;
        document.getElementById('branchIndex').value = branchIndex;
        document.getElementById('branchName').value = branch.name;
        document.getElementById('branchCode').value = branch.code;
        document.getElementById('branchGovernorate').value = branch.governorate || '';
        
        this.clearFormErrors('branchForm');
        
        const modal = new bootstrap.Modal(document.getElementById('branchModal'));
        modal.show();
    }
    
    saveBranch() {
        const name = document.getElementById('branchName').value.trim();
        const code = document.getElementById('branchCode').value.trim();
        const governorate = document.getElementById('branchGovernorate').value.trim();
        

        
        if (!name) {
            this.showFieldError('branchName', 'Shop name is required');
            return;
        }
        
        if (!code) {
            this.showFieldError('branchCode', 'Shop code is required');
            return;
        }
        
        if (name.length > 100) {
            this.showFieldError('branchName', 'Shop name must be 100 characters or less');
            return;
        }
        
        if (code.length > 50) {
            this.showFieldError('branchCode', 'Shop code must be 50 characters or less');
            return;
        }
        
        // Check for duplicate codes across all branches for this user
        const allBranches = this.currentUserRegions.flatMap((region, regionIndex) => 
            region.branches ? region.branches.map((branch, branchIndex) => ({
                ...branch, 
                regionIndex, 
                branchIndex
            })) : []
        );
        
        const existingBranch = allBranches.find(branch => 
            branch.code.toLowerCase() === code.toLowerCase() && 
            !(branch.regionIndex === this.currentRegionIndex && branch.branchIndex === this.editingBranchIndex)
        );
        
        if (existingBranch) {
            this.showFieldError('branchCode', 'Shop code already exists for this user');
            return;
        }
        
        const region = this.currentUserRegions[this.currentRegionIndex];
        if (!region.branches) {
            region.branches = [];
        }
        
        if (this.editingBranchIndex >= 0) {
            // Edit existing shop
            region.branches[this.editingBranchIndex].name = name;
            region.branches[this.editingBranchIndex].code = code;
            region.branches[this.editingBranchIndex].governorate = governorate;
        } else {
            // Add new shop
            region.branches.push({ name, code, governorate });
        }
        
        this.renderRegions();
        bootstrap.Modal.getInstance(document.getElementById('branchModal')).hide();
    }
    
    deleteBranch(regionIndex, branchIndex) {
        const branch = this.currentUserRegions[regionIndex].branches[branchIndex];
        
        this.showConfirmDialog(`Delete shop "${branch.name}"?`, () => {
            this.currentUserRegions[regionIndex].branches.splice(branchIndex, 1);
            this.renderRegions();
        });
    }
    
    async saveUser() {
        // Clear previous errors
        this.clearFormErrors('userForm');
        
        // Get form data
        const formData = {
            spvr_name: document.getElementById('spvrName').value.trim(),
            spvr_code: document.getElementById('spvrCode').value.trim(),
            username: document.getElementById('username').value.trim(),
            password: document.getElementById('password').value.trim(),
            regions: this.currentUserRegions
        };
        
        // Validate required fields
        let hasErrors = false;
        
        if (!formData.spvr_name) {
            this.showFieldError('spvrName', 'SPVR Name is required');
            hasErrors = true;
        } else if (formData.spvr_name.length > 100) {
            this.showFieldError('spvrName', 'SPVR Name must be 100 characters or less');
            hasErrors = true;
        }
        
        if (!formData.spvr_code) {
            this.showFieldError('spvrCode', 'SPVR Code is required');
            hasErrors = true;
        } else if (formData.spvr_code.length > 50) {
            this.showFieldError('spvrCode', 'SPVR Code must be 50 characters or less');
            hasErrors = true;
        }
        
        if (!formData.username) {
            this.showFieldError('username', 'Username is required');
            hasErrors = true;
        }
        
        const isCreating = !this.currentUser;
        if (isCreating && !formData.password) {
            this.showFieldError('password', 'Password is required');
            hasErrors = true;
        }
        
        if (hasErrors) {
            return;
        }
        
        // Disable save button
        const saveBtn = document.getElementById('saveUserBtn');
        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        
        try {
            const url = isCreating ? '/admin/api/users' : `/admin/api/users/${this.currentUser.id}`;
            const method = isCreating ? 'POST' : 'PUT';
            
            // If editing and password is empty, don't send it
            if (!isCreating && !formData.password) {
                delete formData.password;
            }
            

            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showSuccess(isCreating ? 'User created successfully' : 'User updated successfully');
                bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
                await this.loadUsers(); // Reload users list
            } else {
                this.showError(result.message || 'Failed to save user');
            }
        } catch (error) {
            console.error('Error saving user:', error);
            this.showError('Error saving user: ' + error.message);
        } finally {
            // Re-enable save button
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    }
    
    async deleteUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (!user) return;
        
        try {
            // First, try to delete without any special options to see if user has reports
            const response = await fetch(`/admin/api/users/${userId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showSuccess('User deleted successfully');
                await this.loadUsers();
                
                // Refresh dashboard stats if the function exists
                if (typeof window.refreshDashboard === 'function') {
                    window.refreshDashboard();
                }
            } else if (response.status === 400 && result.force_delete_required) {
                // User has reports - show force delete option
                this.showForceDeleteDialog(userId, user, result);
            } else {
                this.showError(result.message || 'Failed to delete user');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            this.showError('Error deleting user');
        }
    }
    
    showForceDeleteDialog(userId, user, result) {
        const reportsCount = result.reports_count;
        
        // Create modal content
        const modalContent = `
            <div class="modal fade" id="forceDeleteModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                User Has Reports
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning">
                                <strong>${user.spvr_name}</strong> has <strong>${reportsCount}</strong> report${reportsCount !== 1 ? 's' : ''}.
                            </div>
                            
                            <p>To delete this user, you must also delete all their reports. This action cannot be undone.</p>
                            
                            <div class="mt-3">
                                <button class="btn btn-outline-info me-2" onclick="usersManager.viewUserReports(${userId})">
                                    <i class="fas fa-eye me-2"></i>View Reports (${reportsCount})
                                </button>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-danger" onclick="usersManager.forceDeleteUser(${userId})">
                                <i class="fas fa-trash me-2"></i>Delete User & Reports
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('forceDeleteModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalContent);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('forceDeleteModal'));
        modal.show();
        
        // Clean up when modal is hidden
        document.getElementById('forceDeleteModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
    
    async forceDeleteUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (!user) return;
        
        try {
            const response = await fetch(`/admin/api/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ force_delete: true })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showSuccess(result.message);
                bootstrap.Modal.getInstance(document.getElementById('forceDeleteModal')).hide();
                await this.loadUsers();
                
                // Refresh dashboard stats if the function exists
                if (typeof window.refreshDashboard === 'function') {
                    window.refreshDashboard();
                }
            } else {
                this.showError(result.message || 'Failed to delete user');
            }
        } catch (error) {
            console.error('Error force deleting user:', error);
            this.showError('Error deleting user');
        }
    }
    
    async viewUserReports(userId) {
        try {
            const response = await fetch(`/admin/api/users/${userId}/reports`);
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showUserReportsModal(result.user, result.reports);
            } else {
                this.showError('Failed to load user reports');
            }
        } catch (error) {
            console.error('Error loading user reports:', error);
            this.showError('Error loading user reports');
        }
    }
    
    showUserReportsModal(user, reports) {
        const modalContent = `
            <div class="modal fade" id="userReportsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-file-alt me-2"></i>
                                Reports for ${user.name} (${user.code})
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${reports.length > 0 ? `
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>ID</th>
                                                <th>Store</th>
                                                <th>Store Code</th>
                                                <th>Area</th>
                                                <th>Report Date</th>
                                                <th>Created</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${reports.map(report => `
                                                <tr id="report-row-${report.id}">
                                                    <td>${report.id}</td>
                                                    <td>${report.store_name}</td>
                                                    <td><code>${report.store_code}</code></td>
                                                    <td><span class="badge bg-info">${report.area}</span></td>
                                                    <td>${report.report_date}</td>
                                                    <td>${report.created_at}</td>
                                                    <td>
                                                        <button class="btn btn-sm btn-outline-danger" 
                                                                onclick="usersManager.deleteReport(${report.id})"
                                                                title="Delete Report">
                                                            <i class="fas fa-trash"></i>
                                                        </button>
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            ` : `
                                <div class="text-center py-4">
                                    <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                                    <p class="text-muted">No reports found for this user.</p>
                                </div>
                            `}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('userReportsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalContent);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('userReportsModal'));
        modal.show();
        
        // Clean up when modal is hidden
        document.getElementById('userReportsModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
    
    async deleteReport(reportId) {
        if (!confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/admin/api/reports/${reportId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showSuccess('Report deleted successfully');
                
                // Remove the row from the table
                const row = document.getElementById(`report-row-${reportId}`);
                if (row) {
                    row.remove();
                }
                
                // If no more rows, show empty message
                const tbody = document.querySelector('#userReportsModal tbody');
                if (tbody && tbody.children.length === 0) {
                    const modalBody = document.querySelector('#userReportsModal .modal-body');
                    modalBody.innerHTML = `
                        <div class="text-center py-4">
                            <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                            <p class="text-muted">No reports found for this user.</p>
                        </div>
                    `;
                }
            } else {
                this.showError(result.message || 'Failed to delete report');
            }
        } catch (error) {
            console.error('Error deleting report:', error);
            this.showError('Error deleting report');
        }
    }
    

    
    filterUsers() {
        const searchTerm = document.getElementById('searchUsers').value.toLowerCase();
        
        if (!searchTerm) {
            this.renderUsers();
            return;
        }
        
        const filteredUsers = this.users.filter(user => 
            user.spvr_name.toLowerCase().includes(searchTerm) ||
            user.spvr_code.toLowerCase().includes(searchTerm) ||
            user.username.toLowerCase().includes(searchTerm)
        );
        
        const container = document.getElementById('usersContainer');
        
        if (filteredUsers.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No users found</h5>
                    <p class="text-muted">No users match your search criteria.</p>
                </div>
            `;
            return;
        }
        
        const usersHtml = filteredUsers.map(user => this.renderUserCard(user)).join('');
        container.innerHTML = usersHtml;
    }
    
    updateUserCount() {
        const count = this.users.length;
        document.getElementById('userCount').textContent = `${count} user${count !== 1 ? 's' : ''}`;
    }
    
    showConfirmDialog(message, callback) {
        document.getElementById('confirmMessage').textContent = message;
        this.confirmCallback = callback;
        
        const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        modal.show();
    }
    
    executeConfirmAction() {
        if (this.confirmCallback) {
            this.confirmCallback();
            this.confirmCallback = null;
        }
        bootstrap.Modal.getInstance(document.getElementById('confirmModal')).hide();
    }
    
    showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        
        field.classList.add('is-invalid');
        if (feedback) {
            feedback.textContent = message;
        }
    }
    
    clearFormErrors(formId = null) {
        const selector = formId ? `#${formId} .is-invalid` : '.is-invalid';
        const invalidFields = document.querySelectorAll(selector);
        invalidFields.forEach(field => {
            field.classList.remove('is-invalid');
        });
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'danger');
    }
    
    showToast(message, type = 'info') {
        const container = document.querySelector('.toast-container');
        
        const toastHtml = `
            <div class="toast align-items-center text-bg-${type} border-0 slide-in-right" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = container.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
        toast.show();
        
        // Remove element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.usersManager = new UsersManager();
    console.log('🚀 Clean Users Manager ready!');
});