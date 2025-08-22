from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Avg, Count, F, Sum
from django.http import JsonResponse, HttpResponse
from .models import Excursion, Review
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime, timedelta
import json
import time
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from . import models

from .models import (
    Excursion, Country, City, Category, Review, ReviewImage, Booking, 
    Favorite, Application, ExcursionImage, User, UserSettings
)
from .forms import (
    ApplicationForm, BookingForm, ReviewForm, 
    ExcursionFilterForm, ContactForm
)


def home_view(request):
    """Главная страница"""
    # Получаем популярные экскурсии с изображениями
    popular_excursions = Excursion.objects.filter(
        status='published', 
        is_popular=True
    ).select_related('city', 'country', 'category').prefetch_related('images')[:6]
    
    # Получаем все страны
    countries = Country.objects.all().prefetch_related('cities')
    

    
    # Получаем категории экскурсий
    categories = Category.objects.all()[:4]
    
    # Получаем последние отзывы
    recent_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('user', 'excursion')[:3]
    
    # Получаем избранное для авторизованных пользователей
    user_favorites = []
    user_favorite_countries = []
    user_favorite_categories = []
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user, excursion__isnull=False).values_list('excursion_id', flat=True)
        user_favorite_countries = Favorite.objects.filter(user=request.user, country__isnull=False).values_list('country_id', flat=True)
        user_favorite_categories = Favorite.objects.filter(user=request.user, category__isnull=False).values_list('category_id', flat=True)
    
    # Получаем статистику
    stats = {
        'excursions_count': Excursion.objects.filter(status='published').count(),
        'countries_count': Country.objects.count(),
        'reviews_count': Review.objects.filter(is_approved=True).count(),
        'happy_customers': User.objects.filter(bookings__status='completed').distinct().count(),
    }
    
    context = {
        'popular_excursions': popular_excursions,
        'countries': countries,
        'categories': categories,
        'recent_reviews': recent_reviews,
        'stats': stats,
        'user_favorites': user_favorites,
        'user_favorite_countries': user_favorite_countries,
        'user_favorite_categories': user_favorite_categories,
        'application_form': ApplicationForm(),
    }
    
    return render(request, 'home.html', context)





class CatalogView(ListView):
    """Каталог экскурсий"""
    model = Excursion
    template_name = 'catalog.html'
    context_object_name = 'excursions'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Excursion.objects.filter(status='published').select_related(
            'city', 'country', 'category'
        ).prefetch_related('images')
        
        # Поиск
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title_ru__icontains=search) |
                Q(title_en__icontains=search) |
                Q(description_ru__icontains=search) |
                Q(description_en__icontains=search) |
                Q(city__name_ru__icontains=search) |
                Q(city__name_en__icontains=search) |
                Q(country__name_ru__icontains=search) |
                Q(country__name_en__icontains=search)
            )
        
        # Фильтры
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country__slug=country)
        
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__slug=city)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Фильтр по цене
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Фильтр по рейтингу
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating__gte=float(rating))
        
        # Сортировка
        sort = self.request.GET.get('sort', 'popular')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        else:  # popular
            queryset = queryset.order_by('-is_popular', '-views_count', '-rating')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        context['categories'] = Category.objects.all()
        context['filter_form'] = ExcursionFilterForm(self.request.GET)
        context['current_filters'] = self.request.GET
        
        # Добавляем контекст избранного для авторизованных пользователей
        if self.request.user.is_authenticated:
            user_favorites = Favorite.objects.filter(user=self.request.user, excursion__isnull=False).values_list('excursion_id', flat=True)
            context['user_favorites'] = user_favorites
        else:
            context['user_favorites'] = []
        
        return context


class ExcursionDetailView(DetailView):
    """Детальная страница экскурсии"""
    model = Excursion
    template_name = 'excursion_detail.html'
    context_object_name = 'excursion'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Excursion.objects.filter(status='published').select_related(
            'city', 'country', 'category'
        ).prefetch_related('images', 'reviews__user')
    
    def get_object(self):
        excursion = super().get_object()
        # Увеличиваем счетчик просмотров
        Excursion.objects.filter(pk=excursion.pk).update(views_count=F('views_count') + 1)
        return excursion
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        excursion = self.object
        
        # Добавляем сегодняшнюю дату для формы бронирования
        from datetime import date
        context['today'] = date.today()
        
        # Отзывы
        reviews = excursion.reviews.filter(is_approved=True).select_related('user').prefetch_related('images')
        context['reviews'] = reviews[:10]  # Показываем только первые 10
        context['reviews_count'] = reviews.count()
        
        # Проверяем права пользователя на экскурсию
        user_can_review = False
        user_has_reviewed = False
        user_has_booking = False
        
        if self.request.user.is_authenticated:
            user_can_review = self.request.user.can_review_excursion(excursion)
            user_has_reviewed = self.request.user.has_reviewed_excursion(excursion)
            user_has_booking = Booking.objects.filter(
                user=self.request.user,
                excursion=excursion,
                status__in=['confirmed', 'completed']
            ).exists()
        
        context['user_can_review'] = user_can_review
        context['user_has_reviewed'] = user_has_reviewed
        context['user_has_booking'] = user_has_booking
        
        # Статистика рейтинга
        if reviews.exists():
            rating_breakdown = {}
            for i in range(1, 6):
                count = reviews.filter(rating=i).count()
                percentage = (count / reviews.count()) * 100 if reviews.count() > 0 else 0
                rating_breakdown[i] = {'count': count, 'percentage': percentage}
            context['rating_breakdown'] = rating_breakdown
            
            # Последние отзывы для сайдбара
            context['recent_reviews'] = reviews[:3]
        
        # Похожие экскурсии
        context['similar_excursions'] = Excursion.objects.filter(
            status='published',
            category=excursion.category
        ).exclude(pk=excursion.pk)[:4]
        
        # Формы
        context['booking_form'] = BookingForm(user=self.request.user)
        context['review_form'] = ReviewForm()
        
        # Добавляем пользователя в контекст
        context['user'] = self.request.user
        
        # Проверяем, добавлена ли экскурсия в избранное
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                excursion=excursion
            ).exists()
            
            # Получаем список ID избранных экскурсий пользователя
            user_favorite_excursions = Favorite.objects.filter(
                user=self.request.user,
                excursion__isnull=False
            ).values_list('excursion_id', flat=True)
            context['user_favorite_excursions'] = user_favorite_excursions
        else:
            context['is_favorite'] = False
            context['user_favorite_excursions'] = []
        
        return context


