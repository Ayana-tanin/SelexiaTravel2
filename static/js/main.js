/**
 * SELEXIA Travel - Основной JavaScript файл
 * Содержит общую функциональность для всех страниц
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // Инициализация всех компонентов
    initBackToTop();
    initSmoothScrolling();
    initLazyLoading();
    initTooltips();
    initAnimations();
    initFormValidation();
    initSearchAutocomplete();
    initMobileMenu();
    initNotifications();
    initAuthModals();
    
    console.log('SELEXIA Travel - JavaScript загружен');
});

/**
 * Кнопка "Наверх"
 */
function initBackToTop() {
    const backToTopBtn = document.getElementById('btn-back-to-top');
    
    if (!backToTopBtn) return;
    
    // Показываем/скрываем кнопку при скролле
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
            backToTopBtn.classList.add('fade-in');
        } else {
            backToTopBtn.style.display = 'none';
            backToTopBtn.classList.remove('fade-in');
        }
    });
    
    // Плавная прокрутка наверх при клике
    backToTopBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Плавная прокрутка к якорям
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const offsetTop = target.offsetTop - 80; // Учитываем высоту навигации
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Ленивая загрузка изображений
 */
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * Инициализация тултипов
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Анимации при скролле
 */
function initAnimations() {
    if ('IntersectionObserver' in window) {
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            animationObserver.observe(el);
        });
    }
}

/**
 * Валидация форм
 */
function initFormValidation() {
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Пожалуйста, исправьте ошибки в форме', 'error');
            }
        });
        
        // Валидация в реальном времени
        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('blur', function() {
                validateField(this);
            });
            
            field.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

/**
 * Валидация отдельного поля
 */
function validateField(field) {
    const value = field.value.trim();
    const rules = field.dataset.rules;
    
    if (!rules) return true;
    
    const ruleList = rules.split('|');
    let isValid = true;
    let errorMessage = '';
    
    ruleList.forEach(rule => {
        if (rule === 'required' && !value) {
            isValid = false;
            errorMessage = 'Это поле обязательно для заполнения';
        } else if (rule === 'email' && value && !isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Введите корректный email адрес';
        } else if (rule === 'phone' && value && !isValidPhone(value)) {
            isValid = false;
            errorMessage = 'Введите корректный номер телефона';
        } else if (rule.startsWith('min:') && value) {
            const minLength = parseInt(rule.split(':')[1]);
            if (value.length < minLength) {
                isValid = false;
                errorMessage = `Минимальная длина: ${minLength} символов`;
            }
        }
    });
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

/**
 * Валидация всей формы
 */
function validateForm(form) {
    let isValid = true;
    
    form.querySelectorAll('input, textarea, select').forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Показать ошибку поля
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Очистить ошибку поля
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Валидация email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Валидация телефона
 */
function isValidPhone(phone) {
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

/**
 * Автодополнение поиска
 */
function initSearchAutocomplete() {
    const searchInputs = document.querySelectorAll('[data-autocomplete]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        let searchResults;
        
        // Создаем контейнер для результатов
        searchResults = document.createElement('div');
        searchResults.className = 'search-results position-absolute bg-white border rounded shadow-sm';
        searchResults.style.display = 'none';
        searchResults.style.zIndex = '1000';
        searchResults.style.width = '100%';
        searchResults.style.top = '100%';
        
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(searchResults);
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query, input, searchResults);
            }, 300);
        });
        
        // Скрываем результаты при клике вне поля
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    });
}

/**
 * Выполнение поиска
 */
function performSearch(query, input, resultsContainer) {
    const searchUrl = input.dataset.searchUrl || '/api/search-autocomplete/';
    
    fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                displaySearchResults(data.results, resultsContainer, input);
            } else {
                resultsContainer.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            resultsContainer.style.display = 'none';
        });
}

/**
 * Отображение результатов поиска
 */
function displaySearchResults(results, container, input) {
    container.innerHTML = results.map(result => `
        <div class="search-result-item p-2 border-bottom" style="cursor: pointer;">
            <div class="fw-bold">${result.label}</div>
            <small class="text-muted">${result.type}</small>
        </div>
    `).join('');
    
    // Добавляем обработчики кликов
    container.querySelectorAll('.search-result-item').forEach((item, index) => {
        item.addEventListener('click', function() {
            input.value = results[index].value;
            container.style.display = 'none';
            
            if (results[index].url) {
                window.location.href = results[index].url;
            }
        });
    });
    
    container.style.display = 'block';
}

/**
 * Мобильное меню
 */
function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.navbar-toggler');
    const mobileMenu = document.querySelector('.navbar-collapse');
    
    if (!mobileMenuToggle || !mobileMenu) return;
    
    // Закрываем меню при клике на ссылку
    mobileMenu.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                mobileMenu.classList.remove('show');
            }
        });
    });
    
    // Закрываем меню при клике вне его
    document.addEventListener('click', function(e) {
        if (!mobileMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
            mobileMenu.classList.remove('show');
        }
    });
}

/**
 * Система уведомлений
 */
function initNotifications() {
    // Создаем контейнер для уведомлений
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(notificationContainer);
    }
}

/**
 * Показать уведомление
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        initNotifications();
    }
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Автоматически скрываем через указанное время
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    // Удаляем при клике на кнопку закрытия
    notification.querySelector('.btn-close').addEventListener('click', function() {
        notification.remove();
    });
}

/**
 * AJAX запросы
 */
function makeAjaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin'
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Добавляем CSRF токен для POST запросов
    if (finalOptions.method === 'POST') {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            finalOptions.headers['X-CSRFToken'] = csrfToken;
        }
    }
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

/**
 * Загрузка файлов
 */
