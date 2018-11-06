class AuthError(Exception):
    def __init__(self):
        super().__init__(self)
        self.message = "User or password not match"

    def __str__(self):
        return self.message