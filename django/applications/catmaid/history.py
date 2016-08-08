from django.db import connection

from django.db.transaction import TransactionManagementError


def add_log_entry(user_id, label):
    """Give a label to the current transaction and time, executed by a
    particular user. This information is recorded only once per transaction, and
    subsequent calls will be ignored silently.
    """
    cursor = connection.cursor()
    # Only try to insert log record if current transaction is still valid
    if not cursor.db.needs_rollback:
        cursor.execute("""
            INSERT INTO catmaid_transaction_info (user_id, change_type, label)
            VALUES (%s, 'Backend', %s)
            ON CONFLICT DO NOTHING
        """, (user_id, label))


def record_request_action(label, method=None):
    """Give a label to the current transaction and time, executed by a Django
    user as provided by the wrapped function's request parameter. This
    parameter is first looked up in the function's keyword arguments and if not
    found, the request is expected to be provided as the first argument. If
    <method> is set to a particular HTTP method (i.e. GET or POST), only these
    requests are recorded.
    """
    if method and not method.isupper():
        raise ValueError("Method name must be upper case")

    def decorator(f):
        def wrapped_f(*args, **kwargs):
            if 'request' in kwargs:
                request = kwargs['request']
            elif len(args) > 0:
                request = args[0]
            else:
                raise ValueError("Couldn't find request to record action for")

            result = f(*args, **kwargs)

            user_id = request.user.id
            if not method or request.method == method:
                add_log_entry(user_id, label)

            return result
        return wrapped_f
    return decorator


def record_action(user_id, label):
    """Give a label to the current transaction and time, executed by a
    particular user.
    """
    def decorator(f):
        def wrapped_f(*args, **kwargs):
            result = f(*args, **kwargs)
            add_log_entry(user_id, label)
            return result
        return wrapped_f
    return decorator


def enable_history_tracking(ignore_missing_fn=False):
    """Enable history tracking globally.
    """
    cursor = connection.cursor()
    if ignore_missing_fn:
        cursor.execute("""
            SELECT EXISTS(SELECT 1 FROM pg_class
            WHERE relname='catmaid_history_table');""")
        result = cursor.fetchone()
        if not result[0]:
            # If the function does not exist, return silently if the missing
            # function shouldn't be reported
            return False
    cursor.execute("SELECT enable_history_tracking()")
    return True


def disable_history_tracking(ignore_missing_fn=False):
    """Disable history tracking globally.
    """
    cursor = connection.cursor()
    if ignore_missing_fn:
        cursor.execute("""
            SELECT EXISTS(SELECT * FROM pg_proc
            WHERE proname = 'disable_history_tracking');""")
        result = cursor.fetchone()
        if not result[0]:
            # If the function does not exist, return silently if the missing
            # function shouldn't be reported
            return False
    cursor.execute("SELECT disable_history_tracking()")
    return True