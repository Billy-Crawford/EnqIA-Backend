def check_age_group(age, group):

    if age is None:
        return False

    if group == "18-25":
        return 18 <= age <= 25

    if group == "26-35":
        return 26 <= age <= 35

    if group == "36-50":
        return 36 <= age <= 50

    if group == "50+":
        return age > 50

    return False