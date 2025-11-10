from student_registration.students import utils


def test_generate_id_simple():
    uid = utils.generate_id(
        first_name='Ali',
        father_name='Hassan',
        last_name='Rahman',
        mother_full_name='Fatima',
        gender='Male',
        birthday_day='05',
        birthday_month='07',
        birthday_year='2000'
    )
    assert uid == '15063024566856M'


def test_list_to_string():
    assert utils.listToString(['a', 'b', 'c']) == 'a,b,c'
