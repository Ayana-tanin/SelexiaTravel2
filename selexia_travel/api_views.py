from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django.contrib.auth import get_user_model
from .models import (
    Excursion, Category, Country, City, 
    Booking, Review, Favorite, Application
)
from .serializers import (
    ExcursionSerializer, ExcursionDetailSerializer, CategorySerializer,
    CountrySerializer, CitySerializer, ReviewSerializer, ReviewCreateSerializer,
    BookingSerializer, BookingCreateSerializer, FavoriteSerializer,
    ApplicationSerializer, ContactSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer
)

User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
    """Стандартная пагинация для API"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# Экскурсии API
class ExcursionListAPIView(generics.ListAPIView):
    """API для списка экскурсий с фильтрацией и поиском"""
    serializer_class = ExcursionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Excursion.objects.filter(status='published').select_related(
            'category', 'country', 'city'
        ).prefetch_related('favorites')
        
        # Поиск по тексту
        query = self.request.query_params.get('search', None)
        if query:
            queryset = queryset.filter(
                Q(title_ru__icontains=query) |
                Q(title_en__icontains=query) |
                Q(description_ru__icontains=query) |
                Q(description_en__icontains=query) |
                Q(short_description_ru__icontains=query) |
                Q(short_description_en__icontains=query)
            )
        
        # Фильтрация по категории
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Фильтрация по стране
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(country_id=country)
        
        # Фильтрация по городу
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city_id=city)
        
        # Фильтрация по цене
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Фильтрация по длительности
        duration = self.request.query_params.get('duration', None)
        if duration:
            queryset = queryset.filter(duration__lte=duration)
        
        # Фильтрация по количеству людей
        people_count = self.request.query_params.get('people_count', None)
        if people_count:
            queryset = queryset.filter(
                min_people__lte=people_count,
                max_people__gte=people_count
            )
        
        # Фильтрация по рейтингу
        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(average_rating__gte=rating)
        
        # Сортировка
        sort_by = self.request.query_params.get('sort', 'created_at')
        if sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'duration':
            queryset = queryset.order_by('duration')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

class ExcursionDetailAPIView(generics.RetrieveAPIView):
    """API для детальной информации об экскурсии"""
    queryset = Excursion.objects.filter(status='published').select_related(
        'category', 'country', 'city'
    ).prefetch_related('favorites', 'reviews')
    serializer_class = ExcursionDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

# Категории, страны, города API
class CategoryListAPIView(generics.ListAPIView):
    """API для списка категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CountryListAPIView(generics.ListAPIView):
    """API для списка стран"""
    queryset = Country.objects.all().order_by('name_ru')
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]

class CityListAPIView(generics.ListAPIView):
    """API для списка городов"""
    queryset = City.objects.all().select_related('country').order_by('name_ru')
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

class CitiesByCountryAPIView(generics.ListAPIView):
    """API для списка городов по стране"""
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        country_id = self.kwargs['country_id']
        return City.objects.filter(country_id=country_id).select_related('country').order_by('name_ru')

