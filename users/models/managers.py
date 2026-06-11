from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
            self,
            email,
            name,
            surname,
            phone,
            password=None,
            **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not name:
            raise ValueError("Name is required")
        if not surname:
            raise ValueError("Surname is required")
        if not phone:
            raise ValueError("Phone is required")

        normalized_email = self.normalize_email(email)
        user = self.model(
            email=normalized_email,
            name=name,
            surname=surname,
            phone=phone,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, name, surname, phone, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields["is_staff"] is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email,
            name,
            surname,
            phone,
            password,
            **extra_fields)
