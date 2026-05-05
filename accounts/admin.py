from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# আপনার কাস্টম ইউজার মডেলটি অ্যাডমিন প্যানেলে রেজিস্টার করুন
class MyUserAdmin(UserAdmin):
    model = User
    # অ্যাডমিন প্যানেলে কোন কোন কলাম দেখাবে তা সেট করতে পারেন
    list_display = ['username', 'phone_number', 'email', 'is_staff', 'is_admin']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'is_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'is_admin')}),
    )

admin.site.register(User, MyUserAdmin)