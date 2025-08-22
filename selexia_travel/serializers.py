from rest_framework import serializers
from .models import (
    User, Excursion, Category, Country, City, 
    Booking, Review, Favorite, Application
)

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'avatar', 'date_of_birth']
        read_only_fields = ['id', 'username', 'email']

class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""
    class Meta:
        model = Category
        fields = ['id', 'name_ru', 'name_en', 'slug', 'description_ru', 'description_en', 'icon', 'color', 'image', 'is_featured']

class CountrySerializer(serializers.ModelSerializer):
    """Сериализатор для стран"""
    class Meta:
        model = Country
        fields = ['id', 'name_ru', 'name_en', 'iso_code', 'slug', 'image', 'is_popular']

class CitySerializer(serializers.ModelSerializer):
    """Сериализатор для городов"""
    country = CountrySerializer(read_only=True)
    excursions_count = serializers.ReadOnlyField()
    
    class Meta:
        model = City
        fields = ['id', 'name_ru', 'name_en', 'country', 'slug', 'latitude', 'longitude', 'image', 'excursions_count', 'created_at']

class ExcursionSerializer(serializers.ModelSerializer):
    """Сериализатор для экскурсий"""
    category = CategorySerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Excursion
        fields = [
            'id', 'title_ru', 'title_en', 'slug', 'description_ru', 'description_en', 
            'short_description_ru', 'short_description_en', 'price', 'currency', 'duration', 
            'duration_unit', 'max_people', 'category', 'country', 'city', 
            'views_count', 'rating', 'reviews_count', 'is_popular', 'is_featured', 
            'average_rating', 'total_reviews', 'is_favorite',
            'status', 'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        return obj.rating
    
    def get_total_reviews(self, obj):
        return obj.reviews_count
    
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

class ExcursionDetailSerializer(ExcursionSerializer):
    """Детальный сериализатор для экскурсии"""
    class Meta(ExcursionSerializer.Meta):
        fields = ExcursionSerializer.Meta.fields + [
            'program_ru', 'program_en', 'included_ru', 'included_en',
            'important_info_ru', 'important_info_en', 'meeting_point_ru', 'meeting_point_en'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
    user = UserSerializer(read_only=True)
    excursion = ExcursionSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'excursion', 'rating', 'text', 'created_at']
        read_only_fields = ['user', 'created_at']

class ReviewCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания отзыва"""
    class Meta:
        model = Review
        fields = ['excursion', 'rating', 'text']

class BookingSerializer(serializers.ModelSerializer):
    """Сериализатор для бронирований"""
    user = UserSerializer(read_only=True)
    excursion = ExcursionSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'excursion', 'date', 'people_count',
            'total_price', 'status', 'special_requests', 'created_at'
        ]
        read_only_fields = ['user', 'total_price', 'created_at']

class BookingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания бронирования"""
    class Meta:
        model = Booking
        fields = ['excursion', 'date', 'people_count', 'special_requests']

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    user = UserSerializer(read_only=True)
    excursion = ExcursionSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'excursion', 'created_at']
        read_only_fields = ['user', 'created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    """Сериализатор для заявок"""
    class Meta:
        model = Application
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['created_at']

class ContactSerializer(serializers.Serializer):
    """Сериализатор для контактной формы"""
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    message = serializers.CharField()
    subject = serializers.CharField(max_length=200, required=False)

class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'avatar', 'date_of_birth']
        read_only_fields = ['id', 'email']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'date_of_birth']
