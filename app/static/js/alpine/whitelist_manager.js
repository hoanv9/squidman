document.addEventListener('alpine:init', () => {
    Alpine.data('whitelistManager', () => ({
        // Restore tab from localStorage or default to 'domains'
        currentTab: localStorage.getItem('whitelist_active_tab') || 'domains',
        searchQuery: '',

        // Pagination State
        currentPage: 1,
        limit: 10,

        // Raw Data (Server-injected)
        allDomains: [],
        allIps: [],
        allTemplates: [],

        // Filtered Data
        filteredDomains: [],
        filteredIps: [],
        filteredTemplates: [],

        // Modals
        isModalOpen: false,
        isDeleteModalOpen: false,
        isImportModalOpen: false,
        modalTitle: '',
        modalMode: 'add', // add | edit
        formAction: '',
        formData: { value: '', description: '', templateName: '', templateDomains: '' },
        deleteId: null,
        deleteType: '',

        // Bulk Action State
        isBulk: false,
        confirmText: '',
        selectedCount: 0,

        init() {
            this.$watch('searchQuery', () => this.filterItems());
            this.$watch('limit', () => {
                this.currentPage = 1;
                this.filterItems();
            });

            // Re-calculate selection on tab switch or pagination change
            this.$watch('currentPage', () => setTimeout(() => this.updateSelectedCount(), 50));
            this.$watch('currentTab', () => {
                this.selectedCount = 0;
                this.confirmText = '';
            });
        },

        initData() {
            try {
                // Get data from JSON script tag
                const dataElement = document.getElementById('whitelist-data');
                const data = dataElement ? JSON.parse(dataElement.textContent) : {};

                const domains = data.domains;
                const ips = data.ips;
                const templates = data.templates;

                // Ensure we have arrays
                this.allDomains = Array.isArray(domains) ? domains : [];
                this.allIps = Array.isArray(ips) ? ips : [];
                this.allTemplates = Array.isArray(templates) ? templates : [];
            } catch (e) {
                console.error("Error parsing whitelist data:", e);
                this.allDomains = [];
                this.allIps = [];
                this.allTemplates = [];
            }

            this.filterItems();
        },

        // --- Selection & Bulk Actions ---

        toggleSelectAll(e) {
            const isChecked = e.target.checked;
            const formId = this.getStatusFormId();
            if (!formId) return;

            const form = document.getElementById(formId);
            if (form) {
                const checkboxes = form.querySelectorAll('input[type="checkbox"][name="item_ids"]');
                checkboxes.forEach(cb => cb.checked = isChecked);
                this.updateSelectedCount();
            }
        },

        updateSelectedCount() {
            const formId = this.getStatusFormId();
            if (!formId) {
                this.selectedCount = 0;
                return;
            }
            const form = document.getElementById(formId);
            if (form) {
                this.selectedCount = form.querySelectorAll('input[type="checkbox"][name="item_ids"]:checked').length;

                // Update header checkbox
                const headerCb = form.querySelector('thead input[type="checkbox"]');
                const allCbs = form.querySelectorAll('input[type="checkbox"][name="item_ids"]');
                if (headerCb && allCbs.length > 0) {
                    headerCb.checked = this.selectedCount === allCbs.length;
                    headerCb.indeterminate = this.selectedCount > 0 && this.selectedCount < allCbs.length;
                }
            }
        },

        getStatusFormId() {
            if (this.currentTab === 'domains') return 'delete-domains-form';
            if (this.currentTab === 'ips') return 'delete-ips-form';
            if (this.currentTab === 'templates') return 'delete-templates-form';
            return null;
        },

        openBulkDeleteModal() {
            if (this.selectedCount === 0) return;
            this.isBulk = true;
            this.confirmText = '';
            this.isDeleteModalOpen = true;
        },

        submitBulkDelete() {
            if (this.confirmText !== 'confirm') return;
            const formId = this.getStatusFormId();
            if (formId) {
                document.getElementById(formId).submit();
            }
        },

        openSingleDelete(id, type) {
            this.isBulk = false;
            this.deleteId = id;
            this.deleteType = type;
            this.isDeleteModalOpen = true;
        },

        closeDeleteModal() {
            this.isDeleteModalOpen = false;
            this.confirmText = '';
        },

        // --- Pagination Getters ---
        get totalItems() {
            if (this.currentTab === 'domains') return this.filteredDomains.length;
            if (this.currentTab === 'ips') return this.filteredIps.length;
            return this.filteredTemplates.length;
        },

        get totalPages() {
            return Math.ceil(this.totalItems / this.limit) || 1;
        },

        get paginatedDomains() {
            const start = (this.currentPage - 1) * this.limit;
            return this.filteredDomains.slice(start, start + parseInt(this.limit));
        },

        get paginatedIps() {
            const start = (this.currentPage - 1) * this.limit;
            return this.filteredIps.slice(start, start + parseInt(this.limit));
        },

        get paginatedTemplates() {
            const start = (this.currentPage - 1) * this.limit;
            return this.filteredTemplates.slice(start, start + parseInt(this.limit));
        },

        get paginationLabel() {
            if (this.totalItems === 0) return 'No items';
            const start = (this.currentPage - 1) * this.limit + 1;
            const end = Math.min(this.currentPage * this.limit, this.totalItems);
            return `Showing ${start} to ${end} of ${this.totalItems}`;
        },

        // Simplified pagination for macro
        prevPage() {
            if (this.currentPage > 1) {
                this.currentPage--;
            }
        },

        nextPage() {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
            }
        },

        updatePagination() {
            // No need to reset currentPage here as it's handled by callers or limit watcher
        },

        reloadList() {
            window.location.reload();
        },

        switchTab(tab) {
            this.currentTab = tab;
            localStorage.setItem('whitelist_active_tab', tab);
            this.searchQuery = '';
            this.currentPage = 1;
            this.filterItems();
            // Reset selection is handled by watcher
        },

        filterItems() {
            // ... existing filter logic ...
            // We need to re-run it
            this.currentPage = 1; // Reset page
            const query = this.searchQuery.toLowerCase().trim();

            this.filteredDomains = this.allDomains.filter(item =>
                item.domain.toLowerCase().includes(query) ||
                (item.description && item.description.toLowerCase().includes(query))
            );

            this.filteredIps = this.allIps.filter(item =>
                item.ip_address.toLowerCase().includes(query) ||
                (item.description && item.description.toLowerCase().includes(query))
            );

            this.filteredTemplates = this.allTemplates.filter(item =>
                item.name.toLowerCase().includes(query) ||
                (item.description && item.description.toLowerCase().includes(query)) ||
                (item.domains && Array.isArray(item.domains) && item.domains.some(d => d && d.toLowerCase().includes(query)))
            );

            // After filter, update selection count (might be 0 if items hidden)
            setTimeout(() => this.updateSelectedCount(), 0);
        },

        openModal(mode, item = null) {
            if (this.currentTab === 'templates') {
                this.openTemplateModal(mode, item);
            } else {
                this.openDomainIpModal(mode, item);
            }
        },

        openDomainIpModal(mode, item = null) {
            this.modalMode = mode;
            const type = this.currentTab === 'domains' ? 'domain' : 'ip';

            if (mode === 'add') {
                this.modalTitle = `Add New ${type === 'domain' ? 'Domain' : 'IP'}`;
                this.formAction = `/whitelist/${type}s/add`;
                this.formData = { value: '', description: '', templateName: '', templateDomains: '' };
            } else {
                this.modalTitle = `Edit ${type === 'domain' ? 'Domain' : 'IP'}`;
                this.formAction = `/whitelist/${type}s/edit/${item.id}`;
                this.formData = {
                    value: type === 'domain' ? item.domain : item.ip_address,
                    description: item.description || '',
                    templateName: '',
                    templateDomains: ''
                };
            }
            this.isModalOpen = true;
        },

        openTemplateModal(mode, item = null) {
            this.modalMode = mode;
            if (mode === 'add') {
                this.modalTitle = 'Add New Template';
                this.formAction = '/whitelist/templates/add';
                this.formData = {
                    value: '',
                    description: '',
                    templateName: '',
                    templateDomains: ''
                };
            } else {
                this.modalTitle = 'Edit Template';
                this.formAction = `/whitelist/templates/edit/${item.id}`;
                this.formData = {
                    value: '',
                    description: item.description || '',
                    templateName: item.name,
                    templateDomains: item.domains ? item.domains.join('\n') : ''
                };
            }
            this.isModalOpen = true;
        },

        closeModal() {
            this.isModalOpen = false;
        },

        // Deprecated openDeleteModal in favor of openSingleDelete
        // But keeping it for potential external calls or legacy if needed
        openDeleteModal(id) {
            // We map it to openSingleDelete
            if (this.currentTab === 'domains') this.openSingleDelete(id, 'domain');
            else if (this.currentTab === 'ips') this.openSingleDelete(id, 'ip');
            else this.openSingleDelete(id, 'template');
        },

        getDeleteUrl() {
            if (this.deleteType === 'template') {
                return `/whitelist/templates/delete/${this.deleteId}`;
            }
            return `/whitelist/${this.deleteType}s/delete/${this.deleteId}`;
        },

        getExportUrl() {
            if (this.currentTab === 'templates') return '/whitelist/templates/export';
            if (this.currentTab === 'domains') return '/whitelist/domains/export';
            return '/whitelist/ips/export';
        },

        getImportAction() {
            if (this.currentTab === 'templates') return '/whitelist/templates/import';
            if (this.currentTab === 'domains') return '/whitelist/domains/import';
            return '/whitelist/ips/import';
        },

        openImportModal() {
            this.isImportModalOpen = true;
        }
    }));
});