@login_required
def dashboard_view(request):
    """Личный кабинет пользователя"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    # Обработка POST-запросов для обновления настроек
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'update_settings':
                setting = data.get('setting')
                value = data.get('value')
                
                # Получаем или создаем настройки пользователя
                try:
                    user_settings = request.user.settings
                except:
                    from .models import UserSettings
                    user_settings = UserSettings.objects.create(user=request.user)
                
                # Обновляем соответствующую настройку
                if setting == 'email':
                    user_settings.email_notifications = value
                elif setting == 'push':
                    user_settings.push_notifications = value
                
                user_settings.save()
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Неизвестное действие'})
                
        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Получаем статистику пользователя
    user_bookings = Booking.objects.filter(user=request.user).count()
    user_favorites = Favorite.objects.filter(user=request.user).count()
    user_reviews = Review.objects.filter(user=request.user).count()
    
    # Последние бронирования с деталями
    recent_bookings = Booking.objects.filter(user=request.user).select_related(
        'excursion__country', 'excursion__city', 'excursion__category'
    ).prefetch_related('excursion__images').order_by('-created_at')[:10]
    
    # Последние отзывы с деталями
    recent_reviews = Review.objects.filter(user=request.user).select_related(
        'excursion__country', 'excursion__city'
    ).prefetch_related('excursion__images').order_by('-created_at')[:10]
    
    # Избранные экскурсии
    favorite_excursions = Favorite.objects.filter(
        user=request.user, 
        excursion__isnull=False
    ).select_related(
        'excursion__country', 'excursion__city', 'excursion__category'
    ).prefetch_related('excursion__images')[:10]
    
    # Статистика по статусам бронирований
    booking_stats = {
        'pending': Booking.objects.filter(user=request.user, status='pending').count(),
        'confirmed': Booking.objects.filter(user=request.user, status='confirmed').count(),
        'completed': Booking.objects.filter(user=request.user, status='completed').count(),
        'cancelled': Booking.objects.filter(user=request.user, status='cancelled').count(),
    }
    
    # Общая сумма потраченная на экскурсии
    total_spent = Booking.objects.filter(
        user=request.user, 
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Получаем настройки пользователя
    try:
        user_settings = request.user.settings
    except:
        # Если настройки не существуют, создаем их
        from .models import UserSettings
        user_settings = UserSettings.objects.create(user=request.user)
    
    # Дополнительные данные для dashboard
    # Получаем все отзывы пользователя для отображения
    all_user_reviews = Review.objects.filter(user=request.user).select_related(
        'excursion__country', 'excursion__city'
    ).prefetch_related('excursion__images').order_by('-created_at')
    
    # Получаем все бронирования пользователя для статистики
    all_user_bookings = Booking.objects.filter(user=request.user).select_related(
        'excursion__country', 'excursion__city'
    ).order_by('-created_at')
    
    # Статистика по месяцам
    from django.utils import timezone
    from datetime import datetime, timedelta
    import calendar
    
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Бронирования за текущий месяц
    current_month_bookings = all_user_bookings.filter(
        created_at__month=current_month,
        created_at__year=current_year
    ).count()
    
    # Бронирования за предыдущий месяц
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    prev_month_bookings = all_user_bookings.filter(
        created_at__month=prev_month,
        created_at__year=prev_year
    ).count()
    
    context = {
        'user': request.user,
        'user_bookings': user_bookings,
        'user_favorites': user_favorites,
        'user_reviews': user_reviews,
        'recent_bookings': recent_bookings,
        'recent_reviews': recent_reviews,
        'all_user_reviews': all_user_reviews,
        'all_user_bookings': all_user_bookings,
        'favorite_excursions': favorite_excursions,
        'booking_stats': booking_stats,
        'total_spent': total_spent,
        'user_settings': user_settings,
        'current_month_bookings': current_month_bookings,
        'prev_month_bookings': prev_month_bookings,
        'current_month_name': calendar.month_name[current_month],
        'prev_month_name': calendar.month_name[prev_month],
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def favorites_view(request):
    """Страница избранных элементов"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    # Получаем все избранные элементы пользователя
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'excursion__country', 'excursion__city', 'excursion__category',
        'category', 'country'
    ).prefetch_related('excursion__images')
    
    # Разделяем по типам
    favorite_excursions = [fav.excursion for fav in favorites if fav.excursion and fav.excursion.status == 'published']
    favorite_categories = [fav.category for fav in favorites if fav.category]
    favorite_countries = [fav.country for fav in favorites if fav.country]
    
    # Получаем количество избранного для каждого типа
    excursions_count = len(favorite_excursions)
    categories_count = len(favorite_categories)
    countries_count = len(favorite_countries)
    
    context = {
        'excursions': favorite_excursions,
        'categories': favorite_categories,
        'countries': favorite_countries,
        'favorites_count': favorites.count(),
        'excursions_count': excursions_count,
        'categories_count': categories_count,
        'countries_count': countries_count,
    }
    
    return render(request, 'favorites.html', context)


def bookings_view(request):
    """Мои бронирования"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    bookings = Booking.objects.filter(user=request.user).select_related(
        'excursion__country', 'excursion__city'
    ).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    
    return render(request, 'users/bookings.html', context)


def user_reviews_view(request):
    """Мои отзывы"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    reviews = Review.objects.filter(user=request.user).select_related(
        'excursion'
    ).order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    
    return render(request, 'users/reviews.html', context)


