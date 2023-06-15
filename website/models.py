import datetime
import time
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from project.current_user import get_current_user


class Accrual(models.Model):
    registration_date = models.DateTimeField("Дата регистрации", null=True, blank=True)
    """Дата регистрации"""
    begin_date = models.DateField("Начало периода", null=True, blank=True)
    """Начало"""
    end_date = models.DateField("Окончание периода", null=True, blank=True)
    """Окончание"""
    percent = models.FloatField("Процент", default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    """Процент"""
    completed = models.BooleanField("Обработано", null=True, blank=True)
    """Обработано"""

    def get_total(self):
        items = AccrualItem.objects.filter(accrual_id=self.id)
        return round(sum(item.value for item in items), 2)
    get_total.short_description = "Сумма, руб."
    get_total.allow_tags = True

    def create_accrual (self):
        users = User.objects.all()
        AccrualItem.objects.filter(accrual_id=self.id).delete()
        for user in users:
            # Если доктор, то добавляем в начисление
            if user.in_group_by_id(3):
                accrual_item = AccrualItem()
                accrual_item.accrual = self
                accrual_item.doctor = user
                count, value = user.get_stat_service(self.begin_date, self.end_date)
                accrual_item.value = round(value * self.percent / 100.0, 2)
                accrual_item.save()

    def __str__(self):
        return "Начисление #" + str(self.id) + " от " + self.registration_date.strftime("%d.%m.%Y")

    class Meta:
        verbose_name = "Начисление"
        verbose_name_plural = "Начисления"


@receiver(pre_save, sender=Accrual)
def accrual_pre_save(sender, instance, **kwargs):
    # if created:
    if instance.registration_date is None:
        instance.registration_date = datetime.datetime.now()
    # if instance.creator is None:
    #     instance.creator = get_current_user()
    if instance.completed is None:
        instance.completed = False


@receiver(post_save, sender=Accrual)
def accrual_post_save(sender, instance, created, **kwargs):
    instance.create_accrual()
    # if created:
    # else:


class AccrualItem(models.Model):
    accrual = models.ForeignKey("Accrual", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Начисление")
    """Начисление"""
    doctor = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Доктор")
    """Доктор"""
    value = models.FloatField("Начислено, руб.", null=True, blank=True)
    """Начислено"""

    def __str__(self):
        return "Начисление доктору #" + str(self.id)

    class Meta:
        verbose_name = "Начисление доктору"
        verbose_name_plural = "Начисление доктору"


class Request(models.Model):
    registration_date = models.DateTimeField("Дата регистрации", null=True, blank=True)
    """Дата регистрации"""
    patient = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пациент")
    """Пациент"""
    procedure = models.ForeignKey("Procedure", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Процедура")
    """Процедура"""
    begin_date = models.DateTimeField("Дата записи", null=True, blank=True)
    """Дата"""
    description = models.TextField("Примечание", null=True, blank=True)
    """Примечание"""
    completed = models.BooleanField("Обработано", null=True, blank=True)
    """Обработано"""

    def __str__(self):
        return "Заявка #" + str(self.id) + " от " + self.registration_date.strftime("%d.%m.%Y")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


@receiver(pre_save, sender=Request)
def request_pre_save(sender, instance, **kwargs):
    # if created:
    if instance.registration_date is None:
        instance.registration_date = datetime.datetime.now()
    if instance.patient is None:
        instance.patient = get_current_user()
    if instance.completed is None:
        instance.completed = False


class Procedure(models.Model):
    """Процедура"""
    title = models.CharField("Название", max_length=255)
    """Название"""
    description = models.TextField("Описание", null=True, blank=True)
    """Описание"""
    image = models.ImageField("Изображение", null=True, blank=True)
    """Изображение"""
    cost = models.FloatField("Стоимость", null=True, blank=True)
    """Стоимость"""
    duration = models.IntegerField("Продолжительность, мин.", null=True, blank=True)
    """Продолжительность (минут)"""
    public = models.BooleanField("Публиковать", null=True, blank=True)
    """Публиковать товар"""

    def image_img(self):
        """Изображение, для отображения в админке"""
        if self.image:
            from django.utils.safestring import mark_safe
            return mark_safe(u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.format(self.image.url))
        else:
            return '(Нет изображения)'
    image_img.short_description = 'Изображение'
    image_img.allow_tags = True

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Процедура"
        verbose_name_plural = "Процедуры"


class ReceptionStatus(models.Model):
    """Статус приема"""
    title = models.CharField("Название", "title", max_length=255)
    """Название"""

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статус приема"
        verbose_name_plural = "Статусы приема"


class Reception(models.Model):
    """Прием"""
    registration_date = models.DateTimeField("Дата регистрации", null=True, blank=True)
    """Дата регистрации"""
    begin_date = models.DateTimeField("Начало", null=True, blank=True)
    """Начало"""
    patient = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пациент", related_name="patient")
    """Пациент"""
    doctor = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Доктор", related_name="doctor")
    """Доктор"""
    description = models.TextField("Описание", null=True, blank=True)
    """Описание"""
    product_movement = models.ForeignKey("ProductMovement", on_delete=models.SET_NULL, null=True, blank=True,
                                         verbose_name="Движение товара")
    """Движение товара"""
    # on_delete=models.SET_NULL, null=True, blank=True,
    reception_status = models.ForeignKey("ReceptionStatus", on_delete=models.RESTRICT, verbose_name="Статус", default=1)
    """Статус приема"""

    def __str__(self):
        # return self.registration_date is not None if self.registration_date.__str__() else ""
        return "Прием #" + self.id.__str__()

    def get_total_duration(self):
        """Метод вычисления продолжительности приема"""
        items = ReceptionProcedure.objects.filter(reception_id=self.id)
        value = sum(item.procedure.duration if item.procedure is not None else 0 for item in items)
        return value
    get_total_duration.short_description = "Длительность, мин."
    get_total_duration.allow_tags = True

    def get_procedures_total_cost(self):
        reception_procedures = ReceptionProcedure.objects.filter(reception_id=self.id)
        value = float(sum(item.cost * item.count if item is not None else 0.0 for item in reception_procedures))
        return round(value, 2)
    get_procedures_total_cost.short_description = "Стоимость процедур, руб."
    get_procedures_total_cost.allow_tags = True

    def get_products_total_cost(self):
        reception_products = ReceptionProduct.objects.filter(reception_id=self.id)
        value = float(sum(item.cost * item.count if item is not None else 0.0 for item in reception_products))
        return round(value, 2)
    get_products_total_cost.short_description = "Стоимость товаров, руб."
    get_products_total_cost.allow_tags = True

    def get_total_cost(self):
        value = self.get_procedures_total_cost() + self.get_products_total_cost()
        return round(value, 2)
    get_total_cost.short_description = "Сумма, руб."
    get_total_cost.allow_tags = True

    def get_end_date(self):
        if self.begin_date is not None:
            total_minutes = self.get_total_duration()
            timetuple = (self.begin_date + datetime.timedelta(minutes=total_minutes)).astimezone().timetuple()
            unix_time = int(time.mktime(timetuple))
            return datetime.datetime.fromtimestamp(unix_time)
        return None
    get_end_date.short_description = "Окончание"
    get_end_date.allow_tags = True

    def product_movement_create(self):
        if self.product_movement is None and self.reception_status.id != 3:
            product_movement = ProductMovement()
            product_movement.registration_date = datetime.datetime.now()
            product_movement.movement_type = ProductMovementType.objects.get(id=2)
            user = self.doctor
            if user is None:
                user = get_current_user()
            product_movement.creator = user
            product_movement.save()
            self.product_movement = product_movement
            self.save()

    def product_movement_create_items(self):
        if self.product_movement is not None and self.reception_status.id != 3:
            reception_products = ReceptionProduct.objects.filter(reception_id=self.id)
            ProductMovementItem.objects.filter(product_movement_id=self.product_movement.id).delete()
            for reception_product in reception_products:
                product_movement_item = ProductMovementItem()
                product_movement_item.product_movement = self.product_movement
                product_movement_item.product = reception_product.product
                product_movement_item.cost = reception_product.product.cost
                product_movement_item.count = reception_product.count
                product_movement_item.save()

    def product_movement_update_status (self):
        if self.reception_status is not None and self.product_movement is not None:
            if self.reception_status.id == 3:
                self.product_movement.composed = True
                self.product_movement.completed = True
                self.product_movement.save()
            else:
                self.product_movement.composed = False
                self.product_movement.completed = False
                self.product_movement.save()

    class Meta:
        verbose_name = "Прием"
        verbose_name_plural = "Приемы"


@receiver(post_save, sender=Reception)
def reception_post_save(sender, instance, created, **kwargs):
    instance.product_movement_create()
    instance.product_movement_create_items()
    instance.product_movement_update_status()
    # if created:
    # else:


class ReceptionProcedure(models.Model):
    """Процедуры приема"""
    reception = models.ForeignKey("Reception", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Прием")
    """Прием"""
    procedure = models.ForeignKey("Procedure", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Процедура")
    """Процедура"""
    cost = models.DecimalField("Стоимость, руб.", max_digits=10, decimal_places=2, default=0)
    """Стоимость"""
    count = models.IntegerField("Количество", "count", validators=[MinValueValidator(1)], default=1)
    """Количество"""

    def get_total_cost(self):
        return round(self.cost * self.count, 2)
    get_total_cost.short_description = "Сумма, руб."
    get_total_cost.allow_tags = True

    def __str__(self):
        if self.procedure is not None:
            return self.procedure.title
        return None

    class Meta:
        verbose_name = "Процедуры приема"
        verbose_name_plural = "Процедуры приема"


@receiver(post_save, sender=ReceptionProcedure)
def reception_procedure_post_save(sender, instance, created, **kwargs):
    if instance.procedure is not None:
        if instance.cost != instance.procedure.cost:
            instance.cost = instance.procedure.cost
            instance.save()
    # if created:
    # else:

class ReceptionProduct(models.Model):
    """Процедуры приема"""
    reception = models.ForeignKey("Reception", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Прием")
    """Прием"""
    product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Товар")
    """Товар"""
    cost = models.DecimalField("Стоимость, руб.", max_digits=10, decimal_places=2, default=0)
    """Стоимость"""
    count = models.IntegerField("Количество", "count", validators=[MinValueValidator(1)], default=1)
    """Количество"""

    def get_total_cost(self):
        return round(self.cost * self.count, 2)
    get_total_cost.short_description = "Сумма, руб."
    get_total_cost.allow_tags = True

    def __str__(self):
        if self.product is not None:
            return self.product.title
        return None

    class Meta:
        verbose_name = "Компоненты приема"
        verbose_name_plural = "Компоненты приема"


@receiver(post_save, sender=ReceptionProduct)
def reception_product_post_save(sender, instance, created, **kwargs):
    if instance.product is not None:
        if instance.cost != instance.product.cost:
            instance.cost = instance.product.cost
            instance.save()

        if instance.reception is not None:
            instance.reception.product_movement_create_items();

    # if created:
    # else:


class Gender(models.Model):
    """Пол"""
    title = models.CharField("Название", max_length=255)
    """Название"""

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пол"
        verbose_name_plural = "Пол"


class UserType(models.Model):
    """Тип пользователя"""
    title = models.CharField("Название", max_length=255)
    """Название класса"""

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип пользователя"
        verbose_name_plural = "Типы пользователей"


class User(AbstractUser):
    """Пользователь"""
    db_table = 'auth_user'

    middle_name = models.CharField("Отчество", "middle_name", max_length=50, null=True, blank=True)
    """Отчество"""
    gender = models.ForeignKey('Gender', on_delete=models.SET_NULL, verbose_name="Пол",
                                  null=True, blank=True)
    """Тип пользователя"""
    birthday = models.DateField("Дата рождения", "birthday", null=True, blank=True)
    """Дата рождения"""
    description = models.TextField("Примечание", "description", null=True, blank=True)
    """Примечание"""
    phone = models.CharField("Телефон", "phone", max_length=255, null=True, blank=True)
    """Номер телефона заявителя"""
    address = models.CharField("Адрес", "address", max_length=255, null=True, blank=True)
    """Адрес"""
    user_type = models.ForeignKey('UserType', on_delete=models.SET_NULL, verbose_name="Тип пользователя",
                                  null=True, blank=True)
    """Тип пользователя"""

    report_date_1 = models.DateField("Начало периода", "report_date_1", null=True, blank=True)
    """Начало периода"""
    report_date_2 = models.DateField("Окончание периода", "report_date_2", null=True, blank=True)
    """"Окончание периода"""

    def get_stat_sale(self, report_date_1, report_date_2):
        """Метод вычисления статистики продаж"""
        items = ProductMovementItem.objects.filter(
                                                   product_movement__movement_type=2,
                                                   product_movement__creator=self.id,
                                                   product_movement__registration_date__range=[user.report_date_1,
                                                                                               user.report_date_2],
                                                   product_movement__completed=True,
                                                   product_movement__composed=True,
                                                   )
        return sum(item.count for item in items), sum(item.count * item.cost for item in items)

    def get_stat_service(self, report_date_1, report_date_2):
        """Метод вычисления статистики услуг"""
        items = Reception.objects.filter(doctor_id=self.id,
                                         reception_status_id=3,
                                         begin_date__range=[report_date_1, report_date_2],
                                         )
        return sum(1 for item in items), sum(item.get_procedures_total_cost() for item in items)

    def __str__(self):
        if self.last_name is not None and self.first_name is not None and self.middle_name is not None:
            return self.last_name + " " + self.first_name[0] + ". " + self.middle_name[0] + "."
        return self.username

    def groups_str(self):
        result = None
        for item in self.groups.all():
            if result is not None:
                result += ", "
            else:
                result = ""
            result += item.name
        return result

    groups_str.short_description = "Группы"
    groups_str.allow_tags = True

    def in_group_by_title (self, group_title):
        return self.groups.filter(name=group_title).exists()

    def in_group_by_id (self, group_id):
        return self.groups.filter(id=group_id).exists()

    def is_client (self):
        return self.in_group_by_id(4)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Category(models.Model):
    """Группа товаров"""
    title = models.CharField("Название", max_length=255)
    """Название группы товаров"""
    description = models.TextField("Описание", null=True, blank=True)
    """Описание группы товаров"""

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа товаров"
        verbose_name_plural = "Группы товаров"


class Unit(models.Model):
    """Единица измерения товара"""
    title = models.CharField("Название", max_length=255)
    """Название единицы измерения"""
    description = models.TextField("Описание", null=True, blank=True)
    """Описание единицы измерения"""

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"


class Brand(models.Model):
    """Бренд товаров"""
    title = models.CharField("Название", max_length=255)
    """Название"""
    description = models.TextField("Описание", null=True, blank=True)
    """Описание"""

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"


class Product(models.Model):
    """Товар"""
    title = models.CharField("Название", max_length=255)
    """Название товара"""
    description = models.TextField("Описание", null=True, blank=True)
    """Описание товара"""
    image = models.ImageField("Изображение", null=True, blank=True)
    """Изображение товара"""
    cost = models.FloatField("Цена за ед., руб.", null=True, blank=True)
    """Стоимость товара"""
    # amount = models.FloatField("Количество на складе", null=True, blank=True)
    # """Стоимость товара"""
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, verbose_name="Категория товаров",
                                 null=True, blank=True)
    """Группа товаров"""
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, verbose_name="Бренд",
                                 null=True, blank=True)
    """Бренд"""
    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, verbose_name="Единицы измерения товаров",
                             null=True, blank=True)
    """Единица измерения товара"""
    public = models.BooleanField("Публиковать", null=True, blank=True)
    """Публиковать товар"""
    production_date = models.DateField("Дата выработки", null=True, blank=True)
    """Дата выработки"""
    expiration_date = models.DateField("Срок годности", null=True, blank=True)
    """Срок годности"""

    def __str__(self):
        """Тайтл для товара"""
        return self.title
        # + " (" + str(self.cost) + " руб., ед.: " + self.unit.title + ")"

    def get_total_count(self):
        """Метод вычисления количества товара, которое есть на складе"""
        items = ProductMovementItem.objects.filter(product_id=self.id)
        # and item.product_movement.completed == True
        return round(sum(item.count * (1 if (item.product_movement.movement_type.id == 1) else -1) for item in items),
                     2)

    get_total_count.short_description = "На складе"
    get_total_count.allow_tags = True

    def get_stat_sale(self, user):
        """Метод вычисления статистики продаж"""
        items = ProductMovementItem.objects.filter(product_id=self.id,
                                                   product_movement__movement_type=2,
                                                   product_movement__registration_date__range=[user.report_date_1,
                                                                                               user.report_date_2],
                                                   product_movement__completed=True,
                                                   product_movement__composed=True,
                                                   )
        return sum(item.count for item in items), sum(item.count * item.cost for item in items)

    def image_img(self):
        """Изображение товара, для отображения в админке"""
        if self.image:
            from django.utils.safestring import mark_safe
            return mark_safe(u'<a href="{0}" target="_blank"><img src="{0}" width="100"/></a>'.format(self.image.url))
        else:
            return '(Нет изображения)'

    image_img.short_description = 'Изображение'
    image_img.allow_tags = True

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class ProductMovementType(models.Model):
    """Тип движения товара"""
    title = models.CharField("Название", max_length=255)
    """Название"""

    def __str__(self):
        return self.title.__str__();

    class Meta:
        verbose_name = "Тип движение товара"
        verbose_name_plural = "Типы движения товара"


class ProductMovementItem(models.Model):
    """Состав корзины (для движения товара)"""
    product_movement = models.ForeignKey('ProductMovement', on_delete=models.CASCADE, verbose_name="Движение")
    """Движение товара"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    """Товар"""
    cost = models.DecimalField("Стоимость", max_digits=10, decimal_places=2, default=0)
    """Стоимость"""
    count = models.IntegerField("Количество", "count", validators=[MinValueValidator(1)])
    """Количество"""

    def get_total_cost(self):
        """Метод вычисления общей стоимости товара"""
        return round(self.cost * self.count, 2)

    get_total_cost.short_description = "Общая стоимость"
    get_total_cost.allow_tags = True

    def __str__(self):
        return self.product.__str__();

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        model = super(ProductMovementItem, self).save(force_insert, force_update, using, update_fields)
        return model

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"


class ProductMovement(models.Model):
    """Движение товара"""
    registration_date = models.DateTimeField("Дата регистрации", "registration_date")
    """Дата регистрации"""
    creator = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Автор")
    """Создатель"""
    movement_type = models.ForeignKey("ProductMovementType", on_delete=models.PROTECT, null=True, blank=True,
                                      verbose_name="Тип движения")
    """Тип движения товара (приход или продажа)"""
    composed = models.BooleanField("Составлено", "composed", default=False)
    """Флаг 'Составлено'"""
    completed = models.BooleanField("Выполнено", "completed", default=False)
    """Флаг 'Выполнено'"""

    def __str__(self):
        return self.registration_date.__str__();

    def get_total_cost(self):
        """Метод расчета общей стоимости заказа"""
        items = ProductMovementItem.objects.filter(product_movement_id=self.id)
        return round(sum(item.get_total_cost() for item in items), 2)

    get_total_cost.short_description = "Общая стоимость"
    get_total_cost.allow_tags = True

    class Meta:
        verbose_name = "Движение товара"
        verbose_name_plural = "Движения товаров"
