import operator

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, DetailView
from django.views.generic.edit import FormView, UpdateView
from django_filters.views import FilterView

from website.access_control import *
from website.filters import *
from website.models import *
from website.forms import *


# **********************************************************************************************
# Корзина
# **********************************************************************************************
def get_basket_id(request):
    # request.session['product_movement_id'] = None

    if request.session.get('product_movement_id', False):
        if ProductMovement.objects.filter(id=request.session['product_movement_id']).exists():
            return request.session['product_movement_id']

    model = ProductMovement()
    model.registration_date = datetime.datetime.now()
    model.creator_id = request.user.id
    model.movement_type_id = 2
    model.complete = False
    model.save()

    request.session['product_movement_id'] = model.id
    return request.session['product_movement_id']


@login_required
def basket_product_add(request, pk_product):
    product = Product.objects.get(id=pk_product)
    product_movement_id = get_basket_id(request)
    model = ProductMovementItem.objects.filter(product_id=product.id, product_movement_id=product_movement_id).all()
    if len(model) == 0:
        model = ProductMovementItem()
        model.product_movement_id = product_movement_id
        model.product_id = product.id
        model.cost = product.cost
        model.count = 0
    else:
        model = model[0]
    model.count += 1
    model.save()
    return redirect(reverse('basket-list', kwargs={}))


@login_required
def basket_composed(request):
    product_movement_id = get_basket_id(request)
    if ProductMovementItem.objects.filter(product_movement_id=product_movement_id).count() == 0:
        messages.info(request, 'В корзине нет товаров', 'alert alert-info')
        return redirect(reverse('basket-list', kwargs={}))
    model = ProductMovement.objects.get(pk=product_movement_id)
    model.composed = True;
    model.save();
    request.session['product_movement_id'] = None
    messages.info(request, 'Заказ отправлен в обработку', 'alert alert-info')
    return redirect(reverse('catalog-list', kwargs={}))


class BasketListView(LoginRequiredMixin, ListView):
    title = 'Корзина'
    model = ProductMovementItem
    template_name = 'basket/list.html'
    paginate_by = 10

    def get_queryset(self):
        basket_id = get_basket_id(self.request);
        queryset = ProductMovementItem.objects.filter(product_movement_id=basket_id)
        return queryset


class BasketUpdateView(LoginRequiredMixin, UpdateView):
    title = 'Редактирование'
    model = ProductMovementItem
    fields = ['count']
    template_name = 'basket/update.html'

    # success_url = reverse_lazy('basket-list')

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("basket-list")


class BasketDeleteView(LoginRequiredMixin, DeleteView):
    title = 'Удаление'
    model = ProductMovementItem
    template_name = 'basket/delete.html'
    success_url = reverse_lazy('basket-list')


# **********************************************************************************************
# Сайт
# **********************************************************************************************
class HomePageView(TemplateView):
    title = 'Главная страница'
    template_name = 'site/home.html'


class AboutPageView(TemplateView):
    title = 'О системе'
    template_name = 'site/about.html'


# **********************************************************************************************
# Профиль пользователя
# **********************************************************************************************
class UserProfileDetailView(TemplateView, LoginRequiredMixin):
    title = 'Профиль'
    template_name = 'user_profile/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(*args, **kwargs)
        context['model'] = self.request.user
        return context


class UserProfileUpdateView(FormView, LoginRequiredMixin):
    title = 'Редактирование профиля'
    template_name = 'user_profile/update.html'
    form_class = UserProfileForm
    success_url = '/user_profile/'

    def get_form(self, form_class=None):
        return UserProfileForm(instance=self.request.user, **self.get_form_kwargs())

    # def form_valid(self, form):
    #     # form.instance.user = self.request.user
    #     form.save()
    #     return super(UserProfileUpdateView, self).form_valid(form)


# **********************************************************************************************
# Каталог товаров
# **********************************************************************************************
class CatalogListView(FilterView):
    title = 'Каталог товаров'
    model = Product
    template_name = 'catalog/list.html'
    paginate_by = 5
    filterset_class = CatalogFilter
    # context_object_name = 'vacancies'

    # def get_queryset(self):
    #     qs = self.model.objects.prefetch_related('photo_set')
    #     if self.kwargs.get('collec_slug'):
    #         qs = qs.filter(collection__slug=self.kwargs['collec_slug'])
    #     return qs

    def get_queryset(self):
        queryset = super().get_queryset().filter(public=True)
        # queryset = queryset.filter(public=True)
        # queryset = Vacancy.objects.filter(public=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.
        # context['filterset'] = self.filterset
        return context


