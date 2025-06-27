from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Tuple

class ImageGenerator:
    """Генератор обучающих изображений для ментальной арифметики"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        self.bg_color = (255, 255, 255)  # Белый фон
        self.text_color = (50, 50, 50)   # Темно-серый текст
        self.accent_color = (0, 123, 255)  # Синий акцент
        self.success_color = (40, 167, 69)  # Зеленый
        
        # Пытаемся найти подходящий шрифт
        self.title_font = self._get_font(36)
        self.text_font = self._get_font(24)
        self.small_font = self._get_font(18)
    
    def _get_font(self, size: int):
        """Получение шрифта подходящего размера"""
        try:
            # Попытка использовать системный шрифт Windows
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except:
                # Используем стандартный шрифт PIL
                return ImageFont.load_default()
    
    def create_soroban_basics(self) -> str:
        """Создание изображения с основами соробана"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "🧮 ОСНОВЫ МЕНТАЛЬНОГО СЧЕТА"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 30), title, fill=self.accent_color, font=self.title_font)
        
        # Рисуем упрощенный соробан
        soroban_x = 50
        soroban_y = 100
        
        # Рамка соробана
        draw.rectangle([soroban_x, soroban_y, soroban_x + 300, soroban_y + 200], 
                      outline=self.text_color, width=3)
        
        # Разделительная линия
        draw.line([soroban_x, soroban_y + 60, soroban_x + 300, soroban_y + 60], 
                 fill=self.text_color, width=2)
        
        # Столбцы с косточками
        for i in range(5):
            col_x = soroban_x + 50 + i * 40
            
            # Верхняя косточка (5)
            draw.ellipse([col_x - 8, soroban_y + 20, col_x + 8, soroban_y + 40], 
                        fill=self.success_color)
            
            # Нижние косточки (1, 1, 1, 1)
            for j in range(4):
                bead_y = soroban_y + 80 + j * 25
                draw.ellipse([col_x - 8, bead_y, col_x + 8, bead_y + 20], 
                           fill=self.accent_color)
            
            # Вертикальная линия (стержень)
            draw.line([col_x, soroban_y + 10, col_x, soroban_y + 190], 
                     fill=self.text_color, width=2)
        
        # Объяснения
        explanations = [
            "• 1 верхняя косточка = 5 единиц",
            "• 4 нижние косточки = по 1 единице",
            "• Каждый столбец = разряд числа",
            "• Справа налево: единицы, десятки, сотни..."
        ]
        
        y_pos = 350
        for explanation in explanations:
            draw.text((50, y_pos), explanation, fill=self.text_color, font=self.text_font)
            y_pos += 40
        
        # Сохраняем изображение
        filepath = "media/photos/basics_1.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath
    
    def create_hand_position(self) -> str:
        """Создание изображения с позицией рук"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "🤲 ПРАВИЛЬНАЯ ПОЗИЦИЯ РУК"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 30), title, fill=self.accent_color, font=self.title_font)
        
        # Рисуем упрощенные руки
        # Правая рука
        draw.text((50, 120), "ПРАВАЯ РУКА:", fill=self.success_color, font=self.text_font)
        
        # Большой палец
        draw.ellipse([100, 160, 140, 200], fill=self.accent_color)
        draw.text((150, 170), "Большой палец", fill=self.text_color, font=self.small_font)
        draw.text((150, 190), "Верхние косточки (×5)", fill=self.text_color, font=self.small_font)
        
        # Указательный палец  
        draw.ellipse([100, 220, 140, 260], fill=self.success_color)
        draw.text((150, 230), "Указательный палец", fill=self.text_color, font=self.small_font)
        draw.text((150, 250), "Нижние косточки (×1)", fill=self.text_color, font=self.small_font)
        
        # Левая рука
        draw.text((400, 120), "ЛЕВАЯ РУКА:", fill=self.success_color, font=self.text_font)
        draw.text((400, 160), "• Придерживает соробан", fill=self.text_color, font=self.small_font)
        draw.text((400, 180), "• Помогает с большими числами", fill=self.text_color, font=self.small_font)
        draw.text((400, 200), "• Участвует в сложных операциях", fill=self.text_color, font=self.small_font)
        
        # Важные правила
        rules = [
            "ВАЖНЫЕ ПРАВИЛА:",
            "• Движения четкие и быстрые",
            "• Руки расслаблены",
            "• Взгляд следует за пальцами",
            "• Начинайте медленно, ускоряйтесь постепенно"
        ]
        
        y_pos = 320
        for i, rule in enumerate(rules):
            color = self.accent_color if i == 0 else self.text_color
            font = self.text_font if i == 0 else self.small_font
            draw.text((50, y_pos), rule, fill=color, font=font)
            y_pos += 30
        
        filepath = "media/photos/basics_7.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath
    
    def create_concentration_techniques(self) -> str:
        """Создание изображения с техниками концентрации"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "РАЗВИТИЕ КОНЦЕНТРАЦИИ"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 20), title, fill=self.accent_color, font=self.title_font)
        
        # Левая часть - круг дыхания
        center_x, center_y = 150, 180
        radius = 60
        
        # Круг дыхания
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], 
                    outline=self.accent_color, width=3)
        
        # Подписи к кругу
        draw.text((center_x - 20, center_y - 8), "ВДОХ", fill=self.success_color, font=self.small_font)
        draw.text((center_x - 40, center_y + 70), "4 - 4 - 4 - 4", fill=self.accent_color, font=self.small_font)
        
        # Правая часть - техники
        draw.text((300, 80), "ТЕХНИКИ КОНЦЕНТРАЦИИ:", fill=self.success_color, font=self.text_font)
        
        # Квадратное дыхание
        draw.text((300, 120), "Квадратное дыхание:", fill=self.accent_color, font=self.text_font)
        breathing_steps = [
            "• Вдох на 4 счета",
            "• Задержка на 4 счета", 
            "• Выдох на 4 счета",
            "• Пауза на 4 счета"
        ]
        
        y_pos = 150
        for step in breathing_steps:
            draw.text((310, y_pos), step, fill=self.text_color, font=self.small_font)
            y_pos += 25
        
        # Визуальная концентрация
        draw.text((300, 270), "Визуальная концентрация:", fill=self.accent_color, font=self.text_font)
        visual_steps = [
            "• Фокусировка на точке",
            "• Удержание образа соробана",
            "• Концентрация на движениях"
        ]
        
        y_pos = 300
        for step in visual_steps:
            draw.text((310, y_pos), step, fill=self.text_color, font=self.small_font)
            y_pos += 25
        
        # Практические советы внизу
        draw.text((50, 420), "ПРАКТИЧЕСКИЕ СОВЕТЫ:", fill=self.success_color, font=self.text_font)
        draw.text((60, 450), "• Занимайтесь в тихом месте", fill=self.text_color, font=self.small_font)
        draw.text((60, 475), "• Начинайте с 5-10 минут", fill=self.text_color, font=self.small_font)
        draw.text((400, 450), "• Уберите отвлекающие факторы", fill=self.text_color, font=self.small_font)
        draw.text((400, 475), "• Постепенно увеличивайте время", fill=self.text_color, font=self.small_font)
        
        filepath = "media/photos/basics_2.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath
    
    def create_speed_rules(self) -> str:
        """Создание изображения с правилами быстрого счета"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "⚡ ПРАВИЛА БЫСТРОГО СЧЕТА"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 30), title, fill=self.accent_color, font=self.title_font)
        
        # Принцип "Друзья"
        draw.text((50, 100), "🎯 ПРИНЦИП 'ДРУЗЬЯ':", fill=self.success_color, font=self.text_font)
        
        friends = [
            "1 + 4 = 5",
            "2 + 3 = 5"
        ]
        
        for i, friend in enumerate(friends):
            y = 140 + i * 30
            # Рамка для примера
            draw.rectangle([60, y - 5, 200, y + 25], outline=self.accent_color, width=2)
            draw.text((70, y), friend, fill=self.text_color, font=self.text_font)
        
        # Принцип "Братья"
        draw.text((300, 100), "🔄 ПРИНЦИП 'БРАТЬЯ':", fill=self.success_color, font=self.text_font)
        
        brothers = [
            "1 + 9 = 10",
            "2 + 8 = 10",
            "3 + 7 = 10", 
            "4 + 6 = 10"
        ]
        
        for i, brother in enumerate(brothers):
            y = 140 + i * 30
            # Рамка для примера
            draw.rectangle([310, y - 5, 450, y + 25], outline=self.accent_color, width=2)
            draw.text((320, y), brother, fill=self.text_color, font=self.text_font)
        
        # Последовательность обучения
        sequence = [
            "📚 ПОСЛЕДОВАТЕЛЬНОСТЬ ОБУЧЕНИЯ:",
            "1. Простое сложение и вычитание",
            "2. Работа с 'друзьями' (до 5)",
            "3. Работа с 'братьями' (до 10)", 
            "4. Двузначные числа",
            "5. Трехзначные числа"
        ]
        
        y_pos = 280
        for i, step in enumerate(sequence):
            color = self.success_color if i == 0 else self.text_color
            font = self.text_font if i == 0 else self.small_font
            draw.text((50, y_pos), step, fill=color, font=font)
            y_pos += 30
        
        filepath = "media/photos/basics_3.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath
    
    def create_memory_training(self) -> str:
        """Создание изображения с тренировкой памяти"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "🧠 ТРЕНИРОВКА ПАМЯТИ"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 30), title, fill=self.accent_color, font=self.title_font)
        
        # Пример числовой цепочки
        chain = "3 → 7 → 2 → 9 → 5"
        chain_bbox = draw.textbbox((0, 0), chain, font=self.title_font)
        chain_x = (self.width - (chain_bbox[2] - chain_bbox[0])) // 2
        
        # Рамка для цепочки
        draw.rectangle([chain_x - 20, 90, chain_x + (chain_bbox[2] - chain_bbox[0]) + 20, 130], 
                      fill=(240, 248, 255), outline=self.accent_color, width=2)
        draw.text((chain_x, 100), chain, fill=self.accent_color, font=self.title_font)
        
        # Упражнения
        exercises = [
            "🔢 ЧИСЛОВЫЕ ЦЕПОЧКИ:",
            "• Запомните последовательность",
            "• Воспроизведите в прямом порядке",
            "• Воспроизведите в обратном порядке",
            "",
            "🎨 ВИЗУАЛЬНАЯ ПАМЯТЬ:",
            "• Запоминайте расположение косточек",
            "• Создавайте яркие образы чисел",
            "• Используйте цветовые ассоциации",
            "",
            "🔄 ПОСЛЕДОВАТЕЛЬНОСТИ:",
            "• Запоминайте цепочки вычислений",
            "• Удерживайте промежуточные результаты"
        ]
        
        y_pos = 170
        for exercise in exercises:
            if exercise.startswith("🔢") or exercise.startswith("🎨") or exercise.startswith("🔄"):
                color = self.success_color
                font = self.text_font
            elif exercise == "":
                y_pos += 10
                continue
            else:
                color = self.text_color
                font = self.small_font
            
            draw.text((50, y_pos), exercise, fill=color, font=font)
            y_pos += 25
        
        filepath = "media/photos/basics_4.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath

    def create_addition_examples(self) -> str:
        """Создание изображения с примерами сложения"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "ПРИМЕРЫ СЛОЖЕНИЯ"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 20), title, fill=self.accent_color, font=self.title_font)
        
        # Левая колонка - простые примеры
        draw.text((50, 80), "ПРОСТЫЕ:", fill=self.success_color, font=self.text_font)
        
        simple_examples = ["2 + 3 = 5", "4 + 1 = 5", "1 + 2 = 3"]
        y_pos = 110
        for example in simple_examples:
            draw.rectangle([50, y_pos - 3, 200, y_pos + 22], 
                         outline=self.accent_color, width=1, fill=(240, 248, 255))
            draw.text((60, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Правая колонка - с переходом  
        draw.text((300, 80), "С ПЕРЕХОДОМ:", fill=self.success_color, font=self.text_font)
        
        complex_examples = ["7 + 4 = 11", "9 + 3 = 12", "8 + 6 = 14"]
        y_pos = 110
        for example in complex_examples:
            draw.rectangle([300, y_pos - 3, 450, y_pos + 22], 
                         outline=self.accent_color, width=1, fill=(240, 248, 255))
            draw.text((310, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Двузначные примеры (широкие блоки)
        draw.text((50, 240), "ДВУЗНАЧНЫЕ:", fill=self.success_color, font=self.text_font)
        
        big_examples = ["23 + 15 = 38", "47 + 29 = 76", "34 + 28 = 62"]
        y_pos = 270
        for example in big_examples:
            draw.rectangle([50, y_pos - 3, 250, y_pos + 22], 
                         outline=self.accent_color, width=1, fill=(240, 248, 255))
            draw.text((60, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Советы внизу
        draw.text((50, 380), "СОВЕТЫ:", fill=self.success_color, font=self.text_font)
        tips = [
            "• Начинайте с простых примеров",
            "• Представляйте движения на соробане", 
            "• Тренируйтесь каждый день по 10-15 минут"
        ]
        
        y_pos = 410
        for tip in tips:
            draw.text((60, y_pos), tip, fill=self.text_color, font=self.small_font)
            y_pos += 25
        
        filepath = "media/photos/basics_5.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath

    def create_subtraction_examples(self) -> str:
        """Создание изображения с примерами вычитания"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "➖ ПРИМЕРЫ ВЫЧИТАНИЯ"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 20), title, fill=self.accent_color, font=self.title_font)
        
        # Левая колонка - простые примеры
        draw.text((50, 80), "ПРОСТЫЕ:", fill=self.success_color, font=self.text_font)
        
        simple_examples = ["5 - 2 = 3", "8 - 3 = 5", "7 - 4 = 3"]
        y_pos = 110
        for example in simple_examples:
            draw.rectangle([50, y_pos - 3, 200, y_pos + 22], 
                         outline=(220, 53, 69), width=1, fill=(253, 237, 241))
            draw.text((60, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Правая колонка - с занятием
        draw.text((300, 80), "С ЗАНЯТИЕМ:", fill=self.success_color, font=self.text_font)
        
        complex_examples = ["12 - 7 = 5", "15 - 8 = 7", "23 - 9 = 14"]
        y_pos = 110
        for example in complex_examples:
            draw.rectangle([300, y_pos - 3, 450, y_pos + 22], 
                         outline=(220, 53, 69), width=1, fill=(253, 237, 241))
            draw.text((310, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Большие числа (широкие блоки)
        draw.text((50, 240), "БОЛЬШИЕ ЧИСЛА:", fill=self.success_color, font=self.text_font)
        
        big_examples = ["56 - 28 = 28", "84 - 37 = 47", "93 - 46 = 47"]
        y_pos = 270
        for example in big_examples:
            draw.rectangle([50, y_pos - 3, 250, y_pos + 22], 
                         outline=(220, 53, 69), width=1, fill=(253, 237, 241))
            draw.text((60, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Техники (объединяем в один блок, чтобы избежать наложения)
        draw.text((50, 370), "ТЕХНИКИ ВЫЧИТАНИЯ:", fill=self.accent_color, font=self.text_font)
        
        # Левая колонка техник
        left_techniques = [
            "• При занятии из старшего разряда",
            "• Движения должны быть точными", 
            "• Проверяйте результат"
        ]
        
        y_pos = 400
        for technique in left_techniques:
            draw.text((60, y_pos), technique, fill=self.text_color, font=self.small_font)
            y_pos += 25
        
        # Правая колонка техник
        right_techniques = [
            "• Дополнение до круглого числа",
            "• Разбивка на части",
            "• Использование 'друзей'"
        ]
        
        y_pos = 400
        for technique in right_techniques:
            draw.text((400, y_pos), technique, fill=self.text_color, font=self.small_font)
            y_pos += 25
        
        filepath = "media/photos/basics_6.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath

    def create_multiplication_table(self) -> str:
        """Создание изображения с таблицей умножения"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "✖️ ТАБЛИЦА УМНОЖЕНИЯ"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 30), title, fill=self.accent_color, font=self.title_font)
        
        # Создаем сетку умножения
        start_x, start_y = 50, 100
        cell_width, cell_height = 70, 30
        
        # Заголовки
        for i in range(1, 6):
            # Горизонтальные заголовки
            draw.rectangle([start_x + i * cell_width, start_y, 
                           start_x + (i + 1) * cell_width, start_y + cell_height],
                          fill=self.accent_color)
            draw.text((start_x + i * cell_width + 25, start_y + 8), 
                     str(i), fill='white', font=self.text_font)
            
            # Вертикальные заголовки
            draw.rectangle([start_x, start_y + i * cell_height, 
                           start_x + cell_width, start_y + (i + 1) * cell_height],
                          fill=self.accent_color)
            draw.text((start_x + 25, start_y + i * cell_height + 8), 
                     str(i), fill='white', font=self.text_font)
        
        # Заполняем таблицу
        for i in range(1, 6):
            for j in range(1, 6):
                result = i * j
                x = start_x + j * cell_width
                y = start_y + i * cell_height
                
                # Рамка ячейки
                draw.rectangle([x, y, x + cell_width, y + cell_height],
                              outline=self.text_color, width=1)
                
                # Результат
                text_x = x + (cell_width - 20) // 2
                text_y = y + 8
                draw.text((text_x, text_y), str(result), 
                         fill=self.text_color, font=self.text_font)
        
        # Полезные факты
        facts = [
            "🎯 ПОЛЕЗНЫЕ ФАКТЫ:",
            "• 2 × любое число = удваивание",
            "• 5 × четное = заканчивается на 0", 
            "• 9 × любое = сумма цифр кратна 9",
            "• Практикуйтесь с простыми числами"
        ]
        
        y_pos = 300
        for fact in facts:
            color = self.success_color if fact.startswith("🎯") else self.text_color
            font = self.text_font if fact.startswith("🎯") else self.small_font
            draw.text((50, y_pos), fact, fill=color, font=font)
            y_pos += 25
        
        filepath = "media/photos/basics_8.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath

    def create_division_basics(self) -> str:
        """Создание изображения с основами деления"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "ОСНОВЫ ДЕЛЕНИЯ"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 20), title, fill=self.accent_color, font=self.title_font)
        
        # Колонка "НА 2"
        draw.text((50, 80), "НА 2:", fill=self.success_color, font=self.text_font)
        examples_2 = ["8 ÷ 2 = 4", "12 ÷ 2 = 6", "16 ÷ 2 = 8"]
        y_pos = 110
        for example in examples_2:
            draw.rectangle([50, y_pos - 3, 170, y_pos + 22], 
                         outline=(255, 193, 7), width=1, fill=(255, 248, 225))
            draw.text((60, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Колонка "НА 5"
        draw.text((200, 80), "НА 5:", fill=self.success_color, font=self.text_font)
        examples_5 = ["15 ÷ 5 = 3", "25 ÷ 5 = 5", "35 ÷ 5 = 7"]
        y_pos = 110
        for example in examples_5:
            draw.rectangle([200, y_pos - 3, 320, y_pos + 22], 
                         outline=(255, 193, 7), width=1, fill=(255, 248, 225))
            draw.text((210, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Колонка "НА 10"
        draw.text((350, 80), "НА 10:", fill=self.success_color, font=self.text_font)
        examples_10 = ["30 ÷ 10 = 3", "50 ÷ 10 = 5", "80 ÷ 10 = 8"]
        y_pos = 110
        for example in examples_10:
            draw.rectangle([350, y_pos - 3, 480, y_pos + 22], 
                         outline=(255, 193, 7), width=1, fill=(255, 248, 225))
            draw.text((360, y_pos), example, fill=self.text_color, font=self.small_font)
            y_pos += 30
        
        # Стратегии внизу
        draw.text((50, 250), "СТРАТЕГИИ ДЕЛЕНИЯ:", fill=(255, 193, 7), font=self.text_font)
        
        strategies = [
            "• Деление как обратное умножение",
            "• Используйте знакомые факты", 
            "• Разбивайте на простые части",
            "• Проверяйте умножением"
        ]
        
        y_pos = 280
        for strategy in strategies:
            draw.text((60, y_pos), strategy, fill=self.text_color, font=self.small_font)
            y_pos += 25
        
        # Практические советы
        draw.text((50, 390), "ПРАКТИЧЕСКИЕ СОВЕТЫ:", fill=self.success_color, font=self.text_font)
        draw.text((60, 420), "• Начинайте с деления на 2, 5, 10", fill=self.text_color, font=self.small_font)
        draw.text((60, 445), "• Изучите связь с умножением", fill=self.text_color, font=self.small_font)
        draw.text((60, 470), "• Тренируйте устный счет", fill=self.text_color, font=self.small_font)
        
        filepath = "media/photos/basics_9.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath

    def create_advanced_techniques(self) -> str:
        """Создание изображения с продвинутыми техниками"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        title = "🚀 ПРОДВИНУТЫЕ ТЕХНИКИ"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_x = (self.width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 30), title, fill=self.accent_color, font=self.title_font)
        
        # Техники
        techniques = [
            "🔥 СКОРОСТНЫЕ МЕТОДЫ:",
            "",
            "⚡ Дополнение до 10:",
            "   7 + ? = 10 → думайте '3'",
            "   4 + ? = 10 → думайте '6'",
            "",
            "💫 Дополнение до 100:", 
            "   68 + ? = 100 → думайте '32'",
            "   45 + ? = 100 → думайте '55'",
            "",
            "🎯 Разложение чисел:",
            "   23 = 20 + 3",
            "   57 = 50 + 7"
        ]
        
        y_pos = 100
        for technique in techniques:
            if technique.startswith("🔥"):
                color = (220, 53, 69)
                font = self.text_font
            elif technique.startswith("⚡") or technique.startswith("💫") or technique.startswith("🎯"):
                color = self.success_color
                font = self.text_font
            elif technique == "":
                y_pos += 10
                continue
            else:
                color = self.text_color
                font = self.small_font
            
            draw.text((50, y_pos), technique, fill=color, font=font)
            y_pos += 25
        
        # Практические советы
        tips_box_y = 420
        draw.rectangle([40, tips_box_y, 760, tips_box_y + 120], 
                      fill=(240, 248, 255), outline=self.accent_color, width=2)
        
        draw.text((50, tips_box_y + 10), "💡 ПРАКТИЧЕСКИЕ СОВЕТЫ:", 
                 fill=self.accent_color, font=self.text_font)
        draw.text((50, tips_box_y + 40), "• Практикуйтесь ежедневно минимум 15 минут", 
                 fill=self.text_color, font=self.small_font)
        draw.text((50, tips_box_y + 60), "• Постепенно увеличивайте скорость", 
                 fill=self.text_color, font=self.small_font)
        draw.text((50, tips_box_y + 80), "• Визуализируйте движения даже без соробана", 
                 fill=self.text_color, font=self.small_font)
        
        filepath = "media/photos/basics_10.jpg"
        img.save(filepath, "JPEG", quality=95)
        return filepath

def generate_all_basic_images():
    """Генерация всех базовых изображений"""
    generator = ImageGenerator()
    
    # Создаем папку если не существует
    os.makedirs("media/photos", exist_ok=True)
    
    generated_files = []
    
    print("🎨 Генерирую обучающие изображения...")
    
    # Основы ментального счета
    file1 = generator.create_soroban_basics()
    generated_files.append(file1)
    print(f"✅ Создано: {file1}")
    
    # Развитие концентрации
    file2 = generator.create_concentration_techniques() 
    generated_files.append(file2)
    print(f"✅ Создано: {file2}")
    
    # Правила быстрого счета
    file3 = generator.create_speed_rules()
    generated_files.append(file3)
    print(f"✅ Создано: {file3}")
    
    # Тренировка памяти
    file4 = generator.create_memory_training()
    generated_files.append(file4)
    print(f"✅ Создано: {file4}")
    
    # Примеры сложения
    file5 = generator.create_addition_examples()
    generated_files.append(file5)
    print(f"✅ Создано: {file5}")
    
    # Примеры вычитания
    file6 = generator.create_subtraction_examples()
    generated_files.append(file6)
    print(f"✅ Создано: {file6}")
    
    # Позиция рук (перезапишем существующий файл лучшей версией)
    file7 = generator.create_hand_position()
    generated_files.append(file7)
    print(f"✅ Обновлено: {file7}")
    
    # Таблица умножения
    file8 = generator.create_multiplication_table()
    generated_files.append(file8)
    print(f"✅ Создано: {file8}")
    
    # Основы деления
    file9 = generator.create_division_basics()
    generated_files.append(file9)
    print(f"✅ Создано: {file9}")
    
    # Продвинутые техники
    file10 = generator.create_advanced_techniques()
    generated_files.append(file10)
    print(f"✅ Создано: {file10}")
    
    print(f"\n🎉 Успешно создано {len(generated_files)} обучающих изображений!")
    return generated_files

if __name__ == "__main__":
    generate_all_basic_images() 