function uploadFile(file, uploadUrl, onProgress = null) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('file', file);
        
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable && onProgress) {
                const percentComplete = (e.loaded / e.total) * 100;
                onProgress(percentComplete);
            }
        });
        
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (e) {
                    reject(new Error('Invalid JSON response'));
                }
            } else {
                reject(new Error(`Upload failed with status: ${xhr.status}`));
            }
        });
        
        xhr.addEventListener('error', function() {
            reject(new Error('Upload failed'));
        });
        
        xhr.open('POST', uploadUrl);
        
        // Добавляем CSRF токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }
        
        xhr.send(formData);
    });
}

/**
 * Утилиты для работы с датами
 */
const DateUtils = {
    /**
     * Форматирование даты
     */
    formatDate(date, format = 'DD.MM.YYYY') {
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        
        return format
            .replace('DD', day)
            .replace('MM', month)
            .replace('YYYY', year);
    },
    
    /**
     * Проверка, является ли дата сегодняшней
     */
    isToday(date) {
        const today = new Date();
        const checkDate = new Date(date);
        
        return today.toDateString() === checkDate.toDateString();
    },
    
    /**
     * Проверка, является ли дата вчерашней
     */
    isYesterday(date) {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        const checkDate = new Date(date);
        
        return yesterday.toDateString() === checkDate.toDateString();
    },
    
    /**
     * Получение относительного времени
     */
    getRelativeTime(date) {
        const now = new Date();
        const checkDate = new Date(date);
        const diffInSeconds = Math.floor((now - checkDate) / 1000);
        
        if (diffInSeconds < 60) {
            return 'только что';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} мин. назад`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} ч. назад`;
        } else if (diffInSeconds < 2592000) {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} дн. назад`;
        } else {
            return this.formatDate(date);
        }
    }
};

/**
 * Утилиты для работы с числами
 */
const NumberUtils = {
    /**
     * Форматирование цены
     */
    formatPrice(price, currency = 'USD') {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: currency
        }).format(price);
    },
    
    /**
     * Форматирование больших чисел
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
};

/**
 * Утилиты для работы с URL
 */
const URLUtils = {
    /**
     * Получение параметров URL
     */
    getQueryParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        
        for (const [key, value] of params) {
            result[key] = value;
        }
        
        return result;
    },
    
    /**
     * Установка параметров URL
     */
    setQueryParams(params) {
        const url = new URL(window.location);
        
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.set(key, params[key]);
            } else {
                url.searchParams.delete(key);
            }
        });
        
        window.history.pushState({}, '', url);
    },
    
    /**
     * Добавление параметра к URL
     */
    addQueryParam(key, value) {
        const url = new URL(window.location);
        url.searchParams.set(key, value);
        window.history.pushState({}, '', url);
    }
};

/**
 * Утилиты для работы с localStorage
 */
const StorageUtils = {
    /**
     * Сохранение данных
     */
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Error saving to localStorage:', e);
            return false;
        }
    },
    
    /**
     * Получение данных
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    },
    
    /**
     * Удаление данных
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Error removing from localStorage:', e);
            return false;
        }
    },
    
    /**
     * Очистка всех данных
     */
    clear() {
        try {
            localStorage.clear();
            return true;
        } catch (e) {
            console.error('Error clearing localStorage:', e);
            return false;
        }
    }
};

/**
 * Экспорт утилит в глобальную область
 */
window.SELEXIA = {
    showNotification,
    makeAjaxRequest,
    uploadFile,
    DateUtils,
    NumberUtils,
    URLUtils,
    StorageUtils
};

/**
 * Инициализация модальных окон аутентификации
 */
function initAuthModals() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignupSubmit);
    }
    
    // Обработка успешной аутентификации
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'success') {
        showNotification('Успешная аутентификация!', 'success');
    }
}

/**
 * Обработка отправки формы входа
 */
function handleLoginSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Показываем состояние загрузки
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Вход...';
    
    // Отправляем форму
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.redirected) {
            // Успешный вход, перенаправляем
            window.location.href = response.url;
        } else if (response.ok) {
            // Проверяем ответ
            return response.text();
        } else {
            throw new Error('Ошибка входа');
        }
    })
    .then(html => {
        if (html) {
            // Показываем ошибки валидации
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            const errors = tempDiv.querySelectorAll('.alert-danger, .invalid-feedback');
            
            if (errors.length > 0) {
                errors.forEach(error => {
                    showNotification(error.textContent, 'error');
                });
            } else {
                // Успешный вход
                showNotification('Успешный вход!', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        showNotification('Ошибка входа. Попробуйте еще раз.', 'error');
    })
    .finally(() => {
        // Восстанавливаем кнопку
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

/**
 * Обработка отправки формы регистрации
 */
function handleSignupSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Показываем состояние загрузки
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Регистрация...';
    
    // Отправляем форму
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.redirected) {
            // Успешная регистрация, перенаправляем
            window.location.href = response.url;
        } else if (response.ok) {
            // Проверяем ответ
            return response.text();
        } else {
            throw new Error('Ошибка регистрации');
        }
    })
    .then(html => {
                    if (html) {
                // Показываем ошибки валидации
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                const errors = tempDiv.querySelectorAll('.alert-danger, .invalid-feedback');
                
                if (errors.length > 0) {
                    errors.forEach(error => {
                        showNotification(error.textContent, 'error');
                    });
                } else {
                    // Успешная регистрация
                    showNotification('Успешная регистрация!', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            }
    })
    .catch(error => {
        console.error('Signup error:', error);
        showNotification('Ошибка регистрации. Попробуйте еще раз.', 'error');
    })
    .finally(() => {
        // Восстанавливаем кнопку
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}
