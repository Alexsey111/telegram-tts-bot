import os
import json
from typing import List, Dict, Optional
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import config

class VoiceManager:
    """Класс для управления голосами и генерацией аудио через ElevenLabs API"""
    
    def __init__(self):
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        
        # Создаем папку для временных аудио файлов
        if not os.path.exists(config.TEMP_AUDIO_DIR):
            os.makedirs(config.TEMP_AUDIO_DIR)
    
    def get_voices(self) -> List[Dict]:
        """
        Получает список доступных голосов (предустановленные голоса ElevenLabs)
        
        Returns:
            List[Dict]: Список голосов с их характеристиками
        """
        # Предустановленные голоса ElevenLabs, доступные всем пользователям
        default_voices = [
            {
                'voice_id': '21m00Tcm4TlvDq8ikWAM',  # Rachel
                'name': 'Rachel',
                'description': 'Calm, soothing voice perfect for narration',
                'category': 'premade',
                'labels': {'gender': 'female', 'age': 'young_adult'},
                'preview_url': ''
            },
            {
                'voice_id': 'AZnzlk1XvdvUeBnXmlld',  # Domi
                'name': 'Domi',
                'description': 'Confident, strong voice with authority',
                'category': 'premade',
                'labels': {'gender': 'female', 'age': 'middle_aged'},
                'preview_url': ''
            },
            {
                'voice_id': 'EXAVITQu4vr4xnSDxMaL',  # Bella
                'name': 'Bella',
                'description': 'Warm, friendly voice with character',
                'category': 'premade',
                'labels': {'gender': 'female', 'age': 'young_adult'},
                'preview_url': ''
            },
            {
                'voice_id': 'ErXwobaYiN019PkySvjV',  # Antoni
                'name': 'Antoni',
                'description': 'Professional, clear male voice',
                'category': 'premade',
                'labels': {'gender': 'male', 'age': 'young_adult'},
                'preview_url': ''
            },
            {
                'voice_id': 'MF3mGyEYCl7XYWbV9V6O',  # Elli
                'name': 'Elli',
                'description': 'Energetic, upbeat voice',
                'category': 'premade',
                'labels': {'gender': 'female', 'age': 'young_adult'},
                'preview_url': ''
            },
            {
                'voice_id': 'TxGEqnHWrfWFTfGW9XjX',  # Josh
                'name': 'Josh',
                'description': 'Deep, resonant male voice',
                'category': 'premade',
                'labels': {'gender': 'male', 'age': 'adult'},
                'preview_url': ''
            },
            {
                'voice_id': 'VR6AewLTigWG4xSOukaG',  # Arnold
                'name': 'Arnold',
                'description': 'Strong, authoritative male voice',
                'category': 'premade',
                'labels': {'gender': 'male', 'age': 'adult'},
                'preview_url': ''
            },
            {
                'voice_id': 'pNInz6obpgDQGcFmaJgB',  # Adam
                'name': 'Adam',
                'description': 'Clear, professional male voice',
                'category': 'premade',
                'labels': {'gender': 'male', 'age': 'young_adult'},
                'preview_url': ''
            },
            {
                'voice_id': 'yoZ06aMxZJJ28mfd3POQ',  # Sam
                'name': 'Sam',
                'description': 'Friendly, approachable male voice',
                'category': 'premade',
                'labels': {'gender': 'male', 'age': 'young_adult'},
                'preview_url': ''
            },
            {
                'voice_id': '2EiwWnXFnvU5JabPnv8n',  # Clyde
                'name': 'Clyde',
                'description': 'Wise, mature male voice',
                'category': 'premade',
                'labels': {'gender': 'male', 'age': 'senior'},
                'preview_url': ''
            }
        ]
        
        return default_voices
    
    def generate_audio(self, text: str, voice_id: str, output_filename: str = None) -> Optional[str]:
        """
        Генерирует аудио из текста с использованием указанного голоса
        
        Args:
            text (str): Текст для озвучки
            voice_id (str): ID голоса для озвучки
            output_filename (str, optional): Имя файла для сохранения аудио
            
        Returns:
            Optional[str]: Путь к сгенерированному аудио файлу или None в случае ошибки
        """
        try:
            # Проверяем длину текста
            if len(text) > config.MAX_TEXT_LENGTH:
                print(f"Текст слишком длинный. Максимум {config.MAX_TEXT_LENGTH} символов")
                return None
            
            # Генерируем имя файла если не указано
            if not output_filename:
                import time
                timestamp = int(time.time())
                output_filename = f"audio_{timestamp}.mp3"
            
            # Убеждаемся что файл имеет правильное расширение
            if not output_filename.endswith(('.mp3', '.wav')):
                output_filename += '.mp3'
            
            file_path = os.path.join(config.TEMP_AUDIO_DIR, output_filename)
            
            # Генерируем аудио используя официальную библиотеку
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            # Сохраняем аудио файл
            save(audio, file_path)
            
            print(f"Аудио успешно сгенерировано: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"Ошибка при генерации аудио: {e}")
            return None
    
    def get_voice_by_name(self, voice_name: str) -> Optional[Dict]:
        """
        Находит голос по имени
        
        Args:
            voice_name (str): Имя голоса для поиска
            
        Returns:
            Optional[Dict]: Данные голоса или None если не найден
        """
        voices = self.get_voices()
        for voice in voices:
            if voice['name'].lower() == voice_name.lower():
                return voice
        return None
    
    def get_default_voices(self) -> List[Dict]:
        """
        Возвращает список популярных голосов для быстрого доступа
        
        Returns:
            List[Dict]: Список популярных голосов
        """
        voices = self.get_voices()
        # Фильтруем популярные голоса (можно настроить по категориям)
        popular_voices = []
        for voice in voices[:10]:  # Берем первые 10 голосов
            popular_voices.append(voice)
        return popular_voices
    
    def cleanup_temp_files(self):
        """Очищает временные аудио файлы"""
        try:
            if os.path.exists(config.TEMP_AUDIO_DIR):
                for filename in os.listdir(config.TEMP_AUDIO_DIR):
                    file_path = os.path.join(config.TEMP_AUDIO_DIR, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print("Временные файлы очищены")
        except Exception as e:
            print(f"Ошибка при очистке временных файлов: {e}")


# Функции для удобного использования
def get_available_voices() -> List[Dict]:
    """Получить список доступных голосов"""
    voice_manager = VoiceManager()
    return voice_manager.get_voices()

def text_to_speech(text: str, voice_id: str, output_filename: str = None) -> Optional[str]:
    """Конвертировать текст в речь"""
    voice_manager = VoiceManager()
    return voice_manager.generate_audio(text, voice_id, output_filename)

def get_voice_by_name(voice_name: str) -> Optional[Dict]:
    """Найти голос по имени"""
    voice_manager = VoiceManager()
    return voice_manager.get_voice_by_name(voice_name)
