from .forms import LoginForm, RegisterForm


def add_my_forms(request):
    return {
        'form': LoginForm(),
        'form2': RegisterForm()
    }





