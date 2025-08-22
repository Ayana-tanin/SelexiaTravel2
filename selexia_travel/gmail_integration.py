"""
Интеграция с Gmail API для получения профиля пользователя
"""

import os
import json
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailProfileUpdater:
    """Класс для обновления профиля пользователя из Gmail"""
    
    # Если изменяете эти области, удалите файл token.json.
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email'
    ]
    
    def __init__(self):
        self.credentials_file = getattr(settings, 'GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = getattr(settings, 'GMAIL_TOKEN_FILE', 'token.json')
        
    def get_gmail_service(self, user):
        """Получает сервис Gmail для пользователя"""
        try:
            if user.needs_gmail_refresh():
                if not self.refresh_user_token(user):
                    return None
            
            credentials = Credentials(
                token=user.gmail_access_token,
                refresh_token=user.gmail_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET,
                scopes=self.SCOPES
            )
            
            service = build('gmail', 'v1', credentials=credentials)
            return service
            
        except Exception as e:
            print(f"Ошибка при создании Gmail сервиса: {e}")
            return None
    
    def get_user_profile(self, user):
        """Получает профиль пользователя из Gmail"""
        try:
            service = self.get_gmail_service(user)
            if not service:
                return None
            
            # Получаем профиль пользователя
            profile = service.users().getProfile(userId='me').execute()
            
            # Получаем дополнительную информацию о пользователе
            user_info = service.users().getProfile(userId='me').execute()
            
            return {
                'email': profile.get('emailAddress'),
                'name': profile.get('name'),
                'given_name': profile.get('givenName'),
                'family_name': profile.get('familyName'),
                'picture': profile.get('picture'),
                'locale': profile.get('locale'),
                'verified_email': profile.get('verifiedEmail', False)
            }
            
        except HttpError as error:
            print(f'Ошибка Gmail API: {error}')
            return None
        except Exception as e:
            print(f"Ошибка при получении профиля Gmail: {e}")
            return None
    
    def update_user_profile(self, user):
        """Обновляет профиль пользователя из Gmail"""
        try:
            profile_data = self.get_user_profile(user)
            if not profile_data:
                return False
            
            # Обновляем поля пользователя
            if profile_data.get('given_name') and not user.first_name:
                user.first_name = profile_data['given_name']
            
            if profile_data.get('family_name') and not user.last_name:
                user.last_name = profile_data['family_name']
            
            # Обновляем email если он изменился
            if profile_data.get('email') and profile_data['email'] != user.email:
                user.email = profile_data['email']
            
            # Сохраняем изменения
            user.save(update_fields=['first_name', 'last_name', 'email'])
            
            print(f"Профиль пользователя {user.email} обновлен из Gmail")
            return True
            
        except Exception as e:
            print(f"Ошибка при обновлении профиля пользователя: {e}")
            return False
    
    def refresh_user_token(self, user):
        """Обновляет токен доступа пользователя"""
        try:
            if not user.gmail_refresh_token:
                return False
            
            credentials = Credentials(
                token=user.gmail_access_token,
                refresh_token=user.gmail_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET,
                scopes=self.SCOPES
            )
            
            # Обновляем токен
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Сохраняем новый токен
                user.gmail_access_token = credentials.token
                user.gmail_token_expiry = timezone.now() + timedelta(hours=1)
                user.save(update_fields=['gmail_access_token', 'gmail_token_expiry'])
                
                print(f"Токен пользователя {user.email} обновлен")
                return True
            
            return False
            
        except Exception as e:
            print(f"Ошибка при обновлении токена: {e}")
            return False
    
    def get_gmail_messages(self, user, max_results=10):
        """Получает последние сообщения Gmail пользователя"""
        try:
            service = self.get_gmail_service(user)
            if not service:
                return []
            
            # Получаем список сообщений
            results = service.users().messages().list(
                userId='me', 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Получаем детали сообщений
            detailed_messages = []
            for message in messages:
                msg = service.users().messages().get(
                    userId='me', 
                    id=message['id']
                ).execute()
                
                # Извлекаем заголовки
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                detailed_messages.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': msg.get('snippet', '')
                })
            
            return detailed_messages
            
        except HttpError as error:
            print(f'Ошибка Gmail API: {error}')
            return []
        except Exception as e:
            print(f"Ошибка при получении сообщений Gmail: {e}")
            return []


class GmailOAuthHelper:
    """Помощник для OAuth аутентификации Gmail"""
    
    def __init__(self):
        self.credentials_file = getattr(settings, 'GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = getattr(settings, 'GMAIL_TOKEN_FILE', 'token.json')
    
    def get_authorization_url(self):
        """Получает URL для авторизации Gmail"""
        try:
            if not os.path.exists(self.credentials_file):
                print(f"Файл {self.credentials_file} не найден")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, 
                GmailProfileUpdater.SCOPES
            )
            
            # URL для авторизации
            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url, flow
            
        except Exception as e:
            print(f"Ошибка при создании URL авторизации: {e}")
            return None, None
    
    def exchange_code_for_tokens(self, flow, authorization_response):
        """Обменивает код авторизации на токены"""
        try:
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            
            return {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_expiry': credentials.expiry,
                'scopes': credentials.scopes
            }
            
        except Exception as e:
            print(f"Ошибка при обмене кода на токены: {e}")
            return None


def sync_user_with_gmail(user):
    """Синхронизирует пользователя с Gmail профилем"""
    try:
        updater = GmailProfileUpdater()
        return updater.update_user_profile(user)
    except Exception as e:
        print(f"Ошибка при синхронизации с Gmail: {e}")
        return False


def get_gmail_activity_summary(user):
    """Получает сводку активности пользователя в Gmail"""
    try:
        updater = GmailProfileUpdater()
        messages = updater.get_gmail_messages(user, max_results=5)
        
        if not messages:
            return "Нет новых сообщений"
        
        summary = f"Последние {len(messages)} сообщений:\n"
        for msg in messages:
            summary += f"- {msg['subject']} от {msg['sender']}\n"
        
        return summary
        
    except Exception as e:
        print(f"Ошибка при получении сводки Gmail: {e}")
        return "Ошибка при получении данных"
