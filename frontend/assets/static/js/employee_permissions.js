// Employee Permission Manager - Simple version
(function() {
    'use strict';
    
    console.log('🔐 Permission Manager loaded');
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    function init() {
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
        
        // Only for employees
        if (userInfo.user_type !== 'employee' && userInfo.user_type !== 'staff' && userInfo.user_type !== 'client_user') {
            // Show all modules for non-employees
            document.querySelectorAll('.nav-item[class*="module-"]').forEach(el => {
                el.classList.add('module-visible');
            });
            return;
        }
        
        console.log('🔐 Employee detected - loading permissions...');
        
        // Fetch permissions
        fetch('/api/user-management/user-permissions', {
            method: 'GET',
            credentials: 'include'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.permissions) {
                console.log('✅ Permissions:', data.permissions);
                
                // Show only allowed modules
                const moduleMap = {
                    'dashboard': '.module-dashboard',
                    'sales': '.module-sales',
                    'credit': '.module-credit',
                    'billing': '.module-billing',
                    'invoices': '.module-invoices',
                    'products': '.module-products',
                    'inventory': '.module-inventory',
                    'customers': '.module-customers',
                    'reports': '.module-reports',
                    'settings': '.module-settings'
                };
                
                Object.keys(moduleMap).forEach(module => {
                    if (data.permissions[module] === true) {
                        document.querySelectorAll(moduleMap[module]).forEach(el => {
                            el.classList.add('module-visible');
                        });
                        console.log(`✅ ${module} enabled`);
                    }
                });
            }
        })
        .catch(err => console.error('❌ Permission error:', err));
    }
})();
