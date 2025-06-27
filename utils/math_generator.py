import random
from typing import Tuple, List

class MathProblemGenerator:
    """Генератор математических задач для ментальной арифметики"""
    
    def __init__(self):
        self.level_configs = {
            1: {"type": "addition", "range": (1, 10), "terms": 2},
            2: {"type": "subtraction", "range": (1, 10), "terms": 2},
            3: {"type": "addition", "range": (10, 50), "terms": 2},
            4: {"type": "subtraction", "range": (10, 50), "terms": 2},
            5: {"type": "addition", "range": (1, 20), "terms": 3},
            6: {"type": "mixed", "range": (10, 30), "terms": 2},
            7: {"type": "multiplication", "range": (2, 12), "terms": 2},
            8: {"type": "addition", "range": (50, 100), "terms": 2},
            9: {"type": "mixed_advanced", "range": (10, 50), "terms": 3},
            10: {"type": "challenge", "range": (10, 100), "terms": 4}
        }
    
    def generate_problem(self, level: int) -> Tuple[str, int]:
        """
        Генерирует задачу для указанного уровня
        
        Args:
            level: Уровень сложности (1-10)
            
        Returns:
            Tuple[str, int]: (текст_задачи, правильный_ответ)
        """
        if level not in self.level_configs:
            level = 1
        
        config = self.level_configs[level]
        problem_type = config["type"]
        num_range = config["range"]
        terms_count = config["terms"]
        
        if problem_type == "addition":
            return self._generate_addition(num_range, terms_count)
        elif problem_type == "subtraction":
            return self._generate_subtraction(num_range)
        elif problem_type == "multiplication":
            return self._generate_multiplication(num_range)
        elif problem_type == "mixed":
            return self._generate_mixed(num_range)
        elif problem_type == "mixed_advanced":
            return self._generate_mixed_advanced(num_range, terms_count)
        elif problem_type == "challenge":
            return self._generate_challenge(num_range, terms_count)
        else:
            return self._generate_addition(num_range, terms_count)
    
    def _generate_addition(self, num_range: Tuple[int, int], terms: int) -> Tuple[str, int]:
        """Генерация задач на сложение"""
        numbers = [random.randint(*num_range) for _ in range(terms)]
        problem = " + ".join(map(str, numbers))
        answer = sum(numbers)
        return f"{problem} = ?", answer
    
    def _generate_subtraction(self, num_range: Tuple[int, int]) -> Tuple[str, int]:
        """Генерация задач на вычитание"""
        # Убеждаемся, что результат положительный
        a = random.randint(num_range[0], num_range[1])
        b = random.randint(num_range[0], min(a, num_range[1]))
        problem = f"{a} - {b}"
        answer = a - b
        return f"{problem} = ?", answer
    
    def _generate_multiplication(self, num_range: Tuple[int, int]) -> Tuple[str, int]:
        """Генерация задач на умножение"""
        a = random.randint(*num_range)
        b = random.randint(2, 9)  # Таблица умножения
        problem = f"{a} × {b}"
        answer = a * b
        return f"{problem} = ?", answer
    
    def _generate_mixed(self, num_range: Tuple[int, int]) -> Tuple[str, int]:
        """Генерация смешанных задач (сложение и вычитание)"""
        operation = random.choice(["+", "-"])
        
        if operation == "+":
            return self._generate_addition(num_range, 2)
        else:
            return self._generate_subtraction(num_range)
    
    def _generate_mixed_advanced(self, num_range: Tuple[int, int], terms: int) -> Tuple[str, int]:
        """Генерация продвинутых смешанных задач"""
        numbers = [random.randint(*num_range) for _ in range(terms)]
        operations = [random.choice(["+", "-"]) for _ in range(terms - 1)]
        
        # Строим выражение
        expression_parts = [str(numbers[0])]
        for i, op in enumerate(operations):
            expression_parts.append(f" {op} {numbers[i + 1]}")
        
        problem = "".join(expression_parts)
        
        # Вычисляем ответ
        answer = numbers[0]
        for i, op in enumerate(operations):
            if op == "+":
                answer += numbers[i + 1]
            else:
                answer -= numbers[i + 1]
        
        # Если ответ отрицательный, меняем местами
        if answer < 0:
            # Переставляем числа, чтобы получить положительный результат
            numbers.sort(reverse=True)
            problem = f"{numbers[0]} - {numbers[1]}"
            answer = numbers[0] - numbers[1]
        
        return f"{problem} = ?", answer
    
    def _generate_challenge(self, num_range: Tuple[int, int], terms: int) -> Tuple[str, int]:
        """Генерация сложных задач для высокого уровня"""
        # Случайный выбор типа задачи
        challenge_type = random.choice(["multi_add", "multi_sub", "mixed_operations"])
        
        if challenge_type == "multi_add":
            numbers = [random.randint(*num_range) for _ in range(terms)]
            problem = " + ".join(map(str, numbers))
            answer = sum(numbers)
        
        elif challenge_type == "multi_sub":
            # Большое число минус несколько меньших
            big_num = random.randint(num_range[1] - 20, num_range[1])
            small_nums = [random.randint(5, 15) for _ in range(terms - 1)]
            
            problem = str(big_num)
            answer = big_num
            for num in small_nums:
                problem += f" - {num}"
                answer -= num
            
            # Если получился отрицательный результат, корректируем
            if answer < 0:
                return self._generate_addition(num_range, terms)
        
        else:  # mixed_operations
            # Смешанные операции с умножением
            a = random.randint(2, 10)
            b = random.randint(2, 9)
            c = random.randint(5, 20)
            
            operation = random.choice(["+", "-"])
            problem = f"{a} × {b} {operation} {c}"
            
            if operation == "+":
                answer = a * b + c
            else:
                answer = a * b - c
        
        return f"{problem} = ?", answer
    
    def get_level_description(self, level: int) -> str:
        """Получить описание уровня"""
        descriptions = {
            1: "🎯 Сложение чисел от 1 до 10",
            2: "➖ Вычитание чисел от 1 до 10", 
            3: "➕ Сложение чисел от 10 до 50",
            4: "➖ Вычитание чисел от 10 до 50",
            5: "🔢 Сложение трёх чисел",
            6: "🔄 Смешанные операции",
            7: "✖️ Умножение (таблица умножения)",
            8: "📈 Большие числа (до 100)",
            9: "🧠 Сложные выражения",
            10: "👑 Мастер-уровень"
        }
        return descriptions.get(level, "📚 Обычный уровень")
    
    def get_difficulty_emoji(self, level: int) -> str:
        """Получить эмодзи сложности для уровня"""
        if level <= 2:
            return "🟢"  # Легко
        elif level <= 5:
            return "🟡"  # Средне
        elif level <= 8:
            return "🟠"  # Сложно
        else:
            return "🔴"  # Очень сложно

# Глобальный экземпляр генератора
math_generator = MathProblemGenerator() 