@csrf_exempt
def submit_application(request):
    """Обработка заявки с главной страницы"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            messages.success(request, _('Ваша заявка отправлена! Мы свяжемся с вами в ближайшее время.'))
            
            # Здесь можно добавить отправку в AmoCRM
            # send_to_amocrm(application)
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
@csrf_exempt
def submit_booking(request):
    """Обработка бронирования"""
    print(f"DEBUG: ===== НАЧАЛО submit_booking =====")
    print(f"DEBUG: Метод запроса: {request.method}")
    print(f"DEBUG: URL: {request.path}")
    print(f"DEBUG: GET параметры: {request.GET}")
    print(f"DEBUG: POST параметры: {request.POST}")
    print(f"DEBUG: Content-Type: {request.content_type}")
    print(f"DEBUG: Пользователь: {request.user}")
    print(f"DEBUG: Пользователь аутентифицирован: {request.user.is_authenticated}")
    
    if request.method == 'POST':
        print(f"DEBUG: Получены данные формы: {request.POST}")
        print(f"DEBUG: Пользователь: {request.user}")
        print(f"DEBUG: Пользователь ID: {request.user.id if request.user else None}")
        print(f"DEBUG: Аутентифицирован: {request.user.is_authenticated}")
        print(f"DEBUG: Тип пользователя: {type(request.user)}")
        print(f"DEBUG: Атрибуты пользователя: {dir(request.user) if request.user else 'None'}")
        
        # Создаем форму с данными пользователя
        form = BookingForm(request.POST, user=request.user)
        print(f"DEBUG: Форма создана: {form}")
        print(f"DEBUG: Поля формы: {form.fields.keys()}")
        print(f"DEBUG: Данные формы: {form.data}")
        print(f"DEBUG: Форма валидна: {form.is_valid()}")
        
        if form.is_valid():
            print(f"DEBUG: Данные формы: {form.cleaned_data}")
            
            try:
                # Создаем бронирование
                booking = form.save(commit=False)
                print(f"DEBUG: Объект бронирования создан (ID: {booking.id if booking.id else 'не сохранен'})")
                print(f"DEBUG: Excursion ID: {booking.excursion_id}")
                print(f"DEBUG: Date: {booking.date}")
                print(f"DEBUG: People count: {booking.people_count}")
                
                # СРАЗУ устанавливаем пользователя, чтобы избежать ошибок валидации
                booking.user = request.user
                print(f"DEBUG: Пользователь установлен: {request.user}")
                print(f"DEBUG: Пользователь ID: {request.user.id}")
                
                booking.status = 'pending'  # Устанавливаем статус по умолчанию
                
                # Проверяем, что пользователь установлен
                print(f"DEBUG: Устанавливаем пользователя: {request.user}")
                print(f"DEBUG: Пользователь ID: {request.user.id}")
                print(f"DEBUG: Пользователь аутентифицирован: {request.user.is_authenticated}")
                print(f"DEBUG: Booking.user после установки: {booking.user}")
                print(f"DEBUG: Booking.user ID: {booking.user.id if booking.user else None}")
                
                # Устанавливаем цену экскурсии (без умножения на количество человек)
                excursion = booking.excursion
                print(f"DEBUG: Экскурсия: {excursion}")
                print(f"DEBUG: Цена экскурсии: {excursion.price}")
                print(f"DEBUG: Количество человек: {booking.people_count}")
                
                booking.total_price = excursion.price  # Цена за экскурсию, не за человека
                print(f"DEBUG: Цена экскурсии: {booking.total_price}")
                
                print(f"DEBUG: Создаем бронирование: {booking.excursion.title_ru}, {booking.date}, {booking.people_count} чел., цена: {booking.total_price}")
                print(f"DEBUG: Все данные бронирования перед сохранением:")
                print(f"DEBUG: - excursion: {booking.excursion}")
                print(f"DEBUG: - user: {booking.user}")
                print(f"DEBUG: - date: {booking.date}")
                print(f"DEBUG: - people_count: {booking.people_count}")
                print(f"DEBUG: - total_price: {booking.total_price}")
                print(f"DEBUG: - status: {booking.status}")
                print(f"DEBUG: - contact_phone: {booking.contact_phone}")
                print(f"DEBUG: - contact_email: {booking.contact_email}")
                
                # Финальная проверка перед сохранением
                if not booking.user:
                    print(f"DEBUG: ОШИБКА: Пользователь не установлен перед сохранением!")
                    return JsonResponse({
                        'success': False, 
                        'error': 'Ошибка: пользователь не установлен'
                    }, status=500)
                
                # Дополнительная валидация после установки пользователя
                if not booking.excursion:
                    print(f"DEBUG: ОШИБКА: Экскурсия не установлена!")
                    return JsonResponse({
                        'success': False, 
                        'error': 'Ошибка: экскурсия не установлена'
                    }, status=500)
                
                if not booking.date:
                    print(f"DEBUG: ОШИБКА: Дата не установлена!")
                    return JsonResponse({
                        'success': False, 
                        'error': 'Ошибка: дата не установлена'
                    }, status=500)
                
                if not booking.people_count or booking.people_count <= 0:
                    print(f"DEBUG: ОШИБКА: Количество человек не установлено!")
                    return JsonResponse({
                        'success': False, 
                        'error': 'Ошибка: количество человек должно быть больше 0'
                    }, status=500)
                
                # Проверяем, что дата не в прошлом
                from django.utils import timezone
                if booking.date < timezone.now().date():
                    print(f"DEBUG: ОШИБКА: Дата в прошлом!")
                    return JsonResponse({
                        'success': False, 
                        'error': 'Ошибка: дата не может быть в прошлом'
                    }, status=500)
                
                # Проверяем, что количество человек не превышает максимум
                if booking.people_count > booking.excursion.max_people:
                    print(f"DEBUG: ОШИБКА: Слишком много человек!")
                    return JsonResponse({
                        'success': False, 
                        'error': f'Ошибка: максимальное количество человек: {booking.excursion.max_people}'
                    }, status=500)
                
                print(f"DEBUG: Все проверки пройдены, сохраняем бронирование...")
                
                # Сохраняем бронирование
                try:
                    booking.save()
                    print(f"DEBUG: Бронирование сохранено с ID: {booking.id}")
                    # print(f"DEBUG: Бронирование в БД: {Booking.objects.get(id=booking.id)}")  # Временно отключено
                except Exception as e:
                    print(f"DEBUG: Ошибка при сохранении бронирования: {e}")
                    print(f"DEBUG: Тип ошибки: {type(e)}")
                    import traceback
                    print(f"DEBUG: Traceback: {traceback.format_exc()}")
                    
                    return JsonResponse({
                        'success': False, 
                        'error': f'Ошибка при сохранении бронирования: {str(e)}'
                    }, status=500)
                
                messages.success(request, _('Ваше бронирование отправлено! Мы свяжемся с вами для подтверждения.'))
                
                # Отправляем email уведомления
                try:
                    send_booking_notifications(booking)
                    print(f"DEBUG: Email уведомления отправлены")
                except Exception as e:
                    print(f"DEBUG: Ошибка отправки email: {e}")
                
                # Здесь можно добавить отправку в AmoCRM
                # send_booking_to_amocrm(booking)
                
                print(f"DEBUG: ===== КОНЕЦ submit_booking (успешно) =====")
                return JsonResponse({'success': True, 'redirect': reverse('bookings')})
                
            except Exception as e:
                print(f"DEBUG: Ошибка при сохранении бронирования: {e}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                print(f"DEBUG: ===== КОНЕЦ submit_booking (ошибка) =====")
                return JsonResponse({'success': False, 'error': f'Ошибка при сохранении: {str(e)}'})
        else:
            print(f"DEBUG: Ошибки формы: {form.errors}")
            print(f"DEBUG: Невалидные поля: {form.non_field_errors()}")
            for field, errors in form.errors.items():
                print(f"DEBUG: Поле {field}: {errors}")
            print(f"DEBUG: ===== КОНЕЦ submit_booking (ошибки валидации) =====")
            return JsonResponse({'success': False, 'errors': form.errors})
    
    print(f"DEBUG: Запрос не POST, возвращаем 'Invalid method'")
    print(f"DEBUG: ===== КОНЕЦ submit_booking (Invalid method) =====")
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
@csrf_exempt
def submit_review(request):
    """Обработка отзыва"""
    if request.method == 'POST':
        print(f"DEBUG: Получены данные отзыва: {request.POST}")
        print(f"DEBUG: Получены файлы: {request.FILES}")
        
        form = ReviewForm(request.POST, request.FILES)
        print(f"DEBUG: Форма отзыва валидна: {form.is_valid()}")
        
        if form.is_valid():
            print(f"DEBUG: Данные формы отзыва: {form.cleaned_data}")
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            print(f"DEBUG: Отзыв сохранен с ID: {review.id}")
            
            # Обрабатываем фотографии
            photos = request.FILES.getlist('photos')
            print(f"DEBUG: Получено файлов: {len(photos)}")
            
            if photos:
                print(f"DEBUG: Обрабатываем {len(photos)} фотографий")
                for i, photo in enumerate(photos):
                    print(f"DEBUG: Фото {i+1}: {photo.name}, размер: {photo.size}")
                    try:
                        from .models import ReviewImage
                        ReviewImage.objects.create(review=review, image=photo)
                        print(f"DEBUG: Фото {i+1} сохранено успешно")
                    except Exception as e:
                        print(f"DEBUG: Ошибка сохранения фото {i+1}: {e}")
                print(f"DEBUG: Все фотографии обработаны")
            else:
                print(f"DEBUG: Фотографии не найдены в request.FILES")
                print(f"DEBUG: Доступные ключи: {list(request.FILES.keys())}")
                # Попробуем альтернативный способ
                if 'photos' in request.FILES:
                    single_photo = request.FILES['photos']
                    print(f"DEBUG: Найден одиночный файл: {single_photo.name}")
                    try:
                        from .models import ReviewImage
                        ReviewImage.objects.create(review=review, image=single_photo)
                        print(f"DEBUG: Одиночное фото сохранено")
                    except Exception as e:
                        print(f"DEBUG: Ошибка сохранения одиночного фото: {e}")
            
            # Обновляем рейтинг экскурсии
            excursion = review.excursion
            avg_rating = excursion.reviews.filter(is_approved=True).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating']
            excursion.rating = avg_rating or 0
            excursion.reviews_count = excursion.reviews.filter(is_approved=True).count()
            excursion.save()
            print(f"DEBUG: Рейтинг экскурсии обновлен: {excursion.rating}")
            
            messages.success(request, _('Спасибо за ваш отзыв!'))
            return JsonResponse({'success': True})
        else:
            print(f"DEBUG: Ошибки формы отзыва: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
@csrf_exempt
def toggle_favorite(request):
    """Добавление/удаление из избранного"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            item_type = data.get('item_type', 'excursion')
            
            print(f"DEBUG: toggle_favorite called with item_id={item_id}, item_type={item_type}")
            print(f"DEBUG: request.body = {request.body}")
            print(f"DEBUG: data = {data}")
            
            if item_type == 'excursion':
                item = get_object_or_404(Excursion, id=item_id, status='published')
                # Проверяем, есть ли уже в избранном
                existing_favorite = Favorite.objects.filter(user=request.user, excursion=item).first()
                if existing_favorite:
                    existing_favorite.delete()
                    is_favorite = False
                    print(f"DEBUG: Removed from favorites")
                else:
                    Favorite.objects.create(user=request.user, excursion=item, item_type='excursion')
                    is_favorite = True
                    print(f"DEBUG: Added to favorites")
            elif item_type == 'category':
                item = get_object_or_404(Category, id=item_id)
                existing_favorite = Favorite.objects.filter(user=request.user, category=item).first()
                if existing_favorite:
                    existing_favorite.delete()
                    is_favorite = False
                else:
                    Favorite.objects.create(user=request.user, category=item, item_type='category')
                    is_favorite = True
            elif item_type == 'country':
                item = get_object_or_404(Country, id=item_id)
                existing_favorite = Favorite.objects.filter(user=request.user, country=item).first()
                if existing_favorite:
                    existing_favorite.delete()
                    is_favorite = False
                else:
                    Favorite.objects.create(user=request.user, country=item, item_type='country')
                    is_favorite = True
            else:
                return JsonResponse({'success': False, 'error': 'Неизвестный тип элемента'})
            
            favorites_count = request.user.favorites.count()
            print(f"DEBUG: Returning success, is_favorite={is_favorite}, favorites_count={favorites_count}")
            
            return JsonResponse({
                'success': True,
                'is_favorite': is_favorite,
                'favorites_count': favorites_count
            })
        except Exception as e:
            print(f"DEBUG: Error in toggle_favorite: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


def search_autocomplete(request):
    """Автодополнение для поиска"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # Поиск по городам
    cities = City.objects.filter(
        Q(name_ru__icontains=query) | Q(name_en__icontains=query)
    )[:5]
    for city in cities:
        results.append({
            'type': 'city',
            'value': city.name_ru,
            'label': f"{city.name_ru}, {city.country.name_ru}",
            'url': reverse('catalog') + f'?city={city.slug}'
        })
    
    # Поиск по странам
    countries = Country.objects.filter(
        Q(name_ru__icontains=query) | Q(name_en__icontains=query)
    )[:5]
    for country in countries:
        results.append({
            'type': 'country',
            'value': country.name_ru,
            'label': country.name_ru,
            'url': reverse('catalog') + f'?country={country.slug}'
        })
    
    # Поиск по категориям
    categories = Category.objects.filter(
        Q(name_ru__icontains=query) | Q(name_en__icontains=query)
    )[:5]
    for category in categories:
        results.append({
            'type': 'category',
            'value': category.name_ru,
            'label': category.name_ru,
            'url': reverse('catalog') + f'?category={category.slug}'
        })
    
    # Поиск по экскурсиям
    excursions = Excursion.objects.filter(
        status='published'
    ).filter(
        Q(title_ru__icontains=query) | Q(title_en__icontains=query)
    )[:5]
    for excursion in excursions:
        results.append({
            'type': 'excursion',
            'value': excursion.title_ru,
            'label': excursion.title_ru,
            'url': excursion.get_absolute_url()
        })
    
    return JsonResponse({'results': results})


def cities_by_country(request):
    """API для получения городов по стране"""
    country_slug = request.GET.get('country')
    if not country_slug:
        return JsonResponse({'cities': []})
    
    try:
        country = Country.objects.get(slug=country_slug)
        cities = country.cities.values('slug', 'name_ru', 'name_en')
        return JsonResponse({'cities': list(cities)})
    except Country.DoesNotExist:
        return JsonResponse({'cities': []})


def contact_view(request):
    """Страница контактов"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Обработка контактной формы
            messages.success(request, _('Ваше сообщение отправлено!'))
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'contact.html', context)


