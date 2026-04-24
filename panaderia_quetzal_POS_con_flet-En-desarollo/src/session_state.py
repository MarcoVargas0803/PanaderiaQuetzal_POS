class SessionState:
    current_user = None
    current_password = None
    current_role = None
    current_user_id = None
    current_caja_id = None
    temp_carrito = {}
    temp_total = 0.0

    @classmethod
    def reset(cls):
        cls.current_user = None
        cls.current_password = None
        cls.current_role = None
        cls.current_user_id = None
        cls.current_caja_id = None

def get_session():
    return SessionState