class CatalogDetailView(DetailView):
    title = 'Просмотр'
    model = Product
    template_name = 'catalog/detail.html'


# **********************************************************************************************
# Каталог товаров
# **********************************************************************************************
class ProcedureListView (FilterView):
    title = 'Процедуры'
    model = Procedure
    template_name = 'procedure/list.html'
    paginate_by = 5
    filterset_class = ProcedureFilter
    # context_object_name = 'vacancies'

    # def get_queryset(self):
    #     qs = self.model.objects.prefetch_related('photo_set')
    #     if self.kwargs.get('collec_slug'):
    #         qs = qs.filter(collection__slug=self.kwargs['collec_slug'])
    #     return qs

    def get_queryset(self):
        queryset = super().get_queryset().filter(public=True)
        # queryset = queryset.filter(public=True)
        # queryset = Vacancy.objects.filter(public=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.
        # context['filterset'] = self.filterset
        return context


class ProcedureDetailView(DetailView):
    title = 'Просмотр'
    model = Procedure
    template_name = 'procedure/detail.html'


# **********************************************************************************************
# Отчеты
# **********************************************************************************************
class ReportSettingsDetailView(LoginRequiredMixin, UserPassesTestOrganizationOrAdmin,  TemplateView):
    title = 'Анализ'
    template_name = 'report/detail.html'
    login_url = '/login'
    # form = ReportSettingsForm

    def get_context_data(self, *args, **kwargs):
        context = super(ReportSettingsDetailView, self).get_context_data(*args, **kwargs)
        context['model'] = self.request.user
        return context