def about_view(request):
    """Страница о компании"""
    context = {
        'team_stats': {
            'years_experience': 10,
            'countries_visited': 50,
            'happy_clients': 5000,
            'excursions_conducted': 15000,
        }
    }
    return render(request, 'about.html', context)


class CountryDetailView(DetailView):
    """Детальная страница страны"""
    model = Country
    template_name = 'country_detail.html'
    context_object_name = 'country'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country = self.object
        
        # Города страны
        context['cities'] = country.cities.annotate(
            excursions_count=Count('excursions', filter=Q(excursions__status='published'))
        ).filter(excursions_count__gt=0)
        
        # Популярные экскурсии страны
        context['popular_excursions'] = Excursion.objects.filter(
            status='published',
            country=country
        ).order_by('-is_popular', '-views_count')[:8]
        
        # Статистика
        context['stats'] = {
            'cities_count': country.cities_count,
            'excursions_count': country.excursions.filter(status='published').count(),
        }
        
        return context


def error_404_view(request, exception=None):
    """Обработчик 404 ошибки"""
    return render(request, '404.html', status=404)


def error_500_view(request):
    """Обработчик 500 ошибки"""
    return render(request, '500.html', status=500)


def profile_view(request):
    """Профиль пользователя"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    if request.method == 'POST':
        # Обработка обновления профиля
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('profile')
    
    context = {
        'user': request.user,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile_view(request):
    """Редактирование профиля пользователя"""
    from .forms import UserProfileForm
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль успешно обновлен'))
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


def terms_view(request):
    """Условия использования"""
    context = {
        'terms': 'Условия использования сервиса SELEXIA Travel...'
    }
    
    return render(request, 'terms.html', context)


def privacy_view(request):
    """Политика конфиденциальности"""
    context = {
        'privacy': 'Политика конфиденциальности SELEXIA Travel...'
    }
    
    return render(request, 'privacy.html', context)


def faq_view(request):
    """FAQ страница"""
    context = {
        'faqs': [
            {
                'question': 'Как забронировать экскурсию?',
                'answer': 'Выберите экскурсию, заполните форму бронирования и мы свяжемся с вами для подтверждения.'
            },
            {
                'question': 'Можно ли отменить бронирование?',
                'answer': 'Да, отмена возможна за 24 часа до начала экскурсии. Свяжитесь с нами для отмены.'
            },
            {
                'question': 'Какие документы нужны для экскурсии?',
                'answer': 'Паспорт или документ, удостоверяющий личность. Для некоторых экскурсий может потребоваться виза.'
            },
            {
                'question': 'Как оплатить экскурсию?',
                'answer': 'Оплата производится наличными гиду или банковской картой через наш сайт.'
            },
            {
                'question': 'Что включено в стоимость экскурсии?',
                'answer': 'Услуги гида, транспорт (если указано), входные билеты (если включены).'
            }
        ]
    }
    
    return render(request, 'faq.html', context)


def vue_spa_view(request):
    """Представление для Vue.js Single Page Application"""
    return render(request, 'vue_spa.html')


def excursions_api(request):
    """API для получения списка экскурсий"""
    excursions = Excursion.objects.filter(status='published').select_related('country', 'city', 'category')
    
    # Фильтрация
    country = request.GET.get('country')
    if country:
        excursions = excursions.filter(country__slug=country)
    
    city = request.GET.get('city')
    if city:
        excursions = excursions.filter(city__slug=city)
    
    category = request.GET.get('category')
    if category:
        excursions = excursions.filter(category__slug=category)
    
    # Поиск
    search = request.GET.get('search')
    if search:
        excursions = excursions.filter(
            Q(title_ru__icontains=search) |
            Q(description_ru__icontains=search) |
            Q(city__name_ru__icontains=search) |
            Q(country__name_ru__icontains=search)
        )
    
    # Пагинация
    page = request.GET.get('page', 1)
    paginator = Paginator(excursions, 12)
    try:
        excursions_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        excursions_page = paginator.page(1)
    
    data = {
        'excursions': [
            {
                'id': ex.id,
                'title': ex.title_ru,
                'short_description': ex.short_description_ru,
                'price': float(ex.price),
                'currency': ex.currency,
                'duration': ex.duration,
                'duration_unit': ex.duration_unit,
                'rating': float(ex.rating),
                'reviews_count': ex.reviews_count,
                'slug': ex.slug,
                'country': ex.country.name_ru,
                'city': ex.city.name_ru,
                'main_image': ex.main_image.image.url if ex.main_image else None,
            }
            for ex in excursions_page
        ],
        'total_pages': paginator.num_pages,
        'current_page': excursions_page.number,
        'has_next': excursions_page.has_next(),
        'has_previous': excursions_page.has_previous(),
    }
    
    return JsonResponse(data)


def excursion_detail_api(request, slug):
    """API для получения детальной информации об экскурсии"""
    try:
        excursion = Excursion.objects.select_related('country', 'city', 'category').get(slug=slug, status='published')
        
        # Получаем отзывы
        reviews = Review.objects.filter(excursion=excursion, is_approved=True).select_related('user')
        
        data = {
            'id': excursion.id,
            'title': excursion.title_ru,
            'description': excursion.description_ru,
            'short_description': excursion.short_description_ru,
            'price': float(excursion.price),
            'currency': excursion.currency,
            'duration': excursion.duration,
            'duration_unit': excursion.duration_unit,
            'max_people': excursion.max_people,
            'rating': float(excursion.rating),
            'reviews_count': excursion.reviews_count,
            'views_count': excursion.views_count,
            'slug': excursion.slug,
            'status': excursion.status,
            'country': {
                'name': excursion.country.name_ru,
                'slug': excursion.country.slug,
            },
            'city': {
                'name': excursion.city.name_ru,
                'slug': excursion.city.slug,
            },
            'category': {
                'name': excursion.category.name_ru,
                'slug': excursion.category.slug,
            },
            'program': excursion.program_ru,
            'included': excursion.included_ru,
            'important_info': excursion.important_info_ru,
            'meeting_point': excursion.meeting_point_ru,
            'images': [
                {
                    'url': img.image.url,
                    'caption': img.caption_ru,
                }
                for img in excursion.images.all()
            ],
            'reviews': [
                {
                    'id': review.id,
                    'rating': review.rating,
                    'text': review.text,
                    'created_at': review.created_at.isoformat(),
                    'user': {
                        'name': review.user.full_name,
                        'avatar': review.user.avatar.url if review.user.avatar else None,
                    }
                }
                for review in reviews[:10]  # Только первые 10 отзывов
            ],
        }
        
        return JsonResponse(data)
        
    except Excursion.DoesNotExist:
        return JsonResponse({'error': 'Экскурсия не найдена'}, status=404)


@login_required
def review_detail_api(request, review_id):
    """API для получения деталей отзыва"""
    try:
        review = Review.objects.get(id=review_id, user=request.user)
        data = {
            'id': review.id,
            'rating': review.rating,
            'text': review.text,
            'created_at': review.created_at.isoformat(),
        }
        return JsonResponse(data)
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Отзыв не найден'}, status=404)


@login_required
def update_review(request, review_id):
    """Обновление отзыва"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    try:
        review = Review.objects.get(id=review_id, user=request.user)
        
        # Проверяем, есть ли у пользователя подтвержденная бронь
        if not Booking.objects.filter(
            user=request.user,
            excursion=review.excursion,
            status='confirmed'
        ).exists():
            return JsonResponse({'error': 'У вас нет подтвержденной брони на эту экскурсию'}, status=403)
        
        # Обновляем отзыв
        review.rating = int(request.POST.get('rating', review.rating))
        review.text = request.POST.get('text', review.text)
        review.save()
        
        # Обрабатываем фотографии
        photos = request.FILES.getlist('photos')
        if photos:
            # Удаляем старые фотографии
            review.images.all().delete()
            
            # Добавляем новые
            for photo in photos:
                ReviewImage.objects.create(review=review, image=photo)
        
        return JsonResponse({'success': True, 'message': 'Отзыв успешно обновлен'})
        
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Отзыв не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_review(request, review_id):
    """Удаление отзыва"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    try:
        review = Review.objects.get(id=review_id, user=request.user)
        review.delete()
        return JsonResponse({'success': True, 'message': 'Отзыв успешно удален'})
        
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Отзыв не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def submit_review_new(request):
    """Отправка отзыва с проверкой прав на основе бронирований"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    try:
        # Получаем ID экскурсии
        excursion_id = request.POST.get('excursion')
        if not excursion_id:
            return JsonResponse({'error': 'Не указана экскурсия'}, status=400)
        
        excursion = Excursion.objects.get(id=excursion_id)
        
        # Используем новый метод для проверки прав на отзыв
        if not request.user.can_review_excursion(excursion):
            # Проверяем, есть ли вообще подходящие бронирования
            eligible_bookings = request.user.bookings.filter(
                excursion=excursion,
                status__in=['confirmed', 'completed']
            )
            
            if not eligible_bookings.exists():
                return JsonResponse({
                    'error': 'Для оставления отзыва необходимо иметь подтвержденное или завершенное бронирование на эту экскурсию'
                }, status=403)
            else:
                return JsonResponse({
                    'error': 'Вы уже оставляли отзыв на эту экскурсию'
                }, status=400)
        
        # Получаем данные отзыва
        rating = request.POST.get('rating')
        text = request.POST.get('text', '').strip()
        
        if not rating:
            return JsonResponse({'error': 'Не указан рейтинг'}, status=400)
        
        if not text:
            return JsonResponse({'error': 'Не указан текст отзыва'}, status=400)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({'error': 'Рейтинг должен быть от 1 до 5'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Неверный формат рейтинга'}, status=400)
        
        # Создаем отзыв
        review = Review.objects.create(
            user=request.user,
            excursion=excursion,
            rating=rating,
            text=text
        )
        
        # Обрабатываем фотографии (если есть)
        photos = request.FILES.getlist('photos')
        for photo in photos:
            ReviewImage.objects.create(review=review, image=photo)
        
        # Обновляем рейтинг экскурсии
        excursion.update_rating()
        
        return JsonResponse({
            'success': True, 
            'message': 'Отзыв успешно отправлен',
            'review_id': review.id
        })
        
    except Excursion.DoesNotExist:
        return JsonResponse({'error': 'Экскурсия не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Vue.js HTML шаблоны функции
def catalog_vue(request):
    """
    Каталог экскурсий с Vue.js интеграцией
    """
    # Получаем параметры
    search = request.GET.get('search', '')
    country = request.GET.get('country', '')
    city = request.GET.get('city', '')
    category = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    duration_min = request.GET.get('duration_min', '')
    duration_max = request.GET.get('duration_max', '')
    group_size = request.GET.get('group_size', '')
    rating = request.GET.get('rating', '')
    sort = request.GET.get('sort', 'popular')
    
    # Базовый queryset
    excursions = Excursion.objects.filter(status='published').select_related('city', 'country', 'category').prefetch_related('images')
    
    # Применяем фильтры
    if search:
        excursions = excursions.filter(
            Q(title_ru__icontains=search) |
            Q(description_ru__icontains=search) |
            Q(city__name_ru__icontains=search) |
            Q(country__name_ru__icontains=search)
        )
    
    if country:
        excursions = excursions.filter(country__slug=country)
    
    if city:
        excursions = excursions.filter(city__slug=city)
    
    if category:
        excursions = excursions.filter(category__slug=category)
    
    if price_min:
        excursions = excursions.filter(price__gte=float(price_min))
    
    if price_max:
        excursions = excursions.filter(price__lte=float(price_max))
    
    if duration_min:
        excursions = excursions.filter(duration__gte=int(duration_min))
    
    if duration_max:
        excursions = excursions.filter(duration__lte=int(duration_max))
    
    if group_size:
        excursions = excursions.filter(max_people__gte=int(group_size))
    
    if rating:
        excursions = excursions.filter(rating__gte=float(rating))
    
    # Сортировка
    if sort == 'popular':
        excursions = excursions.order_by('-views_count', '-rating')
    elif sort == 'rating':
        excursions = excursions.order_by('-rating')
    elif sort == 'price_low':
        excursions = excursions.order_by('price')
    elif sort == 'price_high':
        excursions = excursions.order_by('-price')
    elif sort == 'newest':
        excursions = excursions.order_by('-created_at')
    else:
        excursions = excursions.order_by('-created_at')
    
    # Пагинация
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 12)
    paginator = Paginator(excursions, per_page)
    excursions_page = paginator.get_page(page)
    
    # Получаем справочники для фильтров
    countries = Country.objects.all()
    categories = Category.objects.all()
    
    # Сериализуем данные для Vue.js
    excursions_data = []
    for excursion in excursions_page:
        excursion_data = {
            'id': excursion.id,
            'title_ru': excursion.title_ru,
            'description_ru': excursion.description_ru,
            'price': excursion.price,
            'duration': excursion.duration,
            'max_people': excursion.max_people,
            'rating': excursion.rating,
            'reviews_count': excursion.reviews_count,
            'slug': excursion.slug,
            'city': {
                'name_ru': excursion.city.name_ru if excursion.city else '',
                'slug': excursion.city.slug if excursion.city else ''
            } if excursion.city else None,
            'country': {
                'name_ru': excursion.country.name_ru if excursion.country else '',
                'slug': excursion.country.slug if excursion.country else ''
            } if excursion.country else None,
            'category': {
                'name_ru': excursion.category.name_ru if excursion.category else '',
                'slug': excursion.category.slug if excursion.category else ''
            } if excursion.category else None,
            'main_image': {
                'image': excursion.images.first().image.url if excursion.images.exists() else ''
            } if excursion.images.exists() else None
        }
        excursions_data.append(excursion_data)
    
    context = {
        'excursions_data': excursions_data,
        'countries': countries,
        'categories': categories,
        'total_results': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'per_page': per_page,
    }
    
    return render(request, 'catalog_vue.html', context)


def excursion_detail_vue(request, slug):
    """
    Детальная страница экскурсии с Vue.js интеграцией
    """
    excursion = get_object_or_404(Excursion, slug=slug, status='published')
    
    # Увеличиваем счетчик просмотров
    excursion.views_count += 1
    excursion.save()
    
    # Получаем связанные экскурсии
    related_excursions = Excursion.objects.filter(
        status='published',
        category=excursion.category
    ).exclude(id=excursion.id)[:6]
    
    # Получаем отзывы для экскурсии
    reviews = Review.objects.filter(
        excursion=excursion,
        is_approved=True
    ).select_related('user')[:10]
    
    # Сериализуем изображения в JSON строку
    import json
    images_data = []
    for image in excursion.images.all():
        # Исправляем путь к изображению
        image_url = image.image.url if image.image else '/static/images/placeholder.jpg'
        images_data.append({
            'id': image.id,
            'image': image_url,
            'caption_ru': image.caption_ru or '',
            'order': image.order
        })
    
    # Сериализуем отзывы в JSON
    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'id': review.id,
            'text': review.text,
            'rating': review.rating,
            'created_at': review.created_at.strftime('%d.%m.%Y'),
            'user_name': review.user.first_name or review.user.username,
            'user_avatar': review.user.avatar.url if review.user.avatar else None
        })
    
    context = {
        'excursion': excursion,
        'related_excursions': related_excursions,
        'images_data_json': json.dumps(images_data),
        'reviews_data_json': json.dumps(reviews_data),
    }
    
    return render(request, 'excursion_detail_vue.html', context)


# API endpoints для Vue.js HTML
@csrf_exempt
def api_excursions(request):
    """
    API endpoint для получения списка экскурсий
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    # Получаем параметры
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 12)
    search = request.GET.get('search', '')
    country = request.GET.get('country', '')
    city = request.GET.get('city', '')
    category = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    duration_min = request.GET.get('duration_min', '')
    duration_max = request.GET.get('duration_max', '')
    group_size = request.GET.get('group_size', '')
    rating = request.GET.get('rating', '')
    sort = request.GET.get('sort', 'popular')
    ordering = request.GET.get('ordering', '')
    limit = request.GET.get('limit', '')
    
    # Базовый queryset
    excursions = Excursion.objects.filter(status='published').select_related('city', 'country', 'category').prefetch_related('images')
    
    # Применяем фильтры
    if search:
        excursions = excursions.filter(
            Q(title_ru__icontains=search) |
            Q(description_ru__icontains=search) |
            Q(city__name_ru__icontains=search) |
            Q(country__name_ru__icontains=search)
        )
    
    if country:
        excursions = excursions.filter(country__slug=country)
    
    if city:
        excursions = excursions.filter(city__slug=city)
    
    if category:
        excursions = excursions.filter(category__slug=category)
    
    if price_min:
        try:
            excursions = excursions.filter(price__gte=float(price_min))
        except ValueError:
            pass
    
    if price_max:
        try:
            excursions = excursions.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    if duration_min:
        try:
            excursions = excursions.filter(duration__gte=int(duration_min))
        except ValueError:
            pass
    
    if duration_max:
        try:
            excursions = excursions.filter(duration__lte=int(duration_max))
        except ValueError:
            pass
    
    if group_size:
        try:
            excursions = excursions.filter(max_people__gte=int(group_size))
        except ValueError:
            pass
    
    if rating:
        try:
            excursions = excursions.filter(rating__gte=float(rating))
        except ValueError:
            pass
    
    # Сортировка
    if ordering == '-views_count':
        excursions = excursions.order_by('-views_count', '-rating')
    elif ordering == '-rating':
        excursions = excursions.order_by('-rating')
    elif ordering == 'price':
        excursions = excursions.order_by('price')
    elif ordering == '-price':
        excursions = excursions.order_by('-price')
    elif ordering == '-created_at':
        excursions = excursions.order_by('-created_at')
    elif sort == 'popular':
        excursions = excursions.order_by('-views_count', '-rating')
    elif sort == 'rating':
        excursions = excursions.order_by('-rating')
    elif sort == 'price_low':
        excursions = excursions.order_by('price')
    elif sort == 'price_high':
        excursions = excursions.order_by('-price')
    elif sort == 'newest':
        excursions = excursions.order_by('-created_at')
    else:
        excursions = excursions.order_by('-created_at')
    
    # Ограничение количества (для главной страницы)
    if limit:
        try:
            limit = int(limit)
            excursions = excursions[:limit]
            excursions_page = excursions
        except ValueError:
            excursions = excursions[:20]
            excursions_page = excursions
    else:
        # Пагинация для каталога
        try:
            page = int(page)
            per_page = int(per_page)
            paginator = Paginator(excursions, per_page)
            excursions_page = paginator.get_page(page)
        except (ValueError, TypeError):
            excursions_page = excursions[:20]
    
    # Сериализуем данные
    excursions_data = []
    for excursion in excursions_page:
        # Получаем главное изображение
        main_image = None
        if hasattr(excursion, 'main_image') and excursion.main_image:
            main_image = {
                'image': excursion.main_image.image.url if excursion.main_image.image else None
            }
        elif excursion.images.exists():
            # Если нет главного изображения, берем первое
            first_image = excursion.images.first()
            main_image = {
                'image': first_image.image.url if first_image.image else None
            }
        
        excursion_data = {
            'id': excursion.id,
            'title_ru': excursion.title_ru,
            'description_ru': excursion.description_ru,
            'price': excursion.price,
            'duration': excursion.duration,
            'max_people': excursion.max_people,
            'rating': excursion.rating or 0,
            'reviews_count': excursion.reviews_count or 0,
            'slug': excursion.slug,
            'city': {
                'name_ru': excursion.city.name_ru if excursion.city else '',
                'slug': excursion.city.slug if excursion.city else ''
            } if excursion.city else None,
            'country': {
                'name_ru': excursion.country.name_ru if excursion.country else '',
                'slug': excursion.country.slug if excursion.country else ''
            } if excursion.country else None,
            'category': {
                'name_ru': excursion.category.name_ru if excursion.category else '',
                'slug': excursion.category.slug if excursion.category else ''
            },
            'main_image': {
                'image': excursion.images.first().image.url if excursion.images.exists() else ''
            } if excursion.images.exists() else None
        }
        excursions_data.append(excursion_data)
    
    return JsonResponse({
        'results': excursions_data,
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'per_page': per_page,
    })


def api_countries(request):
    """
    API endpoint для получения списка стран
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    countries = Country.objects.all()
    countries_data = []
    
    for country in countries:
        countries_data.append({
            'id': country.id,
            'name_ru': country.name_ru,
            'slug': country.slug
        })
    
    return JsonResponse(countries_data, safe=False)


def api_categories(request):
    """
    API endpoint для получения списка категорий
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    categories = Category.objects.all()
    categories_data = []
    
    for category in categories:
        categories_data.append({
            'id': category.id,
            'name_ru': category.name_ru,
            'slug': category.slug
        })
    
    return JsonResponse(categories_data, safe=False)


def api_cities(request):
    """
    API endpoint для получения списка городов по стране
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    country_slug = request.GET.get('country', '')
    if country_slug:
        cities = City.objects.filter(country__slug=country_slug)
    else:
        cities = City.objects.all()
    
    cities_data = []
    for city in cities:
        cities_data.append({
            'id': city.id,
            'name_ru': city.name_ru,
            'slug': city.slug,
            'country': city.country.slug if city.country else ''
        })
    
    return JsonResponse(cities_data, safe=False)


@csrf_exempt
def api_favorites_toggle(request):
    """
    API endpoint для добавления/удаления из избранного
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    
    try:
        data = json.loads(request.body)
        excursion_id = data.get('excursion_id')
        
        if not excursion_id:
            return JsonResponse({'error': 'ID экскурсии обязателен'}, status=400)
        
        # Проверяем существование экскурсии
        try:
            excursion = Excursion.objects.get(id=excursion_id, status='published')
        except Excursion.DoesNotExist:
            return JsonResponse({'error': 'Экскурсия не найдена'}, status=404)
        
        # Проверяем, есть ли уже в избранном
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            excursion=excursion,
            defaults={'created_at': timezone.now()}
        )
        
        if not created:
            # Если уже есть - удаляем
            favorite.delete()
            is_favorite = False
            message = 'Убрано из избранного'
        else:
            # Если добавили - оставляем
            is_favorite = True
            message = 'Добавлено в избранное'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'is_favorite': is_favorite
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def test_vue(request):
    """
    Тестовая страница для проверки Vue.js интеграции
    """
    return render(request, 'test_vue.html')


def excursion_detail_simple(request, slug):
    """
    Упрощенная детальная страница экскурсии с Vue.js
    """
    excursion = get_object_or_404(Excursion, slug=slug, status='published')
    
    # Увеличиваем счетчик просмотров
    excursion.views_count += 1
    excursion.save()
    
    context = {
        'excursion': excursion,
    }
    
    return render(request, 'excursion_detail_simple.html', context)


def home_vue(request):
    """
    Главная страница с Vue.js
    """
    return render(request, 'home_vue.html')


def test_vue_simple(request):
    """
    Тестовая страница для проверки Vue.js
    """
    return render(request, 'test_vue_simple.html')


def api_stats(request):
    """API для получения статистики"""
    try:
        stats = {
            'excursions': Excursion.objects.count(),
            'countries': Country.objects.count(),
            'cities': City.objects.count(),
            'reviews': 0,  # Пока нет модели отзывов
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_reviews(request):
    """
    API endpoint для получения отзывов
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    try:
        reviews = Review.objects.filter(is_approved=True).select_related('user', 'excursion')[:10]
        reviews_data = []
        
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'created_at': review.created_at.strftime('%d.%m.%Y'),
                'user_name': review.user.first_name or review.user.username,
                'user_avatar': review.user.avatar.url if review.user.avatar else None,
                'excursion_title': review.excursion.title_ru if review.excursion else '',
                'excursion_slug': review.excursion.slug if review.excursion else ''
            })
        
        return JsonResponse(reviews_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_favorites(request):
    """
    API endpoint для получения избранного пользователя
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    
    try:
        favorites = Favorite.objects.filter(user=request.user, excursion__isnull=False).select_related('excursion')
        favorites_data = []
        
        for favorite in favorites:
            favorites_data.append({
                'id': favorite.id,
                'excursion': {
                    'id': favorite.excursion.id,
                    'title': favorite.excursion.title_ru,
                    'slug': favorite.excursion.slug
                }
            })
        
        return JsonResponse(favorites_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_contact(request):
    """
    API endpoint для отправки контактной формы
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        country = data.get('country', '').strip()
        
        if not name or not email:
            return JsonResponse({'error': 'Имя и email обязательны'}, status=400)
        
        # Создаем заявку
        application = Application.objects.create(
            name=name,
            email=email,
            phone=phone,
            country=country,
            message=f"Контактная форма: {name} ({email}) хочет получить информацию о турах"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Заявка успешно отправлена',
            'application_id': application.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_cities_for_home(request):
    """
    API endpoint для получения списка популярных городов для главной страницы
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешен'}, status=405)
    
    # Получаем города с изображениями для главной страницы
    cities = City.objects.filter(
        is_popular=True
    ).select_related('country').prefetch_related('images')[:6]
    
    cities_data = []
    for city in cities:
        city_data = {
            'id': city.id,
            'name_ru': city.name_ru,
            'slug': city.slug,
            'country': {
                'name_ru': city.country.name_ru if city.country else '',
                'slug': city.country.slug if city.country else ''
            } if city.country else None,
            'image': city.image.url if city.image else None,
            'excursions_count': Excursion.objects.filter(city=city, status='published').count()
        }
        cities_data.append(city_data)
    
    return JsonResponse(cities_data, safe=False)


def favorites_vue(request):
    """
    Страница избранного с Vue.js
    """
    return render(request, 'favorites_vue.html')


def send_booking_notifications(booking):
    """Отправка уведомлений о бронировании"""
    try:
        # Проверяем, что пользователь установлен
        if not hasattr(booking, 'user') or not booking.user:
            print(f"DEBUG: ОШИБКА: Пользователь не установлен в бронировании {booking.id}")
            return
        
        # Email для клиента
        client_subject = _('Подтверждение бронирования - SELEXIA Travel')
        client_message = render_to_string('emails/booking_confirmation.html', {
            'booking': booking,
            'excursion': booking.excursion,
            'user': booking.user
        })
        
        # Email для администратора
        admin_subject = _('Новое бронирование - SELEXIA Travel')
        admin_message = render_to_string('emails/booking_admin_notification.html', {
            'booking': booking,
            'excursion': booking.excursion,
            'user': booking.user
        })
        
        # Отправляем email клиенту
        send_mail(
            subject=client_subject,
            message='',
            html_message=client_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.contact_email],
            fail_silently=False,
        )
        
        # Отправляем email администратору
        admin_email = getattr(settings, 'BOOKING_NOTIFICATION_EMAIL', 'selexiatravelauth@gmail.com')
        send_mail(
            subject=admin_subject,
            message='',
            html_message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
        
        print(f"DEBUG: Email уведомления отправлены для бронирования {booking.id}")
        
    except Exception as e:
        print(f"DEBUG: Ошибка отправки email уведомлений: {e}")
        raise


def social_signup_view(request):
    """
    Кастомный view для социальной регистрации
    """
    from allauth.socialaccount.models import SocialAccount
    from .models import User  # Используем кастомную модель User
    from django.contrib.auth import login
    from django.contrib.auth.backends import ModelBackend
    
    # Если пользователь уже авторизован, перенаправляем на dashboard
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы!')
        return redirect('dashboard')
    
    # Получаем email из GET параметров или POST
    email = request.GET.get('email') or request.POST.get('email') or ''
    
    # Если email передан через GET и пользователь существует, автоматически входим
    if email and request.method == 'GET':
        try:
            user = User.objects.get(email=email)
            # Автоматически авторизуем пользователя
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Вход выполнен успешно! Добро пожаловать, {user.first_name or user.username or user.email}!')
            return redirect('dashboard')
        except User.DoesNotExist:
            # Пользователь не существует, показываем форму регистрации
            pass
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Проверяем, существует ли пользователь с таким email
            try:
                user = User.objects.get(email=email)
                # Если пользователь существует, авторизуем его
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Вход выполнен успешно! Добро пожаловать, {user.first_name or user.username or user.email}!')
                return redirect('dashboard')
            except User.DoesNotExist:
                # Если пользователь не существует, создаем нового
                try:
                    # Создаем пользователя с временным именем
                    username = email.split('@')[0] + '_' + str(int(time.time()))
                    
                    # Проверяем, что username уникален
                    while User.objects.filter(username=username).exists():
                        username = email.split('@')[0] + '_' + str(int(time.time()))
                    
                    print(f"DEBUG: Создаем пользователя с email={email}, username={username}")
                    
                    user = User.objects.create_user(
                        email=email,  # email должен быть первым параметром
                        username=username,
                        first_name='Пользователь',
                        last_name=''
                    )
                    
                    print(f"DEBUG: Пользователь создан успешно: {user.id}")
                    
                    # Авторизуем нового пользователя
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, 'Регистрация завершена успешно! Добро пожаловать!')
                    return redirect('dashboard')
                except Exception as e:
                    print(f"DEBUG: Ошибка при создании пользователя: {str(e)}")
                    print(f"DEBUG: Тип ошибки: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    messages.error(request, f'Ошибка при создании пользователя: {str(e)}')
            except Exception as e:
                print(f"DEBUG: Общая ошибка: {str(e)}")
                messages.error(request, f'Произошла ошибка: {str(e)}')
    
    # Получаем информацию о социальном аккаунте
    social_account = None
    if request.user.is_authenticated:
        social_account = SocialAccount.objects.filter(user=request.user).first()
    
    context = {
        'email': email,
        'social_account': social_account,
    }
    
    return render(request, 'account/social_signup.html', context)


@login_required
def connect_gmail_view(request):
    """Подключение Gmail аккаунта"""
    if request.method == 'POST':
        try:
            from .gmail_integration import GmailOAuthHelper
            
            helper = GmailOAuthHelper()
            auth_url, flow = helper.get_authorization_url()
            
            if auth_url:
                # Сохраняем flow в сессии для последующего использования
                request.session['gmail_flow'] = flow
                return redirect(auth_url)
            else:
                messages.error(request, 'Ошибка при создании URL авторизации Gmail')
                
        except Exception as e:
            messages.error(request, f'Ошибка при подключении Gmail: {str(e)}')
    
    return render(request, 'users/connect_gmail.html')


@login_required
def gmail_callback_view(request):
    """Callback для OAuth авторизации Gmail"""
    try:
        from .gmail_integration import GmailOAuthHelper
        
        # Получаем код авторизации
        authorization_response = request.build_absolute_uri()
        
        # Получаем flow из сессии
        flow = request.session.get('gmail_flow')
        if not flow:
            messages.error(request, 'Ошибка: flow не найден в сессии')
            return redirect('dashboard')
        
        helper = GmailOAuthHelper()
        tokens = helper.exchange_code_for_tokens(flow, authorization_response)
        
        if tokens:
            # Сохраняем токены в профиле пользователя
            user = request.user
            user.gmail_access_token = tokens['access_token']
            user.gmail_refresh_token = tokens['refresh_token']
            user.gmail_token_expiry = tokens['token_expiry']
            user.save(update_fields=['gmail_access_token', 'gmail_refresh_token', 'gmail_token_expiry'])
            
            # Обновляем профиль из Gmail
            from .gmail_integration import sync_user_with_gmail
            if sync_user_with_gmail(user):
                messages.success(request, 'Gmail аккаунт успешно подключен! Профиль обновлен.')
            else:
                messages.warning(request, 'Gmail аккаунт подключен, но не удалось обновить профиль.')
            
            # Очищаем сессию
            if 'gmail_flow' in request.session:
                del request.session['gmail_flow']
                
        else:
            messages.error(request, 'Ошибка при получении токенов Gmail')
            
    except Exception as e:
        messages.error(request, f'Ошибка при обработке callback Gmail: {str(e)}')
    
    return redirect('dashboard')


@login_required
def sync_gmail_profile_view(request):
    """Синхронизация профиля с Gmail"""
    try:
        user = request.user
        
        if not user.gmail_access_token:
            messages.error(request, 'Gmail аккаунт не подключен')
            return redirect('dashboard')
        
        from .gmail_integration import sync_user_with_gmail
        
        if sync_user_with_gmail(user):
            messages.success(request, 'Профиль успешно синхронизирован с Gmail!')
        else:
            messages.warning(request, 'Не удалось синхронизировать профиль с Gmail')
            
    except Exception as e:
        messages.error(request, f'Ошибка при синхронизации: {str(e)}')
    
    return redirect('dashboard')


@login_required
def disconnect_gmail_view(request):
    """Отключение Gmail аккаунта"""
    try:
        user = request.user
        
        # Очищаем Gmail данные
        user.gmail_access_token = None
        user.gmail_refresh_token = None
        user.gmail_token_expiry = None
        user.gmail_profile_updated = None
        user.save(update_fields=[
            'gmail_access_token', 'gmail_refresh_token', 
            'gmail_token_expiry', 'gmail_profile_updated'
        ])
        
        messages.success(request, 'Gmail аккаунт успешно отключен')
        
    except Exception as e:
        messages.error(request, f'Ошибка при отключении Gmail: {str(e)}')
    
    return redirect('dashboard')