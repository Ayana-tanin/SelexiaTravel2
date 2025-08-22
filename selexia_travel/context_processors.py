from django.conf import settings
from .models import Category, Country, Excursion
from .forms import NewsletterForm, SearchForm


def site_context(request):
    """Глобальный контекст для всех шаблонов"""
    
    try:
        # Популярные категории для меню
        popular_categories = Category.objects.filter(is_featured=True)[:6]
        
        # Популярные страны для меню
        popular_countries = Country.objects.filter(is_popular=True)[:8]
        
        # Статистика сайта
        site_stats = {
            'total_excursions': Excursion.objects.filter(status='published').count(),
            'total_countries': Country.objects.count(),
            'total_categories': Category.objects.count(),
        }
        
        # Формы для быстрого доступа
        newsletter_form = NewsletterForm()
        search_form = SearchForm()
        
        # Информация о компании
        company_info = {
            'name': 'SELEXIA Travel',
            'phone': '+1 (555) 123-4567',
            'email': 'info@selexiatravel.com',
            'address': '123 Travel Street, City, Country',
            'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00',
            'social_links': {
                'facebook': 'https://facebook.com/selexiatravel',
                'instagram': 'https://instagram.com/selexiatravel',
                'twitter': 'https://twitter.com/selexiatravel',
                'youtube': 'https://youtube.com/selexiatravel',
            }
        }
        
        # Количество избранных для аутентифицированных пользователей
        favorites_count = 0
        if request.user.is_authenticated:
            favorites_count = request.user.favorites.count()
        
        return {
            'popular_categories': popular_categories,
            'popular_countries': popular_countries,
            'site_stats': site_stats,
            'newsletter_form': newsletter_form,
            'search_form': search_form,
            'company_info': company_info,
            'favorites_count': favorites_count,
            'MEDIA_URL': settings.MEDIA_URL,
            'STATIC_URL': settings.STATIC_URL,
        }
        
    except Exception as e:
        # В случае ошибки возвращаем базовый контекст
        print(f"Ошибка в контекстном процессоре: {e}")
        return {
            'popular_categories': [],
            'popular_countries': [],
            'site_stats': {
                'total_excursions': 0,
                'total_countries': 0,
                'total_categories': 0,
            },
            'newsletter_form': NewsletterForm(),
            'search_form': SearchForm(),
            'company_info': {
                'name': 'SELEXIA Travel',
                'phone': '+1 (555) 123-4567',
                'email': 'info@selexiatravel.com',
                'address': '123 Travel Street, City, Country',
                'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00',
                'social_links': {
                    'facebook': 'https://facebook.com/selexiatravel',
                    'instagram': 'https://instagram.com/selexiatravel',
                    'twitter': 'https://twitter.com/selexiatravel',
                    'youtube': 'https://youtube.com/selexiatravel',
                }
            },
            'favorites_count': 0,
            'MEDIA_URL': settings.MEDIA_URL,
            'STATIC_URL': settings.STATIC_URL,
        }