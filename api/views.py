from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from selexia_travel.models import Excursion, Booking, Review, Favorite, Country, City, Category, Application
from .serializers import (
    ExcursionListSerializer, ExcursionDetailSerializer, ReviewSerializer,
    FavoriteSerializer, FavoriteCreateSerializer, BookingSerializer, BookingCreateSerializer,
    SearchFilterSerializer, CountrySerializer, CitySerializer, CategorySerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Стандартная пагинация для API"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ExcursionViewSet(viewsets.ReadOnlyModelViewSet):
    """API для экскурсий"""
    queryset = Excursion.objects.filter(status='published').select_related(
        'country', 'city', 'category'
    ).prefetch_related('images').order_by('-is_popular', '-rating', '-views_count')
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country__slug', 'city__slug', 'category__slug', 'is_popular', 'is_featured']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en', 'city__name_ru', 'country__name_ru']
    ordering_fields = ['price', 'rating', 'created_at', 'views_count']
    ordering = ['-is_popular', '-rating', '-views_count']
    
    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия"""
        if self.action == 'retrieve':
            return ExcursionDetailSerializer
        return ExcursionListSerializer
    
    def get_queryset(self):
        """Расширенный queryset с фильтрацией"""
        queryset = super().get_queryset()
        
        # Фильтры из query параметров
        search = self.request.query_params.get('search', None)
        country = self.request.query_params.get('country', None)
        city = self.request.query_params.get('city', None)
        category = self.request.query_params.get('category', None)
        price_min = self.request.query_params.get('price_min', None)
        price_max = self.request.query_params.get('price_max', None)
        rating = self.request.query_params.get('rating', None)
        sort = self.request.query_params.get('sort', 'popular')
        
        # Поиск по тексту
        if search:
            queryset = queryset.filter(
                Q(title_ru__icontains=search) |
                Q(title_en__icontains=search) |
                Q(description_ru__icontains=search) |
                Q(description_en__icontains=search) |
                Q(city__name_ru__icontains=search) |
                Q(country__name_ru__icontains=search)
            )
        
        # Фильтр по стране
        if country:
            queryset = queryset.filter(country__slug=country)
        
        # Фильтр по городу
        if city:
            queryset = queryset.filter(city__slug=city)
        
        # Фильтр по категории
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Фильтр по цене
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Фильтр по рейтингу
        if rating:
            queryset = queryset.filter(rating__gte=rating)
        
        # Сортировка
        if sort == 'popular':
            queryset = queryset.order_by('-is_popular', '-views_count', '-rating')
        elif sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating', '-reviews_count')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Получение детальной информации об экскурсии с увеличением счетчика просмотров"""
        instance = self.get_object()
        
        # Увеличиваем счетчик просмотров
        instance.views_count += 1
        
        # Автоматически определяем популярность
        if instance.views_count >= 100:
            instance.is_popular = True
        
        instance.save(update_fields=['views_count', 'is_popular'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Популярные экскурсии"""
        popular_excursions = self.get_queryset().filter(is_popular=True)[:6]
        serializer = self.get_serializer(popular_excursions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Рекомендуемые экскурсии"""
        featured_excursions = self.get_queryset().filter(is_featured=True)[:8]
        serializer = self.get_serializer(featured_excursions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика экскурсий"""
        stats = {
            'total_excursions': Excursion.objects.filter(status='published').count(),
            'popular_excursions': Excursion.objects.filter(status='published', is_popular=True).count(),
            'featured_excursions': Excursion.objects.filter(status='published', is_featured=True).count(),
            'total_countries': Country.objects.count(),
            'total_cities': City.objects.count(),
            'total_categories': Category.objects.count(),
        }
        return Response(stats)


class FavoriteViewSet(viewsets.ModelViewSet):
    """API для избранного"""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Получает избранное только для текущего пользователя"""
        return Favorite.objects.filter(user=self.request.user).select_related(
            'excursion', 'category', 'country'
        )
    
    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия"""
        if self.action == 'create':
            return FavoriteCreateSerializer
        return FavoriteSerializer
    
    def create(self, request, *args, **kwargs):
        """Создание или удаление избранного (toggle)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        item_id = serializer.validated_data['item_id']
        item_type = serializer.validated_data['item_type']
        
        # Проверяем, есть ли уже в избранном
        if item_type == 'excursion':
            existing_favorite = Favorite.objects.filter(
                user=request.user,
                excursion_id=item_id
            ).first()
        elif item_type == 'category':
            existing_favorite = Favorite.objects.filter(
                user=request.user,
                category_id=item_id
            ).first()
        elif item_type == 'country':
            existing_favorite = Favorite.objects.filter(
                user=request.user,
                country_id=item_id
            ).first()
        else:
            return Response({
                'success': False,
                'error': 'Неизвестный тип элемента'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if existing_favorite:
            # Удаляем из избранного
            existing_favorite.delete()
            return Response({
                'success': True,
                'is_favorite': False,
                'message': 'Убрано из избранного'
            })
        else:
            # Добавляем в избранное
            if item_type == 'excursion':
                excursion = get_object_or_404(Excursion, id=item_id)
                favorite = Favorite.objects.create(
                    user=request.user,
                    item_type=item_type,
                    excursion=excursion
                )
            elif item_type == 'category':
                category = get_object_or_404(Category, id=item_id)
                favorite = Favorite.objects.create(
                    user=request.user,
                    item_type=item_type,
                    category=category
                )
            elif item_type == 'country':
                country = get_object_or_404(Country, id=item_id)
                favorite = Favorite.objects.create(
                    user=request.user,
                    item_type=item_type,
                    country=country
                )
            
            return Response({
                'success': True,
                'is_favorite': True,
                'message': 'Добавлено в избранное'
            })
    
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Количество элементов в избранном"""
        count = self.get_queryset().count()
        return Response({'count': count})


class BookingViewSet(viewsets.ModelViewSet):
    """API для бронирований"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Получает бронирования только для текущего пользователя"""
        return Booking.objects.filter(user=self.request.user).select_related('excursion')
    
    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия"""
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer
    
    def create(self, request, *args, **kwargs):
        """Создание бронирования"""
        # Дополнительная проверка аутентификации
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Пользователь должен быть аутентифицирован'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        # Проверяем валидацию с детальным логированием ошибок
        if not serializer.is_valid():
            print(f"DEBUG: Ошибки валидации: {serializer.errors}")
            return Response({
                'success': False,
                'error': 'Ошибка валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем доступность даты
        excursion = serializer.validated_data['excursion']
        date = serializer.validated_data['date']
        people_count = serializer.validated_data['people_count']
        
        # Проверяем, не превышает ли количество человек максимальное
        if people_count > excursion.max_people:
            return Response({
                'success': False,
                'error': f'Максимальное количество человек: {excursion.max_people}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Логируем данные для отладки
            print(f"DEBUG: Создание бронирования для пользователя {request.user.id}")
            print(f"DEBUG: Данные запроса: {request.data}")
            print(f"DEBUG: Валидированные данные: {serializer.validated_data}")
            
            # Создаем бронирование
            booking = serializer.save()
            
            print(f"DEBUG: Бронирование создано успешно: {booking.id}")
            
            return Response({
                'success': True,
                'message': 'Бронирование создано успешно',
                'booking_id': booking.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"DEBUG: Ошибка при создании бронирования: {str(e)}")
            print(f"DEBUG: Тип ошибки: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            return Response({
                'success': False,
                'error': f'Ошибка при создании бронирования: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """API для отзывов (только чтение)"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Получает одобренные отзывы"""
        return Review.objects.filter(is_approved=True).select_related('user', 'excursion')
    
    @action(detail=False, methods=['get'])
    def by_excursion(self, request):
        """Получение отзывов по экскурсии"""
        excursion_id = request.query_params.get('excursion_id')
        if not excursion_id:
            return Response({'error': 'Необходимо указать excursion_id'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        reviews = self.get_queryset().filter(excursion_id=excursion_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для стран (только чтение)"""
    queryset = Country.objects.all().order_by('name_ru')
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_ru', 'name_en']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Получение популярных стран"""
        popular_countries = Country.objects.filter(is_popular=True)[:10]
        serializer = self.get_serializer(popular_countries, many=True)
        return Response(serializer.data)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """API для городов (только чтение)"""
    queryset = City.objects.select_related('country').order_by('name_ru')
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country__slug']
    search_fields = ['name_ru', 'name_en']
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Получение городов по стране"""
        country_slug = request.query_params.get('country')
        if not country_slug:
            return Response({'error': 'Необходимо указать country'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        cities = self.get_queryset().filter(country__slug=country_slug)
        serializer = self.get_serializer(cities, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для категорий (только чтение)"""
    queryset = Category.objects.all().order_by('name_ru')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_ru', 'name_en']
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Получение рекомендуемых категорий"""
        featured_categories = Category.objects.filter(is_featured=True)[:10]
        serializer = self.get_serializer(featured_categories, many=True)
        return Response(serializer.data)

# Дополнительные API views для соответствия новым URL-паттернам
@api_view(['GET'])
@permission_classes([AllowAny])
def api_excursions(request):
    """API для получения списка экскурсий (для AJAX)"""
    excursions = Excursion.objects.filter(status='published').select_related(
        'country', 'city', 'category'
    ).prefetch_related('images')[:20]
    
    data = []
    for excursion in excursions:
        data.append({
            'id': excursion.id,
            'title': excursion.title_ru if request.LANGUAGE_CODE == 'ru' else excursion.title_en,
            'slug': excursion.slug,
            'price': excursion.price,
            'rating': excursion.rating,
            'reviews_count': excursion.reviews_count,
            'image': excursion.images.first().image.url if excursion.images.exists() else None,
            'country': excursion.country.name_ru if request.LANGUAGE_CODE == 'ru' else excursion.country.name_en,
            'city': excursion.city.name_ru if request.LANGUAGE_CODE == 'ru' else excursion.city.name_en,
            'category': excursion.category.name_ru if request.LANGUAGE_CODE == 'ru' else excursion.category.name_en,
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_countries(request):
    """API для получения списка стран (для AJAX)"""
    countries = Country.objects.all()
    data = []
    for country in countries:
        data.append({
            'id': country.id,
            'name': country.name_ru if request.LANGUAGE_CODE == 'ru' else country.name_en,
            'slug': country.slug,
            'image': country.image.url if country.image else None,
            'cities_count': country.cities.count(),
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_categories(request):
    """API для получения списка категорий (для AJAX)"""
    categories = Category.objects.all()
    data = []
    for category in categories:
        data.append({
            'id': category.id,
            'name': category.name_ru if request.LANGUAGE_CODE == 'ru' else category.name_en,
            'slug': category.slug,
            'image': category.image.url if category.image else None,
            'excursions_count': category.excursions.filter(status='published').count(),
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_cities(request):
    """API для получения списка городов (для AJAX)"""
    cities = City.objects.all()
    data = []
    for city in cities:
        data.append({
            'id': city.id,
            'name': city.name_ru if request.LANGUAGE_CODE == 'ru' else city.name_en,
            'slug': city.slug,
            'country': city.country.name_ru if request.LANGUAGE_CODE == 'ru' else city.country.name_en,
            'excursions_count': city.excursions.filter(status='published').count(),
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_cities_for_home(request):
    """API для получения городов для главной страницы"""
    cities = City.objects.filter(is_popular=True)[:8]
    data = []
    for city in cities:
        data.append({
            'id': city.id,
            'name': city.name_ru if request.LANGUAGE_CODE == 'ru' else city.name_en,
            'slug': city.slug,
            'country': city.country.name_ru if request.LANGUAGE_CODE == 'ru' else city.country.name_en,
            'image': city.image.url if city.image else None,
        })
    
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_favorites_toggle(request):
    """API для переключения избранного"""
    item_id = request.data.get('item_id')
    item_type = request.data.get('item_type', 'excursion')
    
    if not item_id:
        return Response({'error': 'item_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if item_type == 'excursion':
            item = get_object_or_404(Excursion, id=item_id, status='published')
            # Проверяем, есть ли уже в избранном
            existing_favorite = Favorite.objects.filter(user=request.user, excursion=item).first()
            if existing_favorite:
                existing_favorite.delete()
                is_favorite = False
            else:
                Favorite.objects.create(user=request.user, excursion=item, item_type='excursion')
                is_favorite = True
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
            return Response({'error': 'Неизвестный тип элемента'}, status=status.HTTP_400_BAD_REQUEST)
        
        favorites_count = request.user.favorites.count()
        
        return Response({
            'success': True,
            'is_favorite': is_favorite,
            'favorites_count': favorites_count
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_favorites(request):
    """API для получения всех избранных элементов"""
    favorites = Favorite.objects.filter(user=request.user).select_related('excursion', 'category', 'country')
    data = []
    for favorite in favorites:
        if favorite.excursion:
            data.append({
                'id': favorite.excursion.id,
                'type': 'excursion',
                'title': favorite.excursion.title_ru if request.LANGUAGE_CODE == 'ru' else favorite.excursion.title_en,
                'slug': favorite.excursion.slug,
                'price': favorite.excursion.price,
                'rating': favorite.excursion.rating,
                'image': favorite.excursion.images.first().image.url if favorite.excursion.images.exists() else None,
            })
        elif favorite.category:
            data.append({
                'id': favorite.category.id,
                'type': 'category',
                'title': favorite.category.name_ru if request.LANGUAGE_CODE == 'ru' else favorite.category.name_en,
                'slug': favorite.category.slug,
                'image': None,
            })
        elif favorite.country:
            data.append({
                'id': favorite.country.id,
                'type': 'country',
                'title': favorite.country.name_ru if request.LANGUAGE_CODE == 'ru' else favorite.country.name_en,
                'slug': favorite.country.slug,
                'image': favorite.country.image.url if favorite.country.image else None,
            })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_reviews(request):
    """API для получения отзывов"""
    excursion_id = request.GET.get('excursion_id')
    if excursion_id:
        reviews = Review.objects.filter(excursion_id=excursion_id, is_approved=True)
    else:
        reviews = Review.objects.filter(is_approved=True)[:10]
    
    data = []
    for review in reviews:
        data.append({
            'id': review.id,
            'user_name': review.user.get_full_name() or review.user.username,
            'rating': review.rating,
            'comment': review.text,
            'created_at': review.created_at,
            'excursion_title': review.excursion.title_ru if request.LANGUAGE_CODE == 'ru' else review.excursion.title_en,
        })
    
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_contact(request):
    """API для отправки контактной формы"""
    # Здесь должна быть логика обработки контактной формы
    return Response({'status': 'success', 'message': 'Message sent successfully'})

@api_view(['GET'])
@permission_classes([AllowAny])
def api_stats(request):
    """API для получения статистики"""
    stats = {
        'excursions_count': Excursion.objects.filter(status='published').count(),
        'countries_count': Country.objects.count(),
        'cities_count': City.objects.count(),
        'reviews_count': Review.objects.filter(is_approved=True).count(),
        'total_bookings': Booking.objects.count(),
    }
    return Response(stats)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_application(request):
    """API для отправки заявки"""
    # Здесь должна быть логика обработки заявки
    return Response({'status': 'success', 'message': 'Application submitted successfully'})

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_booking(request):
    """API для отправки бронирования"""
    # Здесь должна быть логика обработки бронирования
    return Response({'status': 'success', 'message': 'Booking submitted successfully'})

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_review(request):
    """API для отправки отзыва"""
    # Здесь должна быть логика обработки отзыва
    return Response({'status': 'success', 'message': 'Review submitted successfully'})

@api_view(['GET'])
@permission_classes([AllowAny])
def search_autocomplete(request):
    """API для автодополнения поиска"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return Response([])
    
    excursions = Excursion.objects.filter(
        Q(title_ru__icontains=query) | Q(title_en__icontains=query),
        status='published'
    )[:5]
    
    data = []
    for excursion in excursions:
        data.append({
            'id': excursion.id,
            'title': excursion.title_ru if request.LANGUAGE_CODE == 'ru' else excursion.title_en,
            'slug': excursion.slug,
            'type': 'excursion'
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def cities_by_country(request):
    """API для получения городов по стране"""
    country_slug = request.GET.get('country')
    if not country_slug:
        return Response({'error': 'country parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        country = Country.objects.get(slug=country_slug)
        cities = country.cities.all()
        data = []
        for city in cities:
            data.append({
                'id': city.id,
                'name': city.name_ru if request.LANGUAGE_CODE == 'ru' else city.name_en,
                'slug': city.slug,
            })
        return Response(data)
    except Country.DoesNotExist:
        return Response({'error': 'Country not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    """API для сохранения настроек уведомлений пользователя"""
    try:
        setting = request.data.get('setting')
        enabled = request.data.get('enabled')
        
        if not setting:
            return Response({'success': False, 'error': 'Setting parameter required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем или создаем настройки пользователя
        from selexia_travel.models import UserSettings
        user_settings, created = UserSettings.objects.get_or_create(user=request.user)
        
        # Обновляем соответствующую настройку
        if setting == 'Email уведомления':
            user_settings.email_notifications = enabled
        elif setting == 'Push уведомления':
            user_settings.push_notifications = enabled
        else:
            return Response({'success': False, 'error': 'Unknown setting'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user_settings.save()
        
        return Response({
            'success': True, 
            'message': f'Notification setting "{setting}" {"enabled" if enabled else "disabled"}',
            'setting': setting,
            'enabled': enabled
        })
        
    except Exception as e:
        return Response({
            'success': False, 
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, pk):
    """API для отмены бронирования"""
    try:
        # Получаем бронирование
        booking = Booking.objects.get(id=pk, user=request.user)
        
        # Проверяем, что бронирование можно отменить (только в статусе 'pending')
        if booking.status != 'pending':
            return Response({
                'success': False, 
                'error': 'Можно отменить только бронирования в статусе "Ожидание"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Отменяем бронирование
        booking.status = 'cancelled'
        booking.save()
        
        return Response({
            'success': True,
            'message': 'Бронирование успешно отменено'
        })
        
    except Booking.DoesNotExist:
        return Response({
            'success': False, 
            'error': 'Бронирование не найдено'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False, 
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
