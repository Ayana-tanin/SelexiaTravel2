from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаем роутер для API
router = DefaultRouter()
router.register(r'excursions', views.ExcursionViewSet, basename='excursion')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'countries', views.CountryViewSet, basename='country')
router.register(r'cities', views.CityViewSet, basename='city')
router.register(r'categories', views.CategoryViewSet, basename='category')

# Дополнительные URL для специальных эндпоинтов
urlpatterns = [
    # Основные API эндпоинты через роутер
    path('', include(router.urls)),
    
    # Дополнительные эндпоинты
    path('search/', views.ExcursionViewSet.as_view({'get': 'list'}), name='api-search'),
    path('popular/', views.ExcursionViewSet.as_view({'get': 'popular'}), name='api-popular'),
    path('featured/', views.ExcursionViewSet.as_view({'get': 'featured'}), name='api-featured'),
    path('stats/', views.ExcursionViewSet.as_view({'get': 'stats'}), name='api-stats'),
    
    # Избранное - убираем, так как используем отдельные функции
    
    # Отзывы по экскурсии
    path('reviews/by-excursion/', views.ReviewViewSet.as_view({'get': 'by_excursion'}), name='api-reviews-by-excursion'),
    
    # Популярные страны
    path('countries/popular/', views.CountryViewSet.as_view({'get': 'popular'}), name='api-countries-popular'),
    
    # Города по стране
    path('cities/by-country/', views.CityViewSet.as_view({'get': 'by_country'}), name='api-cities-by-country'),
    
    # Рекомендуемые категории
    path('categories/featured/', views.CategoryViewSet.as_view({'get': 'featured'}), name='api-categories-featured'),
    
    # Новые API endpoints для соответствия основному urls.py
    path('excursions/', views.api_excursions, name='api_excursions'),
    path('countries/', views.api_countries, name='api_countries'),
    path('categories/', views.api_categories, name='api_categories'),
    path('cities/', views.api_cities, name='api_cities'),
    path('cities-home/', views.api_cities_for_home, name='api_cities_home'),
    path('favorites/toggle/', views.api_favorites_toggle, name='api_favorites_toggle'),
    path('favorites/', views.api_favorites, name='api_favorites'),
    path('reviews/', views.api_reviews, name='api_reviews'),
    path('contact/', views.api_contact, name='api_contact'),
    path('stats/', views.api_stats, name='api_stats'),
    
    # API для форм
    path('application/submit/', views.submit_application, name='submit_application'),
    path('booking/submit/', views.submit_booking, name='submit_booking'),
    path('review/submit/', views.submit_review, name='submit_review'),
    
    # Отмена бронирования
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Автодополнение и поиск
    path('search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    path('cities-by-country/', views.cities_by_country, name='cities_by_country'),
    
    # Настройки пользователя
    path('settings/notifications/', views.notification_settings, name='api_notification_settings'),
]

# Добавляем API корневой эндпоинт
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    """Корневой эндпоинт API с документацией"""
    return Response({
        'message': 'SELEXIA Travel API',
        'version': 'v1',
        'endpoints': {
            'excursions': reverse('excursion-list', request=request, format=format),
            'favorites': reverse('favorite-list', request=request, format=format),
            'bookings': reverse('booking-list', request=request, format=format),
            'reviews': reverse('review-list', request=request, format=format),
            'countries': reverse('country-list', request=request, format=format),
            'cities': reverse('city-list', request=request, format=format),
            'categories': reverse('category-list', request=request, format=format),
        },
        'documentation': {
            'search': 'GET /api/excursions/?search=query&country=slug&city=slug&category=slug&price_min=100&price_max=1000&rating=4&sort=popular',
            'favorites': 'POST /api/favorites/ {"item_id": 1, "item_type": "excursion"}',
            'bookings': 'POST /api/bookings/ {"excursion": 1, "date": "2024-01-01", "people_count": 2, "contact_phone": "+1234567890", "contact_email": "user@example.com"}',
        }
    })

# Добавляем корневой эндпоинт в начало списка
urlpatterns.insert(0, path('', api_root, name='api-root'))
