// اسکریپت‌های ساده برای تعاملات پایه
document.addEventListener('DOMContentLoaded', function() {
    // فعال کردن آیتم‌های منو
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // مدیریت فرم جستجو
    const searchForm = document.querySelector('.search-input');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input');
        const searchButton = searchForm.querySelector('button');
        
        searchButton.addEventListener('click', function(e) {
            if (!searchInput.value.trim()) {
                e.preventDefault();
                alert('لطفاً عبارت جستجو را وارد کنید');
                searchInput.focus();
            }
        });
    }
    
    // نمایش پیام‌ها (در حالت واقعی از Flask flash messages استفاده می‌شود)
    function showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // استایل‌دهی به پیام
        messageDiv.style.position = 'fixed';
        messageDiv.style.top = '20px';
        messageDiv.style.left = '50%';
        messageDiv.style.transform = 'translateX(-50%)';
        messageDiv.style.padding = '15px 20px';
        messageDiv.style.borderRadius = '4px';
        messageDiv.style.zIndex = '1000';
        messageDiv.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        
        if (type === 'success') {
            messageDiv.style.backgroundColor = '#4caf50';
            messageDiv.style.color = 'white';
        } else if (type === 'error') {
            messageDiv.style.backgroundColor = '#f44336';
            messageDiv.style.color = 'white';
        } else {
            messageDiv.style.backgroundColor = '#2196f3';
            messageDiv.style.color = 'white';
        }
        
        document.body.appendChild(messageDiv);
        
        // حذف خودکار پیام پس از 5 ثانیه
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
    
    // نمونه استفاده از تابع نمایش پیام
    // showMessage('عملیات با موفقیت انجام شد', 'success');
});