from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

def login_page(request):
    if request.user.is_authenticated:
        return redirect("livro:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("livro:home")
        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "livro_monitoramento/login.html")


def logout_page(request):
    logout(request)
    return redirect("login_page")
