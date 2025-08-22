from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from crispy_forms.bootstrap import FormActions
from datetime import date, timedelta

from .models import (
    User, Application, Booking, Review, Excursion, 
    Country, City, Category
)


class CustomUserCreationForm(forms.Form):
    """Кастомная форма регистрации через социальные сети"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Имя')})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Фамилия')})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Введите корректный номер телефона в формате: '+79991234567'")
        )],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Телефон')})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'social-registration-form'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('phone', css_class='form-group mb-3'),
            FormActions(
                Submit('submit', _('Завершить регистрацию'), css_class='btn btn-primary btn-lg w-100')
            )
        )


class UserProfileForm(UserChangeForm):
    """Форма редактирования профиля"""
    password = None
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar', 'date_of_birth')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('date_of_birth', css_class='form-group col-md-6 mb-3'),
                Column('avatar', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', _('Сохранить изменения'), css_class='btn btn-primary')
            )
        )


class ApplicationForm(forms.ModelForm):
    """Форма заявки с главной страницы"""
    
    class Meta:
        model = Application
        fields = [
            'name', 'phone', 'email', 'destination', 
            'travel_dates', 'people_count', 'budget', 'message'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ваше имя')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Номер телефона')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email адрес')
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Куда хотите поехать?')
            }),
            'travel_dates': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Даты поездки')
            }),
            'people_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Количество человек'),
                'min': '1'
            }),
            'budget': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Примерный бюджет')
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Расскажите о ваших пожеланиях...'),
                'rows': 4
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'application-form'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('email', css_class='form-group mb-3'),
            Row(
                Column('destination', css_class='form-group col-md-6 mb-3'),
                Column('travel_dates', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('people_count', css_class='form-group col-md-6 mb-3'),
                Column('budget', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('message', css_class='form-group mb-3'),
            FormActions(
                Submit('submit', _('Отправить заявку'), css_class='btn btn-primary btn-lg w-100')
            )
        )


class BookingForm(forms.ModelForm):
    """Форма бронирования экскурсии"""
    
    class Meta:
        model = Booking
        fields = [
            'excursion', 'date', 'people_count', 
            'contact_phone', 'contact_email', 'special_requests'
        ]
        widgets = {
            'excursion': forms.HiddenInput(),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'people_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ваш телефон')
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ваш email')
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Особые пожелания (необязательно)'),
                'rows': 3
            }),

        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Автоматически заполняем данные пользователя
        if user and user.is_authenticated:
            if user.phone:
                self.fields['contact_phone'].initial = user.phone
            if user.email:
                self.fields['contact_email'].initial = user.email
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'booking-form'
        self.helper.layout = Layout(
            'excursion',
            Row(
                Column('date', css_class='form-group col-md-6 mb-3'),
                Column('people_count', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('contact_phone', css_class='form-group col-md-6 mb-3'),
                Column('contact_email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('special_requests', css_class='form-group mb-3'),
            FormActions(
                Submit('submit', _('Забронировать'), css_class='btn btn-primary btn-lg w-100')
            )
        )
    
    def clean_date(self):
        booking_date = self.cleaned_data['date']
        print(f"DEBUG: Проверяем дату: {booking_date}")
        print(f"DEBUG: Сегодня: {date.today()}")
        
        if booking_date < date.today():
            print(f"DEBUG: Дата в прошлом!")
            raise forms.ValidationError(_('Дата бронирования не может быть в прошлом'))
        
        print(f"DEBUG: Дата прошла валидацию")
        return booking_date
    
    def clean_people_count(self):
        people_count = self.cleaned_data['people_count']
        excursion = self.cleaned_data.get('excursion')
        print(f"DEBUG: Проверяем количество человек: {people_count}")
        print(f"DEBUG: Экскурсия: {excursion}")
        if excursion:
            print(f"DEBUG: Максимум для экскурсии: {excursion.max_people}")
        
        if excursion and people_count > excursion.max_people:
            print(f"DEBUG: Слишком много человек!")
            raise forms.ValidationError(
                _('Максимальное количество участников: {}').format(excursion.max_people)
            )
        
        print(f"DEBUG: Количество человек прошло валидацию")
        return people_count


class ReviewForm(forms.ModelForm):
    """Форма отзыва"""
    photos = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label=_('Фотографии')
    )
    
    class Meta:
        model = Review
        fields = ['excursion', 'rating', 'text']
        widgets = {
            'excursion': forms.HiddenInput(),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Поделитесь своими впечатлениями об экскурсии...'),
                'rows': 4
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'review-form'
        self.helper.layout = Layout(
            'excursion',
            Field('text', css_class='form-group mb-3'),
            Field('photos', css_class='form-group mb-3'),
            FormActions(
                Submit('submit', _('Отправить отзыв'), css_class='btn btn-primary')
            )
        )
    
    def clean_photos(self):
        photos = self.files.getlist('photos')
        print(f"DEBUG: В clean_photos получено файлов: {len(photos)}")
        
        if len(photos) > 5:
            raise forms.ValidationError(_('Можно загрузить максимум 5 фотографий'))
        
        for i, photo in enumerate(photos):
            print(f"DEBUG: Проверяем фото {i+1}: {photo.name}, размер: {photo.size}")
            
            if photo.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(_('Размер каждого файла не должен превышать 5MB'))
            
            # Проверяем тип файла
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError(_('Можно загружать только изображения'))
        
        print(f"DEBUG: Все фото прошли валидацию")
        return photos


class ExcursionFilterForm(forms.Form):
    """Форма фильтрации экскурсий"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Поиск экскурсий...'),
            'id': 'search-input'
        })
    )
    
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        empty_label=_('Все страны'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False,
        empty_label=_('Все города'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label=_('Все категории'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    price_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('От'),
            'min': '0'
        })
    )
    
    price_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('До'),
            'min': '0'
        })
    )
    
    rating = forms.ChoiceField(
        choices=[
            ('', _('Любой рейтинг')),
            ('4', _('4+ звезды')),
            ('3', _('3+ звезды')),
            ('2', _('2+ звезды')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('popular', _('По популярности')),
            ('price_asc', _('Сначала дешевые')),
            ('price_desc', _('Сначала дорогие')),
            ('rating', _('По рейтингу')),
            ('newest', _('Новые')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если выбрана страна, фильтруем города
        if 'country' in self.data and self.data['country']:
            try:
                country_id = int(self.data['country'])
                self.fields['city'].queryset = City.objects.filter(country_id=country_id)
            except (ValueError, TypeError):
                pass


class ContactForm(forms.Form):
    """Форма обратной связи"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ваше имя')
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email адрес')
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Телефон (необязательно)')
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Тема сообщения')
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Ваше сообщение...'),
            'rows': 6
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('subject', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('message', css_class='form-group mb-3'),
            FormActions(
                Submit('submit', _('Отправить сообщение'), css_class='btn btn-primary btn-lg')
            )
        )


class NewsletterForm(forms.Form):
    """Форма подписки на рассылку"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ваш email адрес')
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'newsletter-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='col-md-8'),
                Column(
                    Submit('submit', _('Подписаться'), css_class='btn btn-primary'),
                    css_class='col-md-4'
                ),
                css_class='form-row'
            )
        )


class SearchForm(forms.Form):
    """Форма поиска на главной странице"""
    destination = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Куда хотите поехать?'),
            'id': 'destination-input'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-lg',
            'min': date.today().strftime('%Y-%m-%d')
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-lg',
            'min': date.today().strftime('%Y-%m-%d')
        })
    )
    
    people = forms.IntegerField(
        required=False,
        initial=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'min': '1',
            'max': '20'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'hero-search-form'
        self.helper.form_method = 'get'
        self.helper.form_action = '/catalog/'
        self.helper.layout = Layout(
            Row(
                Column('destination', css_class='col-lg-4 col-md-6 mb-3'),
                Column('date_from', css_class='col-lg-2 col-md-3 mb-3'),
                Column('date_to', css_class='col-lg-2 col-md-3 mb-3'),
                Column('people', css_class='col-lg-2 col-md-6 mb-3'),
                Column(
                    Submit('search', _('Найти'), css_class='btn btn-primary btn-lg w-100'),
                    css_class='col-lg-2 col-md-6 mb-3'
                ),
                css_class='form-row align-items-end'
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError(_('Дата окончания не может быть раньше даты начала'))
        
        return cleaned_data


class QuickBookingForm(forms.Form):
    """Быстрая форма бронирования"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ваше имя')
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Телефон')
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email')
        })
    )
    
    excursion_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'quick-booking-form'
        self.helper.layout = Layout(
            'excursion_id',
            Field('name', css_class='form-group mb-3'),
            Field('phone', css_class='form-group mb-3'),
            Field('email', css_class='form-group mb-3'),
            FormActions(
                Submit('submit', _('Быстрое бронирование'), css_class='btn btn-success btn-lg w-100')
            )
        )