from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер для модели пользователей."""

    def create_user(
        self,
        username,
        email,
        first_name,
        last_name,
        password,
    ):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Users must have a username.')
        if email is None:
            raise TypeError('Users must have an email address.')
        if password is None:
            raise TypeError('Users must have a password.')
        if first_name is None:
            raise TypeError('Users must have a first_name.')
        if last_name is None:
            raise TypeError('Users must have a last_name.')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        email,
        first_name=None,
        last_name=None,
        password=None
    ):
        """Создает и возвращает пользователя с привилегиями суперадмина."""
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(
            username,
            email,
            first_name,
            last_name,
            password
        )
        user.is_staff = True
        user.save(using=self._db)

        return user
