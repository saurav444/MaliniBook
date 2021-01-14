from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, CreateView, FormView, DetailView, ListView
from django.http import Http404, request
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .forms import CheckoutForm, CustomerRegistrationForm, CustomerLoginForm, PasswordForgotForm, ContactForm
from django.urls import reverse_lazy, reverse
import razorpay
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from .models import *


class EcoMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcoMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = Product.objects.all()
        paginator = Paginator(all_products, 6)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context


class AboutView(EcoMixin, TemplateView):
    template_name = 'about.html'


class CheckoutView(EcoMixin, CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "online payment":
                return redirect(reverse('payment') + "?o_id=" + str(order.id))
        else:
            return redirect('home')
        return super().form_valid(form)


class PaymentView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get('o_id')
        order = Order.objects.get(id=o_id)
        context = {
            "order": order
        }
        return render(request, 'payment.html', context)

    def payment(request):
        if request.method == 'POST':
            amount = int(request.POST.get("amount")) * 100
            client = razorpay.Client(auth=('rzp_test_JhHuFn4eOGnneG', 'IRt75C7X876p4tpBOu3e3SHK'))
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
        print(amount)
        return render(request, 'payment.html', {'payment': payment})


class ScienceView(TemplateView):
    template_name = 'science.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.filter(pk=1)
        return context


class ArtsView(TemplateView):
    template_name = 'science.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.filter(pk=2)
        return context


class CommerceView(TemplateView):
    template_name = 'commerce.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.filter(pk=3)
        return context


class GovtView(TemplateView):
    template_name = 'govt.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.filter(pk=4)
        return context


class ReligiousView(TemplateView):
    template_name = 'religious.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.filter(pk=5)
        return context


class StoryView(TemplateView):
    template_name = 'story.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.filter(pk=6)
        return context


class AddToCartView(EcoMixin, TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)
        # check if cart exists
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            try:
                cart_obj = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                raise Http404
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            # item allready exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1,
                    subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1,
                subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()
        return context


class MyCartView(EcoMixin, TemplateView):
    template_name = 'my_cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)

        if cart_id:
            cart = Cart.objects.get(id=cart_id)

        else:
            cart = None
        context['cart'] = cart
        return context


class ProductDetailView(TemplateView):
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        context['product'] = product
        return context


class ManagerCartView(EcoMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("my_cart")


class CustomerRegistrationView(CreateView):
    template_name = 'register.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user = User.objects.create_user(username, email, password)
            form.instance.user = user
            login(self.request, user)
            return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")


class CustomerLoginView(FormView):
    template_name = 'login.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy('home')

    # form_valid metod is a type of post method and is available in createView,FormView and UpdateView
    def form_valid(self, form):
        uname = form.cleaned_data["username"]
        psw = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=psw)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class PasswordForgotView(FormView):
    template_name = 'passwordforgot.html'
    form_class = PasswordForgotForm
    success_url = 'forgot-password'

    def form_valid(self,form):
        email = form.cleaned_data.get('email')
        return super().form_valid(form)


class CustomerProfileView(TemplateView):
    template_name = 'profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer)
        context['orders'] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = 'customerorderdetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET['keyword']
        results = Product.objects.filter(Q(title__icontains=kw) | Q(description__icontains=kw))
        context['results'] = results
        return context


# Admin pages


class AdminLoginView(FormView):
    template_name = 'adminlogin.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy('adminhome')

    def form_valid(self, form):
        uname = form.cleaned_data["username"]
        psw = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=psw)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        return super().form_valid(form)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login-login/")
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = 'adminhome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['po'] = Order.objects.filter(order_status="Order Received")
        return context


class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = 'adminorderdetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = ORDER_STATUS
        return context


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = 'adminorderlist.html'
    queryset = Order.objects.all().order_by('-id')
    context_object_name = 'allorders'


class AdminOrderStatusView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy('adminorderdetail', kwargs={'pk': order_id}))
