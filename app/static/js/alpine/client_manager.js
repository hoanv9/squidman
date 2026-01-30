document.addEventListener('alpine:init', () => {
    Alpine.data('clientManager', () => ({
        // UI States
        isSearchModalOpen: false,
        isDeleteModalOpen: false,
        isBulkDeleteModalOpen: false,
        isClientModalOpen: false,
        isTemplateModalOpen: false,
        currentTab: 'clients',

        // Client Modal Data
        modalTitle: 'Add New Client',
        modalMode: 'add', // add | edit
        formAction: '/clients/add',
        formData: {
            ip: '',
            dns: '',
            domains: '',
            expiration: '',
            ticket: '',
            notes: ''
        },
        isVip: false,
        parsingDNS: false,

        // Templates Data
        urlGroups: {},
        selectedTemplates: [],
        templateSearch: '',
        get filteredUrlGroups() {
            const search = this.templateSearch.toLowerCase().trim();
            if (!search) return this.urlGroups;

            const filtered = {};
            Object.entries(this.urlGroups).forEach(([group, urls]) => {
                // Check if group name matches
                const groupMatches = group.toLowerCase().includes(search);

                // Check if any URL in the group matches
                const urlMatches = urls.some(url => url.toLowerCase().includes(search));

                if (groupMatches || urlMatches) {
                    filtered[group] = urls;
                }
            });
            return filtered;
        },
        get mergedPreview() {
            let domains = [];
            this.selectedTemplates.forEach(group => {
                if (this.urlGroups[group]) domains.push(...this.urlGroups[group]);
            });
            return [...new Set(domains)];
        },

        // Delete Data
        deleteId: null,
        selectedCount: 0,
        confirmText: '', // For bulk delete confirmation

        // List & Pagination Data
        searchContent: '',
        searchField: 'ip',
        ipFilter: '',
        limit: 10,
        page: 1,
        totalRows: 0,
        totalPages: 1,
        start: 0,
        end: 0,

        // Sorting
        sortCol: null,
        sortAsc: true,

        init() {
            this.updatePagination();
            this.fetchUrlGroups();
            this.calculateDefaultExpiration();

            this.$watch('isVip', value => {
                if (value) {
                    this.formData.domains = 'ANY';
                } else if (this.formData.domains === 'ANY') {
                    this.formData.domains = '';
                }
            });
        },

        switchTab(tab) {
            this.currentTab = tab;
        },

        sortBy(col) {
            if (this.sortCol === col) this.sortAsc = !this.sortAsc;
            else { this.sortCol = col; this.sortAsc = true; }
            this.sortRows();
        },

        sortRows() {
            const tbody = document.getElementById('client-rows');
            const rows = Array.from(document.querySelectorAll('.client-row'));

            rows.sort((a, b) => {
                let key = this.sortCol;
                if (key === 'added') key = 'addedIso';

                let vA = a.dataset[key] || '';
                let vB = b.dataset[key] || '';

                if (this.sortCol === 'days') {
                    vA = parseInt(vA) || 0;
                    vB = parseInt(vB) || 0;
                }

                if (vA < vB) return this.sortAsc ? -1 : 1;
                if (vA > vB) return this.sortAsc ? 1 : -1;
                return 0;
            });

            rows.forEach(r => tbody.appendChild(r));
            this.page = 1;
            this.updatePagination();
        },

        // --- Form & Modal Logic ---

        calculateDefaultExpiration() {
            const date = new Date();
            date.setDate(date.getDate() + 7);
            return date.toISOString().split('T')[0];
        },

        addDays(days) {
            const date = new Date();
            date.setDate(date.getDate() + days);
            this.formData.expiration = date.toISOString().split('T')[0];
        },

        openModal(mode, rowEl = null) {
            this.modalMode = mode;

            if (mode === 'add') {
                this.modalTitle = 'Add New Client';
                this.formAction = '/clients/add';
                this.formData = {
                    ip: '', dns: '', domains: '', expiration: this.calculateDefaultExpiration(), ticket: '', notes: ''
                };
                this.isVip = false;
            } else {
                // Edit or Clone
                const data = rowEl.dataset;
                let domains = '';
                try {
                    const parsed = JSON.parse(data.urls);
                    if (Array.isArray(parsed)) {
                        domains = parsed.join('\n');
                    } else {
                        domains = parsed || '';
                    }
                } catch (e) { domains = ''; }

                this.formData = {
                    ip: mode === 'edit' ? data.ip : '',
                    dns: mode === 'edit' ? (data.dns || '') : '',
                    domains: domains,
                    expiration: data.expiration,
                    ticket: data.ticket || '',
                    notes: data.notes || ''
                };

                this.isVip = (domains === 'ANY');

                if (mode === 'edit') {
                    this.modalTitle = 'Edit Client';
                    this.formAction = `/clients/edit/${data.id}`;
                } else {
                    this.modalTitle = 'Clone Client Rules';
                    this.formAction = '/clients/add';
                    this.formData.expiration = this.calculateDefaultExpiration();
                }
            }
            this.isClientModalOpen = true;
        },

        closeClientModal() {
            this.isClientModalOpen = false;
        },

        submitClientForm(e) {
            e.target.submit();
        },

        // --- Helpers ---

        async autoLookupHostname() {
            // Only auto-lookup if hostname is empty and IP is provided
            if (!this.formData.dns || this.formData.dns.trim() === '') {
                await this.performNsLookup();
            }
        },

        async performNsLookup() {
            if (!this.formData.ip) return;
            this.parsingDNS = true;
            try {
                const res = await fetch(`/api/nslookup?ip=${encodeURIComponent(this.formData.ip)}`);
                const json = await res.json();
                if (json.hostname) {
                    this.formData.dns = json.hostname;
                }
            } catch (e) { console.error(e); }
            this.parsingDNS = false;
        },

        async fetchUrlGroups() {
            try {
                // Use API endpoint instead of static JSON file
                const res = await fetch('/api/templates');
                this.urlGroups = await res.json();
            } catch (e) { console.error('Failed to load templates from API'); }
        },

        openTemplateModal() {
            this.selectedTemplates = [];
            this.templateSearch = '';
            this.isTemplateModalOpen = true;
        },

        applyTemplates() {
            let newDomains = [];
            this.selectedTemplates.forEach(group => {
                if (this.urlGroups[group]) newDomains.push(...this.urlGroups[group]);
            });

            const current = this.formData.domains.split('\n').map(s => s.trim()).filter(Boolean);
            const merged = [...new Set([...current, ...newDomains])];
            this.formData.domains = merged.join('\n');
            this.isTemplateModalOpen = false;
        },

        // --- List Management ---

        openSearchModal() { this.isSearchModalOpen = true; },
        closeSearchModal() { this.isSearchModalOpen = false; },

        reloadList() {
            this.ipFilter = '';
            this.searchContent = '';
            this.filterClients();
        },

        filterClients() {
            const rows = document.querySelectorAll('.client-row');
            const filter = this.ipFilter.toLowerCase();
            rows.forEach(row => {
                const ip = (row.dataset.ip || '').toLowerCase();
                row.style.display = ip.includes(filter) ? '' : 'none';
            });
            this.page = 1;
            this.updatePagination();
        },

        performSearch() {
            const filter = this.searchContent.toLowerCase();
            if (!filter) return;

            const rows = document.querySelectorAll('.client-row');
            rows.forEach(row => {
                let val = '';
                if (this.searchField === 'ip') val = row.dataset.ip;
                else if (this.searchField === 'ticket') val = row.dataset.ticket;
                else if (this.searchField === 'dns') val = row.dataset.dns;

                row.style.display = (val && val.toLowerCase().includes(filter)) ? '' : 'none';
            });

            this.closeSearchModal();
            this.page = 1;
            this.updatePagination();
        },

        updatePagination() {
            const rows = Array.from(document.querySelectorAll('.client-row'));
            const visibleRows = rows.filter(r => r.style.display !== 'none');
            this.totalRows = visibleRows.length;
            this.totalPages = Math.ceil(this.totalRows / this.limit);

            if (this.page > this.totalPages) this.page = this.totalPages || 1;

            this.start = (this.page - 1) * this.limit;
            this.end = this.start + parseInt(this.limit);

            rows.forEach(r => r.classList.add('hidden'));

            visibleRows.forEach((row, index) => {
                if (index >= this.start && index < this.end) {
                    row.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                }
            });
        },

        nextPage() {
            if (this.page < this.totalPages) {
                this.page++;
                this.updatePagination();
            }
        },

        prevPage() {
            if (this.page > 1) {
                this.page--;
                this.updatePagination();
            }
        },

        // --- Deletion ---

        openDeleteModal(id) {
            this.deleteId = id;
            this.isDeleteModalOpen = true;
        },

        openBulkDeleteModal() {
            const checked = document.querySelectorAll('.client-checkbox:checked');
            if (checked.length === 0) {
                alert("Please select at least one client.");
                return;
            }
            this.selectedCount = checked.length;
            this.confirmText = '';
            this.isBulkDeleteModalOpen = true;
        },

        closeBulkDeleteModal() {
            this.isBulkDeleteModalOpen = false;
            this.confirmText = '';
        },

        confirmBulkDelete() {
            if (this.confirmText !== 'confirm') return;
            document.getElementById('delete-form').submit();
        },

        toggleSelectAll(e) {
            const checked = e.target.checked;
            document.querySelectorAll('.client-checkbox').forEach(cb => cb.checked = checked);
            this.updateSelectedCount();
        },

        updateSelectedCount() {
            this.selectedCount = document.querySelectorAll('.client-checkbox:checked').length;
        }
    }));
});
