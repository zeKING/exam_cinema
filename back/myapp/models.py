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


# class Genre(models.Model):
#     name = models.CharField("Name", max_length=100)
#
#     def __str__(self):
#         return self.name


class Movie(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description")
    duration = models.IntegerField("Duration(minutes)", validators=[MinValueValidator(0), ])
    age_limit = models.IntegerField("Age Limit", validators=[MinValueValidator(0), ])
    # genres = models.ManyToManyField(Genre)
    rating = models.FloatField("Rating", validators=[MinValueValidator(0), MaxValueValidator(5)], null=True,
                               blank=True, default=0)
    photo = models.ImageField("Photo", upload_to='images/movies',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg',
                                                                                     'jfif', 'webp', 'webm'])])

    def __str__(self):
        return self.name

    def get_feedback_count(self):
        return self.feedback_set.count()

    def get_feedbacks(self):
        return self.feedback_set.all()


class Hall(models.Model):
    name = models.CharField("Hall name", max_length=20)
    rows = models.IntegerField("Number of rows", validators=[MinValueValidator(0), ])
    seats = models.IntegerField("Number of seats", validators=[MinValueValidator(0), ])

    def __str__(self):
        return self.name


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, db_constraint=False)
    hall = models.ForeignKey(Hall, on_delete=models.DO_NOTHING)
    time = models.DateTimeField()
    price = models.IntegerField(validators=[MinValueValidator(0), ])

    def __str__(self):
        return f'{self.movie.name}, {self.hall.name}'


class Ticket(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    row = models.IntegerField("Row", validators=[MinValueValidator(1), ])
    seat = models.IntegerField("Seat", validators=[MinValueValidator(1), ])
    status = models.IntegerField("Status", default=0)  # 0 - free, 1 - prepare, 2 - sold, 3 - not available
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner', on_delete=models.DO_NOTHING, null=True,
                              blank=True)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='editor', on_delete=models.DO_NOTHING,
                               null=True, blank=True)
    # transaction = models.ForeignKey(ClickTransaction, on_delete=models.CASCADE)
    phone = models.CharField("Phone", max_length=19, validators=[validate_uzb_phone, ], null=True)
    tg_owner_id = models.IntegerField("Tg_user_id", null=True, blank=True)

    def __str__(self):
        return f'{self.session.movie.name}, {self.session.hall.name}, {self.created_at}, {self.row} ряд, {self.seat} ' \
               f'место, ' \
               f'статус {self.status}'

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
        'jpg', 'png', 'jpeg', 'jfif', 'docx', 'doc', 'pdf', 'webp', 'webm', 'rar', 'zip'])],
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
    title = models.CharField("Title", max_length=100, null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    created_at = models.DateTimeField("Created", auto_now_add=True)
    photo = models.ImageField("Photo", upload_to='images/news',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg',
                                                                                     'jfif', 'webp', 'webm'])])

    class Meta:
        verbose_name = 'New'
        verbose_name_plural = 'News'
        ordering = ('-created_at', )

    def __str__(self):
        return f'Новость номер {self.id}'
