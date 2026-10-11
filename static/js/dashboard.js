// Production Monitoring System - Main JavaScript
// ==================================================

// Utility Functions
const utils = {
    // Format date
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    // Format time
    formatTime: (date) => {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },

    // Show notification
    showNotification: (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    // API call helper
    apiCall: async (endpoint, method = 'GET', data = null) => {
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(endpoint, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            utils.showNotification('Error occurred during API call', 'error');
            throw error;
        }
    }
};

// Dashboard Module
const dashboard = {
    init: () => {
        dashboard.setupEventListeners();
        dashboard.loadData();
        dashboard.startAutoRefresh();
    },

    setupEventListeners: () => {
        // Add event listeners here
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                const action = e.target.getAttribute('data-action');
                dashboard.handleAction(action, e.target);
            }
        });
    },

    handleAction: (action, element) => {
        switch (action) {
            case 'delete':
                const id = element.getAttribute('data-id');
                const table = element.getAttribute('data-table');
                dashboard.deleteRecord(table, id);
                break;
            case 'refresh':
                dashboard.loadData();
                break;
            default:
                console.log('Unknown action:', action);
        }
    },

    loadData: async () => {
        try {
            const data = await utils.apiCall('/api/chart-data');
            // Update dashboard with new data
            console.log('Data loaded:', data);
        } catch (error) {
            console.error('Failed to load data:', error);
        }
    },

    deleteRecord: async (table, id) => {
        if (!confirm('Are you sure you want to delete this record?')) return;

        try {
            const result = await utils.apiCall(`/api/delete/${table}/${id}`, 'DELETE');
            if (result.success) {
                utils.showNotification('Record deleted successfully', 'success');
                dashboard.loadData();
            } else {
                utils.showNotification('Failed to delete record', 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
        }
    },

    startAutoRefresh: () => {
        // Refresh data every 60 seconds
        setInterval(() => {
            dashboard.loadData();
        }, 60000);
    }
};

// Form Handler Module
const formHandler = {
    init: () => {
        formHandler.setupFormValidation();
        formHandler.setupFormSubmit();
    },

    setupFormValidation: () => {
        const forms = document.querySelectorAll('.glass-form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!formHandler.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    },

    validateForm: (form) => {
        const inputs = form.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });

        return isValid;
    },

    setupFormSubmit: () => {
        const forms = document.querySelectorAll('.glass-form');
        forms.forEach(form => {
            form.addEventListener('reset', () => {
                form.querySelectorAll('input').forEach(input => {
                    input.classList.remove('error');
                });
            });
        });
    }
};

// Search Module
const search = {
    init: () => {
        document.querySelectorAll('[id$="Search"]').forEach(input => {
            input.addEventListener('input', (e) => {
                search.handleSearch(e.target);
            });
        });
    },

    handleSearch: async (input) => {
        const query = input.value;
        const table = input.id.includes('customer') ? 'customers' : 'production';

        try {
            const results = await utils.apiCall('/api/search', 'POST', {
                query: query,
                table: table
            });

            // Update table with results
            console.log('Search results:', results);
        } catch (error) {
            console.error('Search error:', error);
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize modules based on page
    if (document.querySelector('.stats-grid')) {
        dashboard.init();
    }

    if (document.querySelector('.glass-form')) {
        formHandler.init();
    }

    if (document.querySelector('[id$="Search"]')) {
        search.init();
    }
});

// Sidebar mobile toggle
const setupMobileMenu = () => {
    const sidebar = document.querySelector('.sidebar');
    
    // Add mobile menu button
    if (window.innerWidth <= 768 && !document.querySelector('.mobile-menu-btn')) {
        const btn = document.createElement('button');
        btn.className = 'mobile-menu-btn';
        btn.innerHTML = '<i class="fas fa-bars"></i>';
        btn.onclick = () => sidebar.classList.toggle('active');
        document.querySelector('.header').prepend(btn);
    }

    // Close sidebar when clicking nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }
        });
    });
};

window.addEventListener('load', setupMobileMenu);
window.addEventListener('resize', setupMobileMenu);
