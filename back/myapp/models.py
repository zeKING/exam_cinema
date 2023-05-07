from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

from rest_framework.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size
    if filesize > 10485760:
        raise ValidationError("You cannot upload file more than 10Mb")
    return value


def validate_uzb_phone(value):
    if len(value) != 13:
        raise ValidationError('Error')
    if value[:4] != '+998':
        raise ValidationError('Error')
    return value


class Role(models.Model):
    name = models.CharField("Role", max_length=64)
    name_en = models.CharField("Role_en", max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, name=None, role_id=None, phone=None, photo=None):

        if not email:
            raise ValueError('The email is required to create this user')
        email = CustomUserManager.normalize_email(email)
        if photo:
            cuser = self.model(email=email, phone=phone, role_id=role_id, photo=photo, name=name, is_staff=False,
                               is_active=True, is_superuser=False)
        else:
            cuser = self.model(email=email, phone=phone, role_id=role_id, name=name, is_staff=False,
                               is_active=True, is_superuser=False,)
        cuser.set_password(password)
        cuser.save(using=self._db)
        return cuser

    def create_superuser(self, email, name, role_id, phone, password=None):
        u = self.create_user(email=email, name=name, role_id=role_id, phone=phone, password=password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


with open('myapp/cinema_person_base64.txt', 'r') as f:
    photo_base64 = f.read()


class User(AbstractUser):
    name = models.CharField("Name", max_length=255)
    email = models.EmailField("Email", unique=True)
    password = models.CharField("Password", max_length=255)
    phone = models.CharField("Phone", max_length=19, validators=[validate_uzb_phone], unique=True)
    photo = models.TextField("Photo", default=photo_base64)
    created_at = models.DateTimeField('Created', auto_now_add=True)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    username = None
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'role_id', 'email']

    objects = CustomUserManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Genre(models.Model):
    name = models.CharField("Name", max_length=100)


class Movie(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description")
    age_limit = models.IntegerField("Age Limit", validators=[MinValueValidator(0)])
    genres = models.ManyToManyField(Genre)


class Hall(models.Model):
    name = models.CharField("Hall name", max_length=20)
    rows = models.IntegerField("Number of rows", validators=[MinValueValidator(0), ])
    seats = models.IntegerField("Number of seats", validators=[MinValueValidator(0), ])

    def __str__(self):
        return self.name


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
    hall = models.ForeignKey(Hall, on_delete=models.DO_NOTHING)
    time = models.DateTimeField()
    price = models.IntegerField(validators=[MinValueValidator(0), ])

    def __str__(self):
        return self.hall


class Ticket(models.Model):
    id = models.UUIDField("ID", primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    row = models.IntegerField("Row")
    seat = models.IntegerField("Seat")
    status = models.IntegerField("Status", )  # 0 - not available, 1 - free, 2 - sold
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.session.hall.name}, {self.row} ряд, {self.seat} место, статус {self.status}'

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ('session', )


class Feedback(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField("Created", auto_now_add=True)
    publish = models.BooleanField("Publish", default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.description[:30] + '...' if len(self.description) > 30 else self.description


class Support(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    description = models.TextField()
    created_at = models.DateTimeField("Created", auto_now_add=True)
    file = models.FileField("File", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=[
        'jpg', 'png', 'jpeg', 'jfif', 'docx', 'doc', 'pdf'])],
        upload_to="files/support")
    solved = models.BooleanField("Solved", default=False)

    class Meta:
        ordering = ('solved', '-created_at')

    def __str__(self):
        return self.description[:30] + '...' if len(self.description) > 30 else self.description

    def get_file_url(self):
        if self.file:
            return self.file.url
        else:
            return None


class News(models.Model):
    title = models.CharField("Title", max_length=100)
    description = models.TextField("Description")
    created_at = models.DateTimeField("Created", auto_now_add=True)
    photo = models.ImageField("Photo", upload_to='images/news',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg',
                                                                                     'jfif'])])

    class Meta:
        verbose_name = 'New'
        verbose_name_plural = 'News'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title
