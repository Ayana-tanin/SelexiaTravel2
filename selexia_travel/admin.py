from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from django.utils.translation import gettext_lazy as _

from .models import (
    User, Country, City, Category, Excursion, ExcursionImage,
    Review, ReviewImage, Booking, Favorite, Application, UserSettings
)


class ExcursionImageInline(admin.TabularInline):
    """Инлайн для изображений экскурсий"""
    model = ExcursionImage
    extra = 1
    fields = ('image', 'caption_ru', 'caption_en', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = _('Превью')


class ReviewImageInline(admin.TabularInline):
    """Инлайн для изображений отзывов"""
    model = ReviewImage
    extra = 0
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit: cover;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = _('Превью')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка пользователей"""
    model = User
    list_display = ('email', 'first_name', 'last_name', 'phone', 'gmail_connected', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'gmail_profile_updated')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Персональная информация'), {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'date_of_birth')}),
        (_('Gmail интеграция'), {
            'fields': ('gmail_access_token', 'gmail_refresh_token', 'gmail_token_expiry', 'gmail_profile_updated'),
            'classes': ('collapse',),
            'description': _('Настройки интеграции с Gmail API')
        }),
        (_('Разрешения'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('gmail_profile_updated',)
    
    def gmail_connected(self, obj):
        """Показывает статус подключения Gmail"""
        if obj.gmail_access_token:
            return format_html(
                '<span style="color: green;">✓ Подключен</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Не подключен</span>'
        )
    gmail_connected.short_description = _('Gmail статус')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            bookings_count=Count('bookings'),
            reviews_count=Count('reviews')
        )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Админка стран"""
    list_display = ('name_ru', 'name_en', 'iso_code', 'cities_count', 'excursions_count', 'is_popular')
    list_filter = ('is_popular',)
    search_fields = ('name_ru', 'name_en', 'iso_code')
    prepopulated_fields = {'slug': ('name_en',)}
    readonly_fields = ('cities_count', 'excursions_count')
    
    def cities_count(self, obj):
        return obj.cities.count()
    cities_count.short_description = _('Количество городов')
    
    def excursions_count(self, obj):
        return obj.excursions.filter(status='published').count()
    excursions_count.short_description = _('Количество экскурсий')


def make_cities_popular(modeladmin, request, queryset):
    """Сделать города популярными"""
    queryset.update(is_popular=True)
make_cities_popular.short_description = _('Сделать города популярными')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Админка городов"""
    list_display = ('name_ru', 'name_en', 'country', 'excursions_count', 'is_popular')
    list_filter = ('country', 'is_popular')
    search_fields = ('name_ru', 'name_en', 'country__name_ru')
    prepopulated_fields = {'slug': ('name_en',)}
    autocomplete_fields = ('country',)
    readonly_fields = ('excursions_count',)
    actions = [make_cities_popular]
    
    def excursions_count(self, obj):
        return obj.excursions.filter(status='published').count()
    excursions_count.short_description = _('Количество экскурсий')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка категорий"""
    list_display = ('name_ru', 'name_en', 'excursions_count', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('name_ru', 'name_en')
    prepopulated_fields = {'slug': ('name_en',)}
    readonly_fields = ('excursions_count',)
    
    def excursions_count(self, obj):
        return obj.excursions.filter(status='published').count()
    excursions_count.short_description = _('Количество экскурсий')


def make_published(modeladmin, request, queryset):
    """Массовая публикация экскурсий"""
    queryset.update(status='published')
make_published.short_description = _('Опубликовать выбранные экскурсии')


def make_draft(modeladmin, request, queryset):
    """Массовый перевод в черновики"""
    queryset.update(status='draft')
make_draft.short_description = _('Перевести в черновики')


def make_popular(modeladmin, request, queryset):
    """Сделать популярными"""
    queryset.update(is_popular=True)
make_popular.short_description = _('Сделать популярными')


@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    """Админка экскурсий"""
    list_display = (
        'title_ru', 'city', 'country', 'category', 'price', 
        'status', 'rating', 'views_count', 'gallery_status', 
        'is_popular', 'is_featured'
    )
    list_filter = (
        'status', 'category', 'country', 'is_popular', 
        'is_featured', 'created_at'
    )
    search_fields = ('title_ru', 'title_en', 'description_ru', 'description_en')
    prepopulated_fields = {'slug': ('title_en',)}
    autocomplete_fields = ('country', 'city', 'category')
    readonly_fields = ('views_count', 'rating', 'reviews_count', 'gallery_status')
    actions = [make_published, make_draft, make_popular]
    inlines = [ExcursionImageInline]
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title_ru', 'title_en', 'slug', 'short_description_ru', 'short_description_en')
        }),
        (_('Местоположение'), {
            'fields': ('country', 'city', 'category')
        }),
        (_('Описание'), {
            'fields': ('description_ru', 'description_en')
        }),
        (_('Детали'), {
            'fields': (
                'price', 'currency', 'duration', 'duration_unit', 'max_people',
                'meeting_point_ru', 'meeting_point_en'
            )
        }),
        (_('Программа и условия'), {
            'fields': ('program_ru', 'program_en', 'included_ru', 'included_en', 'important_info_ru', 'important_info_en'),
            'classes': ('collapse',)
        }),
        (_('Статус и настройки'), {
            'fields': ('status', 'is_popular', 'is_featured')
        }),
        (_('Статистика'), {
            'fields': ('views_count', 'rating', 'reviews_count', 'gallery_status'),
            'classes': ('collapse',)
        }),
    )
    
    def gallery_status(self, obj):
        images_count = obj.images.count()
        if images_count < 6:
            color = 'red'
            status = f'Недостаточно ({images_count}/6)'
        elif images_count > 15:
            color = 'orange'
            status = f'Слишком много ({images_count}/15)'
        else:
            color = 'green'
            status = f'OK ({images_count})'
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color, status
        )
    gallery_status.short_description = _('Статус галереи')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'city', 'country', 'category'
        ).annotate(
            images_count=Count('images')
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка отзывов"""
    list_display = ('user', 'excursion', 'rating', 'text', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__email', 'excursion__title_ru', 'text')
    readonly_fields = ('created_at',)
    inlines = [ReviewImageInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'excursion')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Админка бронирований"""
    list_display = (
        'excursion', 'user', 'date', 'people_count', 
        'total_price', 'status', 'created_at'
    )
    
    def get_total_price_display(self, obj):
        return f"{obj.total_price} {obj.excursion.currency}"
    get_total_price_display.short_description = 'Стоимость экскурсии'
    list_filter = ('status', 'date', 'created_at')
    search_fields = (
        'user__email', 'excursion__title_ru', 
        'contact_phone', 'contact_email'
    )
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Бронирование'), {
            'fields': ('excursion', 'user', 'date', 'people_count', 'total_price', 'status')
        }),
        (_('Контактная информация'), {
            'fields': ('contact_phone', 'contact_email', 'special_requests')
        }),
        (_('Системная информация'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'excursion')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Админка заявок"""
    list_display = (
        'name', 'destination', 'phone', 'email', 
        'people_count', 'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'destination')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Контактная информация'), {
            'fields': ('name', 'phone', 'email')
        }),
        (_('Детали поездки'), {
            'fields': ('destination', 'travel_dates', 'people_count', 'budget')
        }),
        (_('Сообщение'), {
            'fields': ('message',)
        }),
        (_('Обработка'), {
            'fields': ('status', 'created_at')
        }),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного"""
    list_display = ('user', 'item_type', 'get_item_name', 'created_at')
    list_filter = ('item_type', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at',)
    
    def get_item_name(self, obj):
        if obj.excursion:
            return f"Экскурсия: {obj.excursion.title_ru}"
        elif obj.category:
            return f"Категория: {obj.category.name_ru}"
        elif obj.country:
            return f"Страна: {obj.country.name_ru}"
        return "Неизвестный элемент"
    get_item_name.short_description = 'Элемент'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'excursion', 'category', 'country')


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Админка настроек пользователей"""
    list_display = ('user', 'email_notifications', 'push_notifications', 'profile_public', 'preferred_language')
    list_filter = ('email_notifications', 'push_notifications', 'profile_public', 'preferred_language', 'timezone')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Пользователь'), {
            'fields': ('user',)
        }),
        (_('Уведомления'), {
            'fields': ('email_notifications', 'push_notifications')
        }),
        (_('Приватность'), {
            'fields': ('profile_public', 'show_reviews')
        }),
        (_('Региональные настройки'), {
            'fields': ('preferred_language', 'timezone')
        }),
        (_('Системная информация'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Кастомизация админки
admin.site.site_header = 'SELEXIA Travel - Административная панель'
admin.site.site_title = 'SELEXIA Travel Admin'
admin.site.index_title = 'Добро пожаловать в панель управления'


# Добавляем дополнительные фильтры для лучшей навигации
class GalleryStatusFilter(admin.SimpleListFilter):
    """Фильтр по статусу галереи"""
    title = _('Статус галереи')
    parameter_name = 'gallery_status'
    
    def lookups(self, request, model_admin):
        return (
            ('valid', _('Валидная (6-15 фото)')),
            ('insufficient', _('Недостаточно фото')),
            ('excessive', _('Слишком много фото')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'valid':
            return queryset.annotate(
                images_count=Count('images')
            ).filter(images_count__gte=6, images_count__lte=15)
        elif self.value() == 'insufficient':
            return queryset.annotate(
                images_count=Count('images')
            ).filter(images_count__lt=6)
        elif self.value() == 'excessive':
            return queryset.annotate(
                images_count=Count('images')
            ).filter(images_count__gt=15)


# Добавляем фильтр в админку экскурсий
ExcursionAdmin.list_filter = ExcursionAdmin.list_filter + (GalleryStatusFilter,)