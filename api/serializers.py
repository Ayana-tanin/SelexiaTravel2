from rest_framework import serializers
from selexia_travel.models import Excursion, ExcursionImage, Booking, Review, Favorite, User, Country, City, Category
from django.utils import timezone


class CountrySerializer(serializers.ModelSerializer):
    """Сериализатор для стран"""
    class Meta:
        model = Country
        fields = ['id', 'name_ru', 'name_en', 'iso_code', 'slug']


class CitySerializer(serializers.ModelSerializer):
    """Сериализатор для городов"""
    country = CountrySerializer(read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name_ru', 'name_en', 'slug', 'country']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""
    class Meta:
        model = Category
        fields = ['id', 'name_ru', 'name_en', 'slug', 'icon', 'color']


class ExcursionImageSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений экскурсий"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ExcursionImage
        fields = ['id', 'image_url', 'caption_ru', 'caption_en', 'order']
    
    def get_image_url(self, obj):
        """Получает URL изображения"""
        if obj.image:
            return obj.image.url
        return None


class ExcursionListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка экскурсий (краткая информация)"""
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Excursion
        fields = [
            'id', 'title_ru', 'title_en', 'short_description_ru', 'short_description_en',
            'price', 'currency', 'duration', 'duration_unit', 'max_people',
            'country', 'city', 'category', 'rating', 'reviews_count',
            'views_count', 'is_popular', 'is_featured', 'slug',
            'main_image', 'created_at'
        ]
    
    def get_main_image(self, obj):
        """Получает главное изображение экскурсии"""
        main_image = obj.images.first()
        if main_image:
            return {
                'url': main_image.image.url,
                'caption': main_image.caption_ru
            }
        return None


class ExcursionDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации об экскурсии"""
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ExcursionImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Excursion
        fields = [
            'id', 'title_ru', 'title_en', 'description_ru', 'description_en',
            'short_description_ru', 'short_description_en', 'price', 'currency',
            'duration', 'duration_unit', 'max_people', 'country', 'city', 'category',
            'program_ru', 'program_en', 'included_ru', 'included_en',
            'important_info_ru', 'important_info_en', 'meeting_point_ru', 'meeting_point_en',
            'rating', 'reviews_count', 'views_count', 'is_popular', 'is_featured',
            'slug', 'images', 'main_image', 'created_at', 'updated_at'
        ]
    
    def get_main_image(self, obj):
        """Получает главное изображение экскурсии"""
        main_image = obj.images.first()
        if main_image:
            return {
                'url': main_image.image.url,
                'caption': main_image.caption_ru
            }
        return None


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'text', 'created_at']
    
    def get_user(self, obj):
        """Получает имя пользователя"""
        return obj.user.full_name if obj.user else 'Аноним'


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    excursion = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    
    class Meta:
        model = Favorite
        fields = ['id', 'excursion', 'category', 'country', 'item_type', 'created_at']
    
    def get_excursion(self, obj):
        """Получает данные экскурсии если это экскурсия"""
        if obj.excursion:
            return ExcursionListSerializer(obj.excursion).data
        return None
    
    def get_category(self, obj):
        """Получает данные категории если это категория"""
        if obj.category:
            return CategorySerializer(obj.category).data
        return None
    
    def get_country(self, obj):
        """Получает данные страны если это страна"""
        if obj.country:
            return CountrySerializer(obj.country).data
        return None


class FavoriteCreateSerializer(serializers.Serializer):
    """Сериализатор для создания избранного"""
    item_id = serializers.IntegerField(help_text="ID элемента")
    item_type = serializers.ChoiceField(
        choices=[('excursion', 'Экскурсия'), ('category', 'Категория'), ('country', 'Страна')],
        help_text="Тип элемента"
    )
    
    def validate(self, data):
        """Проверяет, что заполнено только одно поле"""
        item_id = data.get('item_id')
        item_type = data.get('item_type')
        
        if not item_id or not item_type:
            raise serializers.ValidationError("Необходимо указать item_id и item_type")
        
        # Проверяем существование объекта
        if item_type == 'excursion':
            try:
                Excursion.objects.get(id=item_id)
            except Excursion.DoesNotExist:
                raise serializers.ValidationError("Экскурсия не найдена")
        elif item_type == 'category':
            try:
                Category.objects.get(id=item_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError("Категория не найдена")
        elif item_type == 'country':
            try:
                Country.objects.get(id=item_id)
            except Country.DoesNotExist:
                raise serializers.ValidationError("Страна не найдена")
        
        return data


class BookingSerializer(serializers.ModelSerializer):
    """Сериализатор для бронирований"""
    excursion = ExcursionListSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'excursion', 'user', 'date', 'people_count', 'total_price',
            'status', 'special_requests', 'contact_phone', 'contact_email', 'created_at'
        ]
    
    def get_user(self, obj):
        """Получает имя пользователя"""
        return obj.user.full_name if obj.user else 'Аноним'


class BookingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания бронирования"""
    class Meta:
        model = Booking
        fields = [
            'excursion', 'date', 'people_count', 'special_requests',
            'contact_phone', 'contact_email'
        ]
    
    def validate(self, data):
        """Валидация данных бронирования"""
        excursion = data.get('excursion')
        date = data.get('date')
        people_count = data.get('people_count')
        
        # Проверяем обязательные поля
        if not excursion:
            raise serializers.ValidationError("Экскурсия обязательна для бронирования")
        
        if not date:
            raise serializers.ValidationError("Дата обязательна для бронирования")
        
        if not people_count:
            raise serializers.ValidationError("Количество человек обязательно для бронирования")
        
        if date < timezone.now().date():
            raise serializers.ValidationError("Дата не может быть в прошлом")
        
        if people_count > excursion.max_people:
            raise serializers.ValidationError(
                f"Максимальное количество человек: {excursion.max_people}"
            )
        
        if people_count <= 0:
            raise serializers.ValidationError("Количество человек должно быть больше 0")
        
        return data
    
    def create(self, validated_data):
        """Создает бронирование с автоматическим расчетом цены"""
        excursion = validated_data['excursion']
        people_count = validated_data['people_count']
        
        # Проверяем, что пользователь аутентифицирован
        print(f"DEBUG: Контекст: {self.context}")
        print(f"DEBUG: Запрос в контексте: {self.context.get('request')}")
        print(f"DEBUG: Тип контекста: {type(self.context)}")
        print(f"DEBUG: Все ключи контекста: {list(self.context.keys())}")
        
        if not self.context.get('request'):
            print("DEBUG: Контекст запроса отсутствует")
            raise serializers.ValidationError("Контекст запроса отсутствует")
        
        print(f"DEBUG: Пользователь в запросе: {self.context['request'].user}")
        print(f"DEBUG: Тип пользователя в запросе: {type(self.context['request'].user)}")
        print(f"DEBUG: Атрибуты пользователя: {dir(self.context['request'].user)}")
        print(f"DEBUG: Проверка user is None: {self.context['request'].user is None}")
        print(f"DEBUG: Проверка user == '': {self.context['request'].user == ''}")
        print(f"DEBUG: Проверка user == False: {self.context['request'].user == False}")
        print(f"DEBUG: Проверка user == 0: {self.context['request'].user == 0}")
        print(f"DEBUG: Проверка user == '0': {self.context['request'].user == '0'}")
        
        if not self.context['request'].user:
            print("DEBUG: Пользователь в запросе отсутствует")
            raise serializers.ValidationError("Пользователь в запросе отсутствует")
        
        print(f"DEBUG: Аутентифицирован ли пользователь: {self.context['request'].user.is_authenticated}")
        
        if not self.context['request'].user.is_authenticated:
            print("DEBUG: Пользователь не аутентифицирован")
            raise serializers.ValidationError("Пользователь должен быть аутентифицирован")
        
        print(f"DEBUG: Пользователь аутентифицирован: {self.context['request'].user.id}")
        
        # Автоматический расчет общей стоимости
        validated_data['total_price'] = excursion.price * people_count
        validated_data['user'] = self.context['request'].user
        
        print(f"DEBUG: Установлен пользователь: {validated_data['user'].id}")
        print(f"DEBUG: Тип пользователя: {type(validated_data['user'])}")
        print(f"DEBUG: Пользователь в validated_data: {validated_data.get('user')}")
        print(f"DEBUG: validated_data после установки пользователя: {validated_data}")
        print(f"DEBUG: Проверка user is None: {validated_data.get('user') is None}")
        print(f"DEBUG: Проверка user == '': {validated_data.get('user') == ''}")
        print(f"DEBUG: Проверка user == False: {validated_data.get('user') == False}")
        
        # Дополнительная проверка, что пользователь установлен
        if not validated_data['user']:
            print("DEBUG: Пользователь не установлен")
            raise serializers.ValidationError("Не удалось определить пользователя")
        
        # Дополнительная проверка, что пользователь не None
        if validated_data['user'] is None:
            print("DEBUG: Пользователь None")
            raise serializers.ValidationError("Пользователь не может быть None")
        
        # Дополнительная проверка, что пользователь не пустая строка
        if validated_data['user'] == '':
            print("DEBUG: Пользователь пустая строка")
            raise serializers.ValidationError("Пользователь не может быть пустой строкой")
        
        # Дополнительная проверка, что пользователь не False
        if validated_data['user'] == False:
            print("DEBUG: Пользователь False")
            raise serializers.ValidationError("Пользователь не может быть False")
        
        # Дополнительная проверка, что пользователь не 0
        if validated_data['user'] == 0:
            print("DEBUG: Пользователь 0")
            raise serializers.ValidationError("Пользователь не может быть 0")
        
        # Дополнительная проверка, что пользователь не '0'
        if validated_data['user'] == '0':
            print("DEBUG: Пользователь '0'")
            raise serializers.ValidationError("Пользователь не может быть '0'")
        
        print(f"DEBUG: Пользователь успешно установлен: {validated_data['user'].id}")
        
        # Логируем данные для отладки
        print(f"DEBUG: Создание бронирования для пользователя {validated_data['user'].id}")
        print(f"DEBUG: Данные: {validated_data}")
        print(f"DEBUG: Тип пользователя: {type(validated_data['user'])}")
        print(f"DEBUG: ID пользователя: {validated_data['user'].id}")
        print(f"DEBUG: Username пользователя: {validated_data['user'].username}")
        print(f"DEBUG: Email пользователя: {validated_data['user'].email}")
        print(f"DEBUG: Все ключи в validated_data: {list(validated_data.keys())}")
        print(f"DEBUG: Значение user в validated_data: {validated_data.get('user')}")
        print(f"DEBUG: Проверка user is None: {validated_data.get('user') is None}")
        print(f"DEBUG: Проверка user == '': {validated_data.get('user') == ''}")
        print(f"DEBUG: Проверка user == False: {validated_data.get('user') == False}")
        print(f"DEBUG: Проверка user == 0: {validated_data.get('user') == 0}")
        print(f"DEBUG: Проверка user == '0': {validated_data.get('user') == '0'}")
        
        try:
            print("DEBUG: Вызываем super().create()")
            print(f"DEBUG: validated_data перед созданием: {validated_data}")
            print(f"DEBUG: Тип validated_data: {type(validated_data)}")
            print(f"DEBUG: Ключи validated_data: {list(validated_data.keys())}")
            
            # Проверяем каждый ключ отдельно
            for key, value in validated_data.items():
                print(f"DEBUG: {key}: {value} (тип: {type(value)})")
                if key == 'user':
                    print(f"DEBUG: Пользователь детально: {value}")
                    if hasattr(value, 'id'):
                        print(f"DEBUG: ID пользователя: {value.id}")
                    if hasattr(value, 'username'):
                        print(f"DEBUG: Username пользователя: {value.username}")
                    if hasattr(value, 'email'):
                        print(f"DEBUG: Email пользователя: {value.email}")
            
            result = super().create(validated_data)
            print(f"DEBUG: super().create() успешно выполнен: {result}")
            return result
        except Exception as e:
            print(f"DEBUG: Ошибка в super().create(): {str(e)}")
            print(f"DEBUG: Тип ошибки: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            # Проверяем конкретную ошибку
            if "user" in str(e).lower():
                raise serializers.ValidationError("Ошибка при сохранении: пользователь не может быть пустым")
            else:
                raise serializers.ValidationError(f"Ошибка при сохранении: {str(e)}")


class SearchFilterSerializer(serializers.Serializer):
    """Сериализатор для фильтров поиска"""
    search = serializers.CharField(required=False, help_text="Поисковый запрос")
    country = serializers.CharField(required=False, help_text="Слаг страны")
    city = serializers.CharField(required=False, help_text="Слаг города")
    category = serializers.CharField(required=False, help_text="Слаг категории")
    price_min = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    price_max = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)
    sort = serializers.ChoiceField(
        required=False,
        choices=[
            ('popular', 'По популярности'),
            ('price_asc', 'Сначала дешевые'),
            ('price_desc', 'Сначала дорогие'),
            ('rating', 'По рейтингу'),
            ('newest', 'Новые'),
            ('views', 'По просмотрам')
        ],
        default='popular'
    )
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
