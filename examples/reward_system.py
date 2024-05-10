import os
import sys
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import random
from typing import List

from pycontroller import Controller

random.seed(0)


@dataclass
class Student:
    id: str
    age: int
    grades: List[float] = field(default_factory=lambda: list())
    bonus_points: float = 0.0

    @property
    def gpa(self):
        return sum(self.grades) / len(self.grades)


def student_generator(num_students: int, num_grades: int = 4) -> List[Student]:
    students = list()
    ids = [id for id in range(num_students)]
    ages = [random.randint(18, 22) for _ in range(num_students)]
    for id, age in zip(ids, ages):
        grades = [random.uniform(0.4, 1.0) for g in range(num_grades)]
        students.append(Student(id, age, grades))
    return students


if __name__ == "__main__":
    students = student_generator(10, 4)

    class CalculateBonus(Controller):
        no_partition = True
        static_mode = True

        @staticmethod
        def action(student: Student, weight: float) -> int:
            gpa = sum(student.grades) / len(student.grades)
            if gpa > 0.90:
                return 3 * weight
            elif gpa > 0.80:
                return 2 * weight
            elif gpa > 0.70:
                return 1 * weight
            return 0

    class StudentSelector(Controller):
        return_generator = True

        @staticmethod
        def filter(chosen: Student) -> bool:
            gpa = sum(chosen.grades) / len(chosen.grades)
            return gpa > 0.7

        @staticmethod
        def preference(a, b) -> int:
            return -1 if a.gpa > b.gpa else 1 if a.gpa < b.gpa else 0

    student_selector = StudentSelector()

    weight = 1.0
    num_awards = 4
    for student in student_selector(students):
        student: Student
        if num_awards == 0:
            break
        student.bonus_points += CalculateBonus(student, weight)
        num_awards -= 1

    pass
