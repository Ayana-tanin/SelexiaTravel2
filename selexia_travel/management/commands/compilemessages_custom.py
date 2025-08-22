"""
Кастомная команда Django для компиляции переводов без GNU gettext
Использует babel для компиляции .po файлов в .mo
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo


class Command(BaseCommand):
    help = 'Компилирует .po файлы в .mo файлы используя babel (без GNU gettext)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--locale', '-l',
            dest='locale',
            help='Компилирует файлы для указанной локали (например, ru, en)'
        )
        parser.add_argument(
            '--all', '-a',
            action='store_true',
            dest='all',
            help='Компилирует файлы для всех локалей'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Начинаю компиляцию переводов...')
        
        locale_paths = getattr(settings, 'LOCALE_PATHS', [])
        if not locale_paths:
            self.stdout.write(self.style.ERROR('❌ LOCALE_PATHS не настроен в settings.py'))
            return
        
        success_count = 0
        total_count = 0
        
        for locale_path in locale_paths:
            locale_path = Path(locale_path)
            if not locale_path.exists():
                continue
            
            # Определяем какие локали компилировать
            if options['locale']:
                locales_to_compile = [options['locale']]
            elif options['all']:
                locales_to_compile = [d.name for d in locale_path.iterdir() 
                                   if d.is_dir() and d.name != '__pycache__']
            else:
                # По умолчанию компилируем все
                locales_to_compile = [d.name for d in locale_path.iterdir() 
                                   if d.is_dir() and d.name != '__pycache__']
            
            for locale in locales_to_compile:
                lc_messages_dir = locale_path / locale / 'LC_MESSAGES'
                if lc_messages_dir.exists():
                    po_file = lc_messages_dir / 'django.po'
                    mo_file = lc_messages_dir / 'django.mo'
                    
                    if po_file.exists():
                        total_count += 1
                        if self._compile_po_to_mo(po_file, mo_file):
                            success_count += 1
        
        self.stdout.write(f"\n📊 Результат компиляции:")
        self.stdout.write(f"✅ Успешно: {success_count}/{total_count}")
        
        if success_count == total_count:
            self.stdout.write(self.style.SUCCESS('🎉 Все переводы успешно скомпилированы!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Некоторые переводы не удалось скомпилировать'))

    def _compile_po_to_mo(self, po_file_path, mo_file_path):
        """Компилирует .po файл в .mo файл"""
        try:
            # Читаем .po файл
            with open(po_file_path, 'r', encoding='utf-8') as f:
                catalog = read_po(f)
            
            # Записываем .mo файл
            with open(mo_file_path, 'wb') as f:
                write_mo(f, catalog)
            
            self.stdout.write(f"✅ Скомпилирован: {po_file_path} -> {mo_file_path}")
            return True
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ошибка компиляции {po_file_path}: {e}")
            )
            return False
