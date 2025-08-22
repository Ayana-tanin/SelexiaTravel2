from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
import os
from django.utils import timezone


class UserManager(BaseUserManager):
    """Кастомный менеджер пользователей для email-аутентификации в Django 4.2+"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Создает обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен для создания пользователя')
        
        # Генерируем username если не предоставлен
        if not extra_fields.get('username'):
            extra_fields['username'] = self.generate_username(email)
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def generate_username(self, email):
        """Генерирует уникальный username на основе email"""
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Создает суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Расширенная модель пользователя для Django 4.2+"""
    # Username делаем необязательным для совместимости с Django Allauth
    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True,
        verbose_name=_('Имя пользователя')
    )
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Аватар'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('Дата рождения'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата регистрации'))
    
    # Gmail интеграция
    gmail_access_token = models.TextField(blank=True, null=True, verbose_name=_('Gmail Access Token'))
    gmail_refresh_token = models.TextField(blank=True, null=True, verbose_name=_('Gmail Refresh Token'))
    gmail_token_expiry = models.DateTimeField(blank=True, null=True, verbose_name=_('Gmail Token Expiry'))
    gmail_profile_updated = models.DateTimeField(blank=True, null=True, verbose_name=_('Последнее обновление профиля Gmail'))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Django Allauth требует username в REQUIRED_FIELDS
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def favorites_count(self):
        return self.favorites.count()
    
    def can_review_excursion(self, excursion):
        """Проверяет, может ли пользователь оставить отзыв на экскурсию"""
        # Проверяем, есть ли у пользователя бронирования со статусом confirmed или completed
        eligible_bookings = self.bookings.filter(
            excursion=excursion,
            status__in=['confirmed', 'completed']
        )
        
        # Проверяем, не оставлял ли пользователь уже отзыв на эту экскурсию
        existing_review = self.reviews.filter(excursion=excursion).exists()
        
        return eligible_bookings.exists() and not existing_review
    
    def has_reviewed_excursion(self, excursion):
        """Проверяет, оставлял ли пользователь отзыв на экскурсию"""
        return self.reviews.filter(excursion=excursion).exists()
    
    def update_from_gmail(self):
        """Обновляет профиль пользователя из Gmail"""
        if not self.gmail_access_token:
            return False
        
        try:
            from .gmail_integration import GmailProfileUpdater
            updater = GmailProfileUpdater()
            success = updater.update_user_profile(self)
            if success:
                self.gmail_profile_updated = timezone.now()
                self.save(update_fields=['gmail_profile_updated'])
            return success
        except Exception as e:
            print(f"Ошибка при обновлении профиля из Gmail: {e}")
            return False
    
    def needs_gmail_refresh(self):
        """Проверяет, нужно ли обновить Gmail токен"""
        if not self.gmail_token_expiry:
            return True
        return timezone.now() >= self.gmail_token_expiry
    
    def refresh_gmail_token(self):
        """Обновляет Gmail токен"""
        if not self.gmail_refresh_token:
            return False
        
        try:
            from .gmail_integration import GmailProfileUpdater
            updater = GmailProfileUpdater()
            success = updater.refresh_user_token(self)
            return success
        except Exception as e:
            print(f"Ошибка при обновлении Gmail токена: {e}")
            return False


