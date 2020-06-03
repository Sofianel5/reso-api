from django.contrib.auth.models import BaseUserManager


class AccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password):
        if not email:
            raise ValueError("Users must have an email.")
        if not (first_name or last_name):
            raise ValueError("Users must have a full name.")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name.strip().capitalize(),
            last_name=last_name.strip().capitalize(),
        )
        user.first_name = user.first_name.strip().capitalize()
        user.last_name = user.last_name.strip().capitalize()
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.model(
            first_name=first_name.strip().capitalize(),
            last_name=last_name.strip().capitalize() + " (Admin)",
            email=email,
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