class ReportSettingsUpdateView(LoginRequiredMixin, UserPassesTestOrganizationOrAdmin, FormView):
    title = 'Редактирование параметров'
    template_name = 'report/update.html'
    form_class = ReportSettingsForm
    success_url = reverse_lazy('report-settings-detail')

    def get_form(self, form_class=None):
        return ReportSettingsForm(instance=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        # form.instance.user = self.request.user
        form.save()
        return super(ReportSettingsUpdateView, self).form_valid(form)


# class ReportSaleListView(LoginRequiredMixin, TemplateView):
#     title = 'Статистика продаж'
#     # model = Product
#     template_name = 'report/sale-list.html'
#     paginate_by = 10
#
#     def get_queryset(self):
#         # queryset = super().get_queryset()
#         queryset = models.Request.objects.filter(user_id=self.request.user.id)
#         return queryset

class ReportSaleListView(LoginRequiredMixin, UserPassesTestOrganizationOrAdmin, TemplateView):
    title = 'Статистика продаж'
    template_name = 'report/sale-list.html'
    login_url = '/login'

    def get_context_data(self, *args, **kwargs):
        context = super(ReportSaleListView, self).get_context_data(*args, **kwargs)

        result = []
        product_list = Product.objects.all()
        stat_sale_total = 0
        for product in product_list:
            total_count, total_sum = product.get_stat_sale(self.request.user)
            stat_sale_total += total_sum

        for product in product_list:
            # stat_sale = product.get_stat_sale(self.request.user)
            total_count, total_sum = product.get_stat_sale(self.request.user)
            if total_sum > 0:
                d = {'title': product.title,
                     'category': product.category,
                     # 'product_class': product.product_class.title,
                     'stat_count': total_count,
                     'stat_sale': total_sum,
                     'stat_sale_percent': round(100 * total_sum / stat_sale_total, 1),
                     }
                result.append(d)

        context['object_list'] = result
        context['stat_sale_total'] = stat_sale_total
        context['model'] = self.request.user

        return context


class ReportSaleListByUserView(LoginRequiredMixin, UserPassesTestOrganizationOrAdmin, TemplateView):
    title = 'Статистика продаж (по сотрудникам)'
    template_name = 'report/sale-list-by-user.html'
    login_url = '/login'

    def get_context_data(self, *args, **kwargs):
        context = super(ReportSaleListByUserView, self).get_context_data(*args, **kwargs)

        result = []
        user_list = []
        user_list_ = User.objects.all()
        for user in user_list_:
            if not user.in_group_by_id(4):
                user_list.append(user)

        stat_sale_total = 0
        for user in user_list:
            total_count, total_sum = user.get_stat_sale(self.request.user)
            stat_sale_total += total_sum

        for user in user_list:
            # stat_sale = product.get_stat_sale(self.request.user)
            total_count, total_sum = user.get_stat_sale(self.request.user)
            if total_sum > 0:
                d = {'title': user.__str__() + (" (" + user.groups_str() + ")" if user.groups_str() is not None else ""),
                     # 'product_class': product.product_class.title,
                     'stat_count': total_count,
                     'stat_sale': total_sum,
                     'stat_sale_percent': round(100 * total_sum / stat_sale_total, 1),
                     }
                result.append(d)

        context['object_list'] = result
        context['stat_sale_total'] = stat_sale_total
        context['model'] = self.request.user

        return context


class ReportServiceStatByUserView(LoginRequiredMixin, UserPassesTestOrganizationOrAdmin, TemplateView):
    title = 'Статистика оказания услуг (по сотрудникам)'
    template_name = 'report/service-stat-by-user.html'
    login_url = '/login'

    def get_context_data(self, *args, **kwargs):
        context = super(ReportServiceStatByUserView, self).get_context_data(*args, **kwargs)

        result = []
        user_list = []
        user_list_ = User.objects.all()
        for user in user_list_:
            if not user.in_group_by_id(4):
                user_list.append(user)

        stat_sale_total = 0
        for user in user_list:
            total_count, total_sum = user.get_stat_service(self.request.user)
            stat_sale_total += total_sum

        for user in user_list:
            # stat_sale = product.get_stat_sale(self.request.user)
            total_count, total_sum = user.get_stat_service(self.request.user)
            if total_sum > 0:
                d = {'title': user.__str__() + (" (" + user.groups_str() + ")" if user.groups_str() is not None else ""),
                     # 'product_class': product.product_class.title,
                     'stat_count': total_count,
                     'stat_sale': total_sum,
                     'stat_sale_user_percent': round(total_sum * 0.3, 2),
                     'stat_sale_percent': round(100 * total_sum / stat_sale_total, 1),
                     }
                result.append(d)

        context['object_list'] = result
        context['stat_sale_total'] = stat_sale_total
        context['stat_sale_total_user_percent'] = round(stat_sale_total * 0.3, 2)
        context['model'] = self.request.user

        return context

# **********************************************************************************************
# Заявки
# **********************************************************************************************

class RequestListView(LoginRequiredMixin, FilterView):
    title = 'Заявки'
    model = Request
    template_name = 'request/list.html'
    paginate_by = 10
    filterset_class = RequestFilter
    # context_object_name = 'communities'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(patient_id=self.request.user.id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RequestDetailView(DetailView):
    title = 'Просмотр'
    model = Request
    template_name = 'request/detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # if not RequestStat.objects.filter(document_id=obj.id, date=datetime.date.today()).exists():
        #     loader = Loader()
        #     loader.document_load(obj)
        #     loader.document_stat_load(obj)
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(RequestDetailView, self).get_context_data(*args, **kwargs)
        # object = context['object']
        # context['stat'] = RequestStat.objects.filter(document_id=object.id).all()
        return context


class RequestCreateView(LoginRequiredMixin, CreateView):
    title = 'Добавление'
    model = Request
    template_name = 'request/create.html'
    success_url = reverse_lazy('request-detail')
    fields = ['procedure', 'begin_date', 'description']

    def get_initial(self, *args, **kwargs):
        initial = super(RequestCreateView, self).get_initial(**kwargs)
        initial['procedure'] = self.kwargs["procedure_id"]
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.registration_date = datetime.datetime.now()
        obj = form.save()
        self.success_url = reverse("request-detail", kwargs={"pk": obj.id})
        return super(RequestCreateView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(RequestCreateView, self).get_context_data(*args, **kwargs)
        return context


class RequestUpdateView(LoginRequiredMixin, UpdateView):
    title = 'Редактирование'
    model = Request
    fields = ['description']
    template_name = 'request/update.html'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("request-detail", kwargs={"pk": pk})


class RequestDeleteView(LoginRequiredMixin, DeleteView):
    title = 'Удаление'
    model = Request
    template_name = 'request/delete.html'
    success_url = reverse_lazy('request-list')
