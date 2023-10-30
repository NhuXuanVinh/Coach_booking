from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    user_phone = models.CharField(max_length=255)
    user_mail = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

class Nhanvienxe(models.Model):
    nhanvien_id = models.BigAutoField(primary_key=True)
    nhanvien_name = models.CharField(max_length=255)
    job = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    age = models.IntegerField()

class Xe(models.Model):
    bien_so = models.CharField(max_length=255, primary_key=True)
    last_maintain = models.DateField()
    production_date = models.DateField()
    row_number = models.IntegerField()
    column_number = models.IntegerField()
    xe_name = models.CharField(max_length=255)

class Chuyenxe(models.Model):
    chuyenxe_id = models.BigAutoField(primary_key=True)
    bien_so = models.ForeignKey(Xe, on_delete=models.CASCADE, db_column='bien_so')
    chuyenxe_date = models.DateField()
    arrive_time = models.TimeField()
    start_time = models.TimeField()
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    
class Ghe(models.Model):
    ghe_id = models.BigAutoField(primary_key=True)
    bien_so = models.ForeignKey(Xe, on_delete=models.CASCADE, db_column='bien_so')
    row = models.IntegerField()
    col = models.IntegerField()

class Ve(models.Model):
    ve_id = models.BigAutoField(primary_key=True)
    ghe_id = models.ForeignKey(Ghe, on_delete=models.CASCADE, db_column='ghe_id')
    chuyenxe_id = models.ForeignKey(Chuyenxe, on_delete=models.CASCADE, db_column='chuyenxe_id')
    status = models.BooleanField(default=False)

class Dieukhien(models.Model):
    chuyenxe_id = models.ForeignKey(Chuyenxe, on_delete=models.CASCADE, db_column='chuyenxe_id')
    nhanvien_id = models.ForeignKey(Nhanvienxe, on_delete=models.CASCADE, db_column='nhanvien_id')

class Datve(models.Model):
    ve_id = models.ForeignKey(Ve, on_delete=models.CASCADE, db_column='ve_id')
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    ve_time = models.DateTimeField(auto_now_add=True)

class Danhgia(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    chuyenxe_id = models.ForeignKey(Chuyenxe, on_delete=models.CASCADE, db_column='chuyenxe_id')
    comment = models.CharField(max_length=1000)
    rating = models.FloatField()
    
    
# Create your models here.
