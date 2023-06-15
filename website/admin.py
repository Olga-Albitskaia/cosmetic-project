from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext, gettext_lazy as _

import website

# Register your models here.
from website.models import *


class RefBookTitleDescriptionA(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ['title']


class RefBookTitleA(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = website.models.User
        fields = ('email', 'username')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = website.models.User
        fields = ('email', 'username')


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = website.models.User

    readonly_fields = ('groups_str',)
    list_display = ('username', 'last_name', 'first_name', 'middle_name', 'phone', 'groups_str', 'is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('last_name', 'first_name', 'middle_name', 'gender', 'birthday',  'email', 'phone', 'address', 'description', 'user_type')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'gender')
    search_fields = UserAdmin.search_fields


class CategoryA (admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ['title']


class UnitA (admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ['title']


class ProductA (admin.ModelAdmin):
    list_display = ('title', 'brand', 'image_img', 'cost', 'get_total_count', 'public')
    list_filter = ('category', 'brand', 'unit', 'public')
    search_fields = ('title', 'description')
    ordering = ['title', 'cost']
    readonly_fields = ('get_total_count', 'image_img',)
    fields = ('category', 'brand', 'title', 'unit', 'cost', 'get_total_count', 'public', 'image', 'image_img', 'description', 'production_date', 'expiration_date')


class ProductMovementItemInline(admin.TabularInline):
    model = ProductMovementItem
    fk_name = 'product_movement'
    # raw_id_fields = ['product', ]
    extra = 1
    # exclude = ('cost',)
    # readonly_fields = ('get_total_cost',)


class ProductMovementA (admin.ModelAdmin):
    list_display = ('registration_date', 'creator', 'movement_type', 'composed', 'completed', 'get_total_cost')
    list_filter = ('registration_date', 'creator', 'movement_type', 'composed', 'completed')
    readonly_fields = ('get_total_cost',)
    search_fields = ('registration_date', 'creator')
    ordering = ['registration_date', 'creator']
    raw_id_fields = ('creator',)
    date_hierarchy = 'registration_date'
    inlines = [ProductMovementItemInline]


class ReceptionProcedureInline(admin.TabularInline):
    model = ReceptionProcedure
    raw_id_fields = ['procedure', ]
    extra = 1
    # exclude = ('cost',)
    readonly_fields = ('cost', 'get_total_cost')


class ReceptionProductInline(admin.TabularInline):
    model = ReceptionProduct
    raw_id_fields = ['product', ]
    extra = 1
    # exclude = ('cost',)
    readonly_fields = ('cost', 'get_total_cost')


class ReceptionA (admin.ModelAdmin):
    save_as = True
    list_display = ('begin_date', 'doctor', 'patient', 'get_end_date', 'get_total_duration', 'get_total_cost', 'reception_status')
    list_filter = ('begin_date', 'reception_status')
    search_fields = ('description', )
    ordering = ['begin_date', 'doctor']
    raw_id_fields = ('doctor', 'patient')
    date_hierarchy = 'begin_date'
    inlines = [ReceptionProcedureInline, ReceptionProductInline]
    readonly_fields = ('get_end_date', 'get_total_duration', 'get_procedures_total_cost', 'get_products_total_cost', 'get_total_cost', 'registration_date')
    exclude = ('product_movement', )


class ProcedureA (admin.ModelAdmin):
    list_display = ('title', 'duration', 'cost', 'image_img', 'public')
    list_filter = ('public', )
    search_fields = ('title', 'description')
    ordering = ['title', 'cost']
    fields = ('title', 'description', 'image', 'image_img', 'cost', 'duration', 'public')
    readonly_fields = ('image_img', )


class RequestA (admin.ModelAdmin):
    list_display = ('registration_date', 'patient', 'procedure', 'completed')
    list_filter = ('completed', 'registration_date', 'procedure')
    search_fields = ('description', )
    ordering = ['registration_date', ]
    raw_id_fields = ('patient',)
    readonly_fields = ('registration_date', )


class AccrualItemInline(admin.TabularInline):
    can_delete = False
    model = AccrualItem
    extra = 1
    readonly_fields = ('doctor', 'value')


class AccrualA (admin.ModelAdmin):
    save_as = True
    list_display = ('registration_date', 'begin_date', 'end_date', 'percent', 'get_total', 'completed')
    list_filter = ('completed', 'percent', 'registration_date', 'begin_date', 'end_date')
    # search_fields = ('description', )
    ordering = ['registration_date']
    # raw_id_fields = ('doctor', 'patient')
    date_hierarchy = 'registration_date'
    inlines = [AccrualItemInline]
    readonly_fields = ('registration_date', 'get_total')
    # exclude = ('product_movement', )


admin.site.register(website.models.User, CustomUserAdmin)
admin.site.register(Product, ProductA)
admin.site.register(Category, CategoryA)
admin.site.register(Unit, UnitA)
admin.site.register(ProductMovement, ProductMovementA)
admin.site.register(ProductMovementType, RefBookTitleA)
admin.site.register(UserType, RefBookTitleA)
admin.site.register(Gender, RefBookTitleA)
admin.site.register(Brand, RefBookTitleDescriptionA)
admin.site.register(ReceptionStatus, RefBookTitleA)
admin.site.register(Reception, ReceptionA)
admin.site.register(Procedure, ProcedureA)
admin.site.register(Request, RequestA)
admin.site.register(Accrual, AccrualA)

admin.site.site_header = "Cosmetology"
