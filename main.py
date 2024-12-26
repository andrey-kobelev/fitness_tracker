
"""
Программный модуль фитнес-трекера.

Модуль обрабатывает данные для трёх видов тренировок:
бега, спортивной ходьбы и плавания.
"""

from dataclasses import dataclass
from typing import Any, Union

SWM: str = 'SWM'
RUN: str = 'RUN'
WLK: str = 'WLK'

# Значения констант - корректная длина списка для каждой тренировки.
LEN_FOR_SWM: int = 5
LEN_FOR_RUN: int = 3
LEN_FOR_WLK: int = 4

NOT_FOUND: str = 'Неизвестная тренировка.'
BAD_DATA: str = 'Некорректный пакет данных.'


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float

    def get_message(self):
        """Возвращает информационное сообщение о результатах тренировки."""
        return (f'Тип тренировки: {self.training_type}; '
                f'Длительность: {self.duration:.3f} ч.; '
                f'Дистанция: {self.distance:,.3f} км; '
                f'Ср. скорость: {self.speed:,.3f} км/ч; '
                f'Потрачено ккал: {self.calories:,.3f}.')


class Training:
    """Базовый класс тренировки."""

    # Расстояние, которое спортсмен преодолевает за один шаг.
    LEN_STEP: float = 0.65
    M_IN_KM: int = 1000
    MIN_IN_HOUR: int = 60

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 ) -> None:
        """Инициализирует атрибуты данных с датчиков фитнес-трекера."""
        self.action: int = action
        self.duration: float = duration
        self.weight: float = weight
        self.spent_calories: float = 0.0
        self.mean_speed_km_h: float = 0.0

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        distance_km: float = (self.action
                              * self.LEN_STEP
                              / self.M_IN_KM)

        return distance_km

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        self.mean_speed_km_h = self.get_distance() / self.duration

        return self.mean_speed_km_h

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        raise NotImplementedError

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        training_info: InfoMessage = InfoMessage(self.__class__.__name__,
                                                 self.duration,
                                                 self.get_distance(),
                                                 self.get_mean_speed(),
                                                 self.get_spent_calories())

        return training_info


class Running(Training):
    """Тренировка: бег."""

    CALORIES_MEAN_SPEED_MULTIPLIER: int = 18
    CALORIES_MEAN_SPEED_SHIFT: float = 1.79

    def get_spent_calories(self) -> float:
        """Расход калорий для бега."""
        self.spent_calories = (
            (self.CALORIES_MEAN_SPEED_MULTIPLIER
             * self.get_mean_speed()
             + self.CALORIES_MEAN_SPEED_SHIFT)
            * self.weight / self.M_IN_KM
            * (self.duration * self.MIN_IN_HOUR)
        )

        return self.spent_calories


class SportsWalking(Training):
    """Тренировка: спортивная ходьба."""

    CALORIES_WEIGHT_FACTOR_1: float = 0.035
    CALORIES_WEIGHT_FACTOR_2: float = 0.029
    M_TO_SEC_CONVERTER: float = 0.278
    CM_IN_METER: int = 100

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 height: float) -> None:
        """Инициализирует дополнительный атрибут: height."""
        super().__init__(action, duration, weight)
        # Рост сразу переводим в метры.
        self.height: float = height / self.CM_IN_METER

    def get_spent_calories(self) -> float:
        """Расчёт калорий для спортивной ходьбы."""
        meters_in_sec: float = self.get_mean_speed() * self.M_TO_SEC_CONVERTER

        self.spent_calories = (
            (
                self.CALORIES_WEIGHT_FACTOR_1 * self.weight
                + (meters_in_sec ** 2 / self.height)
                * self.CALORIES_WEIGHT_FACTOR_2 * self.weight
            )
            * self.duration * self.MIN_IN_HOUR
        )

        return self.spent_calories


class Swimming(Training):
    """Тренировка: плавание."""

    # Расстояние, которое спортсмен преодолевает за один гребок.
    LEN_STEP: float = 1.38
    SPEED_SWIM_SHIFT: float = 1.1
    CALORIES_SPEED_SWIM_MULTIPLIER: int = 2

    def __init__(self, action: int,
                 duration: float,
                 weight: float,
                 length_pool: float,
                 count_pool: int) -> None:
        """Инициализирует дополнительные атрибуты: length_pool, count_pool."""
        super().__init__(action, duration, weight)

        self.length_pool: float = length_pool
        self.count_pool: int = count_pool

    def get_mean_speed(self) -> float:
        """Рассчитывает среднюю скорость плавания."""
        self.mean_speed_km_h = (
            self.length_pool
            * self.count_pool
            / self.M_IN_KM
            / self.duration
        )

        return self.mean_speed_km_h

    def get_spent_calories(self) -> float:
        """Расчёт калорий для плавания."""
        self.spent_calories = (
            (
                self.get_mean_speed()
                + self.SPEED_SWIM_SHIFT
            )
            * self.CALORIES_SPEED_SWIM_MULTIPLIER
            * self.weight
            * self.duration
        )

        return self.spent_calories


def checking_correct_data(wrk_typ: str, dat_list: list) -> bool:
    """Проверка списка пакетов данных.

    Для каждой тренировки список проверяется на длину и присутствие None.
    """
    correct_list_length = {
        SWM: LEN_FOR_SWM,
        RUN: LEN_FOR_RUN,
        WLK: LEN_FOR_WLK
    }

    if None in dat_list:
        return False

    if len(dat_list) != correct_list_length[wrk_typ]:
        return False

    return True


def read_package(workout_tpe: str,
                 data_list: list[Union[int, float], ...]) -> Any:
    """Прочитать данные полученные от датчиков."""
    training_classes: dict = {
        SWM: Swimming,
        RUN: Running,
        WLK: SportsWalking
    }

    if workout_tpe not in training_classes:
        raise Exception(NOT_FOUND)

    if not checking_correct_data(workout_tpe, data_list):
        raise Exception(BAD_DATA)

    training_cls: Training = training_classes[workout_tpe](*data_list)

    return training_cls


def main(training_obj: Any) -> None:
    """Главная функция."""
    if isinstance(training_obj, Training):
        info: InfoMessage = training_obj.show_training_info()
        print(info.get_message())
    else:
        print(training_obj)


if __name__ == '__main__':
    packages: list[tuple[str, list]] = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        main(training)
