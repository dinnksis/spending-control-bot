login = {}
is_authorized = {}


def checking_auth(us_id):
    if us_id not in is_authorized:
        is_authorized[us_id] = False
        login[us_id] = ''
        return False
    else:
        if is_authorized[us_id]:
            return True
        return False
