from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Avg, Count
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Review, Booking, Application, User, Excursion


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_excursion_rating(sender, instance, **kwargs):
    """Обновление рейтинга экскурсии при изменении отзывов"""
    excursion = instance.excursion
    
    # Пересчитываем рейтинг и количество отзывов
    reviews = excursion.reviews.filter(is_approved=True)
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    reviews_count = reviews.count()
    
    excursion.rating = round(avg_rating, 2) if avg_rating else 0
    excursion.reviews_count = reviews_count
    excursion.save(update_fields=['rating', 'reviews_count'])


@receiver(post_save, sender=Booking)
def send_booking_confirmation_email(sender, instance, created, **kwargs):
    """Отправка email подтверждения бронирования"""
    if created:
        try:
            # Email клиенту
            subject = f'Подтверждение бронирования - {instance.excursion.title_ru}'
            html_message = render_to_string('emails/booking_confirmation.html', {
                'booking': instance,
                'user': instance.user,
                'excursion': instance.excursion,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.contact_email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем создание бронирования
            print(f"Ошибка отправки email клиенту: {e}")
        
        try:
            # Email администратору
            admin_subject = f'Новое бронирование: {instance.excursion.title_ru}'
            admin_html_message = render_to_string('emails/booking_admin_notification.html', {
                'booking': instance,
            })
            admin_plain_message = strip_tags(admin_html_message)
            
            send_mail(
                subject=admin_subject,
                message=admin_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                html_message=admin_html_message,
                fail_silently=True,
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем создание бронирования
            print(f"Ошибка отправки email администратору: {e}")


@receiver(post_save, sender=Application)
def send_application_notification(sender, instance, created, **kwargs):
    """Отправка уведомления о новой заявке"""
    if created:
        # Email клиенту
        subject = 'Ваша заявка получена - SELEXIA Travel'
        html_message = render_to_string('emails/application_confirmation.html', {
            'application': instance,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        # Email администратору
        admin_subject = f'Новая заявка от {instance.name}'
        admin_html_message = render_to_string('emails/application_admin_notification.html', {
            'application': instance,
        })
        admin_plain_message = strip_tags(admin_html_message)
        
        send_mail(
            subject=admin_subject,
            message=admin_plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            html_message=admin_html_message,
            fail_silently=True,
        )


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """Отправка приветственного email новым пользователям"""
    if created and not instance.is_staff:
        subject = 'Добро пожаловать в SELEXIA Travel!'
        html_message = render_to_string('emails/welcome.html', {
            'user': instance,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            html_message=html_message,
            fail_silently=True,
        )


@receiver(pre_save, sender=Excursion)
def update_excursion_popularity(sender, instance, **kwargs):
    """Автоматическое обновление популярности экскурсии"""
    if instance.views_count >= 100:
        instance.is_popular = True


@receiver(post_save, sender=Review)
def send_review_notification(sender, instance, created, **kwargs):
    """Уведомление о новом отзыве"""
    if created:
        subject = f'Новый отзыв для экскурсии: {instance.excursion.title_ru}'
        html_message = render_to_string('emails/review_notification.html', {
            'review': instance,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            html_message=html_message,
            fail_silently=True,
        )