class Country(models.Model):
    """Модель страны"""
    name_ru = models.CharField(max_length=100, verbose_name=_('Название (рус)'))
    name_en = models.CharField(max_length=100, verbose_name=_('Название (англ)'))
    iso_code = models.CharField(max_length=3, unique=True, verbose_name=_('ISO код'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Слаг'))
    image = models.ImageField(upload_to='countries/', blank=True, null=True, verbose_name=_('Изображение'))
    is_popular = models.BooleanField(default=False, verbose_name=_('Популярная'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Страна')
        verbose_name_plural = _('Страны')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_popular']),
        ]
        ordering = ['name_ru']
    
    def __str__(self):
        return self.name_ru
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_ru)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog') + f'?country={self.slug}'
    
    @property
    def cities_count(self):
        return self.cities.count()


class City(models.Model):
    """Модель города"""
    name_ru = models.CharField(max_length=100, verbose_name=_('Название (рус)'))
    name_en = models.CharField(max_length=100, verbose_name=_('Название (англ)'))
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities', verbose_name=_('Страна'))
    slug = models.SlugField(max_length=100, verbose_name=_('Слаг'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name=_('Широта'))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name=_('Долгота'))
    image = models.ImageField(upload_to='cities/', blank=True, null=True, verbose_name=_('Изображение'))
    is_popular = models.BooleanField(default=False, verbose_name=_('Популярный'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Город')
        verbose_name_plural = _('Города')
        ordering = ['name_ru']
        unique_together = ['country', 'slug']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['country']),
            models.Index(fields=['is_popular']),
        ]
    
    def __str__(self):
        return f"{self.name_ru}, {self.country.name_ru}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_ru)
        super().save(*args, **kwargs)
    
    @property
    def excursions_count(self):
        return self.excursions.filter(status='published').count()


class Category(models.Model):
    """Модель категории экскурсий"""
    name_ru = models.CharField(max_length=100, verbose_name=_('Название (рус)'))
    name_en = models.CharField(max_length=100, verbose_name=_('Название (англ)'))
    description_ru = models.TextField(blank=True, verbose_name=_('Описание (рус)'))
    description_en = models.TextField(blank=True, verbose_name=_('Описание (англ)'))
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name=_('Изображение'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Рекомендуемая'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Слаг'))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Иконка'))
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_('Цвет'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['name_ru']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.name_ru
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_ru)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog') + f'?category={self.slug}'
    
    @property
    def excursions_count(self):
        return self.excursions.filter(status='published').count()


class Excursion(models.Model):
    """Модель экскурсии"""
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('published', _('Опубликовано')),
        ('archived', _('Архив')),
    ]
    
    DURATION_UNIT_CHOICES = [
        ('hours', _('Часы')),
        ('days', _('Дни')),
    ]
    
    title_ru = models.CharField(max_length=200, verbose_name=_('Название (рус)'))
    title_en = models.CharField(max_length=200, verbose_name=_('Название (англ)'))
    description_ru = models.TextField(verbose_name=_('Описание (рус)'))
    description_en = models.TextField(blank=True, verbose_name=_('Описание (англ)'))
    short_description_ru = models.CharField(max_length=300, verbose_name=_('Краткое описание (рус)'))
    short_description_en = models.CharField(max_length=300, blank=True, verbose_name=_('Краткое описание (англ)'))
    
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='excursions', verbose_name=_('Страна'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='excursions', verbose_name=_('Город'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='excursions', verbose_name=_('Категория'))
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Валюта'))
    
    duration = models.PositiveIntegerField(verbose_name=_('Длительность'))
    duration_unit = models.CharField(max_length=5, choices=DURATION_UNIT_CHOICES, default='hours', verbose_name=_('Единица времени'))
    max_people = models.PositiveIntegerField(default=10, verbose_name=_('Максимум человек'))
    
    program_ru = models.TextField(blank=True, verbose_name=_('Программа (рус)'))
    program_en = models.TextField(blank=True, verbose_name=_('Программа (англ)'))
    included_ru = models.TextField(blank=True, verbose_name=_('Включено (рус)'))
    included_en = models.TextField(blank=True, verbose_name=_('Включено (англ)'))
    important_info_ru = models.TextField(blank=True, verbose_name=_('Важная информация (рус)'))
    important_info_en = models.TextField(blank=True, verbose_name=_('Важная информация (англ)'))
    
    meeting_point_ru = models.CharField(max_length=300, blank=True, verbose_name=_('Место встречи (рус)'))
    meeting_point_en = models.CharField(max_length=300, blank=True, verbose_name=_('Место встречи (англ)'))
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name=_('Статус'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Слаг'))
    
    # Статистика
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Просмотры'))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name=_('Рейтинг'))
    reviews_count = models.PositiveIntegerField(default=0, verbose_name=_('Количество отзывов'))
    is_popular = models.BooleanField(default=False, verbose_name=_('Популярная'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Рекомендуемая'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    
    class Meta:
        verbose_name = _('Экскурсия')
        verbose_name_plural = _('Экскурсии')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['price']),
            models.Index(fields=['city']),
            models.Index(fields=['status']),
            models.Index(fields=['is_popular']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['rating']),
            models.Index(fields=['views_count']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title_ru
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en or self.title_ru)
        
        # Автоматическое определение популярности
        if self.views_count >= 100:
            self.is_popular = True
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('excursion_detail', kwargs={'slug': self.slug})
    
    @property
    def main_image(self):
        return self.images.first()
    
    @property
    def has_valid_gallery(self):
        images_count = self.images.count()
        return 6 <= images_count <= 15
    
    @property
    def duration_display(self):
        unit = 'ч.' if self.duration_unit == 'hours' else 'дн.'
        return f"{self.duration} {unit}"
    
    def update_rating(self):
        """Обновляет рейтинг экскурсии на основе отзывов"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
            self.rating = round(avg_rating, 2)
            self.reviews_count = reviews.count()
        else:
            self.rating = 0
            self.reviews_count = 0
        self.save(update_fields=['rating', 'reviews_count'])


class ExcursionImage(models.Model):
    """Модель изображений экскурсии"""
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='images', verbose_name=_('Экскурсия'))
    image = models.ImageField(upload_to='excursions/%Y/%m/', verbose_name=_('Изображение'))
    caption_ru = models.CharField(max_length=200, blank=True, verbose_name=_('Подпись (рус)'))
    caption_en = models.CharField(max_length=200, blank=True, verbose_name=_('Подпись (англ)'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Изображение экскурсии')
        verbose_name_plural = _('Изображения экскурсий')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.excursion.title_ru} - {self.order}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Автоматическая обработка изображения
        if self.image:
            img = Image.open(self.image.path)
            
            # Изменяем размер до 1200x800
            if img.height > 800 or img.width > 1200:
                output_size = (1200, 800)
                img.thumbnail(output_size, Image.Resampling.LANCZOS)
                img.save(self.image.path, optimize=True, quality=85)


class Review(models.Model):
    """Модель отзывов"""
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Экскурсия'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Пользователь'))
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Рейтинг'))
    text = models.TextField(verbose_name=_('Текст отзыва'))
    is_approved = models.BooleanField(default=True, verbose_name=_('Одобрен'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']
        unique_together = ['user', 'excursion']  # Один пользователь - один отзыв на экскурсию
        indexes = [
            models.Index(fields=['excursion']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.excursion.title_ru}"


class ReviewImage(models.Model):
    """Модель изображений отзывов"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', verbose_name=_('Отзыв'))
    image = models.ImageField(upload_to='reviews/%Y/%m/', verbose_name=_('Изображение'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Изображение отзыва')
        verbose_name_plural = _('Изображения отзывов')


class Booking(models.Model):
    """Модель бронирований"""
    STATUS_CHOICES = [
        ('pending', _('Ожидание')),
        ('confirmed', _('Подтверждено')),
        ('cancelled', _('Отменено')),
        ('completed', _('Завершено')),
    ]
    
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='bookings', verbose_name=_('Экскурсия'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name=_('Пользователь'))
    date = models.DateField(verbose_name=_('Дата'))
    people_count = models.PositiveIntegerField(verbose_name=_('Количество человек'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Стоимость экскурсии'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name=_('Статус'))
    special_requests = models.TextField(blank=True, verbose_name=_('Особые пожелания'))
    contact_phone = models.CharField(max_length=20, verbose_name=_('Контактный телефон'))
    contact_email = models.EmailField(verbose_name=_('Контактный email'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Бронирование')
        verbose_name_plural = _('Бронирования')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['excursion']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
            models.Index(fields=['created_at']),
        ]
    
    def clean(self):
        """Валидация данных бронирования"""
        from django.core.exceptions import ValidationError
        
        # Проверяем пользователя только если он установлен
        if hasattr(self, 'user') and self.user:
            # Дополнительные проверки для пользователя можно добавить здесь
            pass
        
        if not self.excursion:
            raise ValidationError(_('Экскурсия обязательна для бронирования'))
        
        if self.date and self.date < timezone.now().date():
            raise ValidationError(_('Дата не может быть в прошлом'))
        
        if self.people_count and self.people_count <= 0:
            raise ValidationError(_('Количество человек должно быть больше 0'))
        
        if self.people_count and self.excursion and self.people_count > self.excursion.max_people:
            raise ValidationError(_(f'Максимальное количество человек: {self.excursion.max_people}'))
    
    def save(self, *args, **kwargs):
        """Сохраняет бронирование с валидацией"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        user_name = self.user.full_name if hasattr(self, 'user') and self.user else "Неизвестный пользователь"
        return f"{self.excursion.title_ru} - {user_name}"


class Favorite(models.Model):
    """Модель избранного"""
    ITEM_TYPE_CHOICES = [
        ('excursion', _('Экскурсия')),
        ('category', _('Категория')),
        ('country', _('Страна')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('Пользователь'))
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='excursion', verbose_name=_('Тип элемента'))
    
    # Поля для разных типов элементов (только одно может быть заполнено)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('Экскурсия'), null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('Категория'), null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('Страна'), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Добавлено'))
    
    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранные')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['item_type']),
            models.Index(fields=['excursion']),
            models.Index(fields=['category']),
            models.Index(fields=['country']),
            models.Index(fields=['created_at']),
        ]
    
    def clean(self):
        """Проверяем, что заполнено только одно поле"""
        filled_fields = sum([
            bool(self.excursion),
            bool(self.category),
            bool(self.country)
        ])
        if filled_fields != 1:
            raise ValidationError(_('Должно быть заполнено ровно одно поле: экскурсия, категория или страна'))
        
        # Проверяем уникальность
        if self.excursion:
            if Favorite.objects.filter(user=self.user, excursion=self.excursion).exclude(pk=self.pk).exists():
                raise ValidationError(_('Эта экскурсия уже добавлена в избранное'))
        elif self.category:
            if Favorite.objects.filter(user=self.user, category=self.category).exclude(pk=self.pk).exists():
                raise ValidationError(_('Эта категория уже добавлена в избранное'))
        elif self.country:
            if Favorite.objects.filter(user=self.user, country=self.country).exclude(pk=self.pk).exists():
                raise ValidationError(_('Эта страна уже добавлена в избранное'))
    
    def __str__(self):
        if self.excursion:
            return f"{self.user.full_name} - {self.excursion.title_ru}"
        elif self.category:
            return f"{self.user.full_name} - {self.category.name_ru}"
        elif self.country:
            return f"{self.user.full_name} - {self.country.name_ru}"
        return f"{self.user.full_name} - Неизвестный элемент"
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Application(models.Model):
    """Модель заявок с главной страницы"""
    STATUS_CHOICES = [
        ('new', _('Новая')),
        ('in_progress', _('В работе')),
        ('completed', _('Завершена')),
        ('cancelled', _('Отменена')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('Имя'))
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(verbose_name=_('Email'))
    message = models.TextField(verbose_name=_('Сообщение'))
    destination = models.CharField(max_length=200, blank=True, verbose_name=_('Направление'))
    travel_dates = models.CharField(max_length=100, blank=True, verbose_name=_('Даты поездки'))
    people_count = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Количество человек'))
    budget = models.CharField(max_length=100, blank=True, verbose_name=_('Бюджет'))
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='new', verbose_name=_('Статус'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.destination}"


class UserSettings(models.Model):
    """Модель настроек пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings', verbose_name=_('Пользователь'))
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True, verbose_name=_('Email уведомления'))
    push_notifications = models.BooleanField(default=True, verbose_name=_('Push уведомления'))
    
    # Настройки приватности
    profile_public = models.BooleanField(default=False, verbose_name=_('Публичный профиль'))
    show_reviews = models.BooleanField(default=True, verbose_name=_('Показывать отзывы'))
    
    # Настройки языка и региона
    preferred_language = models.CharField(max_length=5, choices=[
        ('ru', 'Русский'),
        ('en', 'English'),
    ], default='ru', verbose_name=_('Предпочитаемый язык'))
    
    timezone = models.CharField(max_length=50, default='Europe/Moscow', verbose_name=_('Часовой пояс'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Настройки пользователя')
        verbose_name_plural = _('Настройки пользователей')
    
    def __str__(self):
        return f"Настройки {self.user.full_name}"
    
    def save(self, *args, **kwargs):
        # Создаем настройки по умолчанию при первом сохранении
        if not self.pk:
            self.email_notifications = True
            self.push_notifications = True
            self.profile_public = False
            self.show_reviews = True
            self.preferred_language = 'ru'
            self.timezone = 'Europe/Moscow'
        super().save(*args, **kwargs)