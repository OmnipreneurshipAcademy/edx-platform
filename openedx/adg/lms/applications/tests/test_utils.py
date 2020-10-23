from openedx.adg.lms.applications.utils import sum_of_two_numbers


def test_sum_of_two_numbers():
    assert sum_of_two_numbers(2, 3) == 5


def test_sum_of_another_two_numbers():
    assert sum_of_two_numbers(5, 5) == 10
