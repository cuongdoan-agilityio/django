from faker import Faker
import random
from datetime import date, timedelta

fake = Faker()


def random_birthday(is_student=False):
    """
    Generate a random date of birth.
    - Student: between 6 and 100 years ago.
    - Instructor:  between 18 and 100 years ago.

    Returns:
        date: A random date of birth.
    """

    today = date.today()
    min_years_ago = today - timedelta(days=18 * 365)

    if is_student:
        min_years_ago = today - timedelta(days=6 * 365)

    max_years_ago = today - timedelta(days=100 * 365)

    start_date = max_years_ago
    end_date = min_years_ago

    return fake.date_between_dates(date_start=start_date, date_end=end_date)


def random_phone_number():
    """
    Generate a random phone number with a length between 10 and 11 digits.

    Returns:
        str: A random phone number.
    """

    length = random.randint(10, 11)
    phone_number = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return phone_number
