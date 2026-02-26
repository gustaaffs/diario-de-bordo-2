from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from livro_monitoramento import auth_views as custom_auth  # login/logout customizados

urlpatterns = [

    # =========================
    # AUTH PERSONALIZADO
    # =========================
    path("", custom_auth.login_page, name="login_page"),
    path("logout/", custom_auth.logout_page, name="logout_page"),

    # =========================
    # TROCA DE SENHA (SEM EMAIL)
    # =========================
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="auth/password_change_form.html",
            success_url="/password-change/done/",
        ),
        name="password_change",
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="auth/password_change_done.html",
        ),
        name="password_change_done",
    ),

    # =========================
    # RESET POR EMAIL (FUTURO)
    # =========================
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset_form.html",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # =========================
    # APP LIVRO
    # =========================
    path("livro/", include("livro_monitoramento.urls")),

    # =========================
    # ADMIN
    # =========================
    path("admin/", admin.site.urls),
]