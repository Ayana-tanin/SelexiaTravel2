# selexia_travel/urls.py (основные URL без Vue.js)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

# Импортируем views
from . import views

# API URL patterns (не зависят от языка)
api_urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Кастомная социальная регистрация
    path('accounts/social/signup/', views.social_signup_view, name='social_signup'),
    
    # Django Allauth
    path('accounts/', include('allauth.urls')),
    
    # DRF API
    path('api/', include('api.urls')),
]

# Основные страницы (зависят от языка)
page_urlpatterns = [
    # Главная страница
    path('', views.home_view, name='home'),
    

    
    # Каталог и детальные страницы
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('excursion/<slug:slug>/', views.ExcursionDetailView.as_view(), name='excursion_detail'),
    
    # Страницы стран и городов
    path('country/<slug:slug>/', views.CountryDetailView.as_view(), name='country_detail'),
    
    # Пользовательские страницы
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Gmail интеграция
    path('gmail/connect/', views.connect_gmail_view, name='connect_gmail'),
    path('gmail/callback/', views.gmail_callback_view, name='gmail_callback'),
    path('gmail/sync/', views.sync_gmail_profile_view, name='sync_gmail_profile'),
    path('gmail/disconnect/', views.disconnect_gmail_view, name='disconnect_gmail'),
    
    # Пользовательские разделы
    path('my/bookings/', views.bookings_view, name='bookings'),
    path('my/reviews/', views.user_reviews_view, name='user_reviews'),
    
    # Формы
    path('booking/submit/', views.submit_booking, name='submit_booking'),
    path('review/submit/', views.submit_review, name='submit_review'),
    path('review/submit/new/', views.submit_review_new, name='submit_review_new'),
    path('application/submit/', views.submit_application, name='submit_application'),
    
    # Информационные страницы
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
]

# Основные URL patterns
urlpatterns = api_urlpatterns + [
    # Смена языка
    path('i18n/setlang/', set_language, name='set_language'),
] + i18n_patterns(*page_urlpatterns, prefix_default_language=False)

# Обработчики ошибок
handler404 = 'selexia_travel.views.error_404_view'
handler500 = 'selexia_travel.views.error_500_view'

# Обслуживание медиа и статических файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)