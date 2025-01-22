from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from user.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from movie.models import Booking
from .models import Account

@login_required
def index(request):
    return render(request, 'user/index.html', {'form': form, 'title': 'index'})

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # Send email
            try:
                htmly = get_template('user/Email.html')
                d = {'username': username}
                subject, from_email, to = 'Welcome', 'your_email@gmail.com', email
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                messages.success(request, "Your account has been created! Please check your email.")
            except Exception as e:
                messages.warning(request, f"Account created, but email not sent: {e}")

            return redirect('login')
        else:
            messages.error(request, "Form submission failed. Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'user/register.html', {'form': form, 'title': 'Register Here'})

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username = username, password = password)
		if user is not None:
			#form = login(request, user)
			messages.success(request, f' welcome {username} !!')
			return redirect('home')
		else:
			messages.info(request, f'Account does not exist! Please enter correct credentials.')
	form = AccountAuthenticationForm()
	return render(request, 'user/login.html', {'form':form, 'title':'log in'})


@login_required
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect("login")
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST or None, request.FILES, instance=request.user)
        if form.is_valid():
            form.initial = {
                "email": request.POST['email'],
                "username": request.POST['username'],
                "first_name": request.POST['first_name'],
                "last_name": request.POST['last_name'],
                "age": request.POST['age'],
                "gender": request.POST['gender'],
                "phone_no": request.POST['phone_no'],
                "address": request.POST['address'],
                "photo": request.FILES['photo']
            }
            form.save()
        return redirect('home')
    else:
        form = AccountUpdateForm(
            initial={
                "email": request.user.email,
                "username": request.user.username,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "age": request.user.age,
                "gender": request.user.gender,
                "phone_no": request.user.phone_no,
                "address": request.user.address,
                "photo": request.user.photo
            }
        )
    context['form'] = form
    return render(request, "user/editprofile.html", context)

class change_password(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your password has been changed.")
        return super(PasswordChangeView, self).form_valid(form)

@login_required
def dashboard(request):
    User = Account.objects.get(username=request.user.username)
    tickets = Booking.objects.filter(user=User.pk)
    return render(request, 'user/dashboard.html', {'tickets': tickets})