# Отзывы API
class ReviewListAPIView(generics.ListCreateAPIView):
    """API для списка отзывов"""
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Review.objects.all().select_related('user', 'excursion').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API для детальной информации об отзыве"""
    queryset = Review.objects.all().select_related('user', 'excursion')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

# Бронирования API
class BookingListAPIView(generics.ListCreateAPIView):
    """API для списка бронирований"""
    serializer_class = BookingSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('excursion').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BookingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API для детальной информации о бронировании"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('excursion')

# Избранное API
class FavoriteListAPIView(generics.ListCreateAPIView):
    """API для списка избранного"""
    serializer_class = FavoriteSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('excursion').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteDetailAPIView(generics.RetrieveDestroyAPIView):
    """API для детальной информации об избранном"""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('excursion')

# Заявки API
class ApplicationCreateAPIView(generics.CreateAPIView):
    """API для создания заявки"""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.AllowAny]

# Контактная форма API
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contact_api(request):
    """API для отправки контактной формы"""
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        # Здесь можно добавить логику отправки email
        # send_contact_email(serializer.validated_data)
        return Response({'message': 'Сообщение отправлено успешно'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Поиск API
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_excursions_api(request):
    """API для поиска экскурсий"""
    query = request.query_params.get('q', '')
    if not query:
        return Response({'error': 'Параметр поиска обязателен'}, status=status.HTTP_400_BAD_REQUEST)
    
    excursions = Excursion.objects.filter(
        Q(title_ru__icontains=query) |
        Q(title_en__icontains=query) |
        Q(description_ru__icontains=query) |
        Q(description_en__icontains=query) |
        Q(short_description_ru__icontains=query) |
        Q(short_description_en__icontains=query),
        status='published'
    ).select_related('category', 'country', 'city')[:10]
    
    serializer = ExcursionSerializer(excursions, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_autocomplete_api(request):
    """API для автодополнения поиска"""
    query = request.query_params.get('q', '')
    if not query:
        return Response([])
    
    # Поиск по названиям экскурсий
    excursions = Excursion.objects.filter(
        title_ru__icontains=query,
        status='published'
    ).values_list('title_ru', flat=True)[:5]
    
    # Поиск по названиям городов
    cities = City.objects.filter(name_ru__icontains=query).values_list('name_ru', flat=True)[:3]
    
    # Поиск по названиям стран
    countries = Country.objects.filter(name_ru__icontains=query).values_list('name_ru', flat=True)[:2]
    
    results = list(excursions) + list(cities) + list(countries)
    return Response(results[:10])

# Пользовательский профиль API
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API для профиля пользователя"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateAPIView(generics.UpdateAPIView):
    """API для обновления профиля пользователя"""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

# Дополнительные API endpoints
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def excursions_api(request):
    """API для получения всех экскурсий (для совместимости)"""
    excursions = Excursion.objects.filter(status='published').select_related(
        'category', 'country', 'city'
    ).prefetch_related('favorites')
    
    # Применяем фильтры
    category = request.query_params.get('category')
    if category:
        excursions = excursions.filter(category_id=category)
    
    country = request.query_params.get('country')
    if country:
        excursions = excursions.filter(country_id=country)
    
    # Сортировка
    sort = request.query_params.get('sort', 'created_at')
    if sort == 'price':
        excursions = excursions.order_by('price')
    elif sort == 'rating':
        excursions = excursions.order_by('-average_rating')
    else:
        excursions = excursions.order_by('-created_at')
    
    serializer = ExcursionSerializer(excursions, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def excursion_detail_api(request, slug):
    """API для получения деталей экскурсии (для совместимости)"""
    excursion = get_object_or_404(
        Excursion.objects.select_related('category', 'country', 'city')
        .prefetch_related('reviews', 'favorites'),
        slug=slug,
        status='published'
    )
    serializer = ExcursionDetailSerializer(excursion, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite_api(request):
    """API для добавления/удаления из избранного"""
    excursion_id = request.data.get('excursion_id')
    if not excursion_id:
        return Response({'error': 'ID экскурсии обязателен'}, status=status.HTTP_400_BAD_REQUEST)
    
    excursion = get_object_or_404(Excursion, id=excursion_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        excursion=excursion
    )
    
    if not created:
        favorite.delete()
        return Response({'message': 'Удалено из избранного'}, status=status.HTTP_200_OK)
    
    return Response({'message': 'Добавлено в избранное'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_favorites_api(request):
    """API для получения избранного пользователя"""
    favorites = Favorite.objects.filter(user=request.user).select_related('excursion')
    serializer = FavoriteSerializer(favorites, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_bookings_api(request):
    """API для получения бронирований пользователя"""
    bookings = Booking.objects.filter(user=request.user).select_related('excursion')
    serializer = BookingSerializer(bookings, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_reviews_api(request):
    """API для получения отзывов пользователя"""
    reviews = Review.objects.filter(user=request.user).select_related('excursion')
    serializer = ReviewSerializer(reviews, many=True, context={'request': request})
    return Response(serializer.data)

# Дополнительные функции для совместимости
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def categories_api(request):
    """API для получения всех категорий"""
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def countries_api(request):
    """API для получения всех стран"""
    countries = Country.objects.all()
    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def cities_api(request):
    """API для получения всех городов"""
    cities = City.objects.all()
    serializer = CitySerializer(cities, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def cities_by_country(request, country_id):
    """API для получения городов по стране"""
    cities = City.objects.filter(country_id=country_id)
    serializer = CitySerializer(cities, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_application(request):
    """API для отправки заявки"""
    serializer = ApplicationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_booking(request):
    """API для отправки бронирования"""
    serializer = BookingCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_review(request):
    """API для отправки отзыва"""
    serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def review_detail_api(request, review_id):
    """API для получения деталей отзыва"""
    review = get_object_or_404(Review, id=review_id)
    serializer = ReviewSerializer(review, context={'request': request})
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_review(request, review_id):
    """API для обновления отзыва"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    serializer = ReviewSerializer(review, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_review(request, review_id):
    """API для удаления отзыва"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request):
    """API для добавления/удаления из избранного"""
    excursion_id = request.data.get('excursion_id')
    if not excursion_id:
        return Response({'error': 'ID экскурсии обязателен'}, status=status.HTTP_400_BAD_REQUEST)
    
    excursion = get_object_or_404(Excursion, id=excursion_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        excursion=excursion
    )
    
    if not created:
        favorite.delete()
        return Response({'message': 'Удалено из избранного'}, status=status.HTTP_200_OK)
    
    return Response({'message': 'Добавлено в избранное'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile_api(request):
    """API для получения профиля пользователя"""
    serializer = UserProfileSerializer(request.user, context={'request': request})
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_api(request):
    """API для обновления профиля пользователя"""
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_autocomplete(request):
    """API для автодополнения поиска"""
    query = request.query_params.get('q', '')
    if len(query) < 2:
        return Response([])
    
    excursions = Excursion.objects.filter(
        Q(title_ru__icontains=query) | Q(short_description_ru__icontains=query),
        status='published'
    )[:10]
    
    results = []
    for excursion in excursions:
        results.append({
            'id': excursion.id,
            'title': excursion.title_ru,
            'slug': excursion.slug,
            'type': 'excursion'
        })
    
    return Response(results)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_excursions_api(request):
    """API для поиска экскурсий"""
    query = request.query_params.get('q', '')
    if not query:
        return Response({'error': 'Поисковый запрос обязателен'}, status=status.HTTP_400_BAD_REQUEST)
    
    excursions = Excursion.objects.filter(
        Q(title_ru__icontains=query) | 
        Q(description_ru__icontains=query) | 
        Q(short_description_ru__icontains=query),
        status='published'
    ).select_related('category', 'country', 'city')
    
    serializer = ExcursionSerializer(excursions, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contact_api(request):
    """API для отправки контактной формы"""
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        # Здесь можно добавить логику отправки email
        serializer.save()
        return Response({'message': 'Сообщение отправлено'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
