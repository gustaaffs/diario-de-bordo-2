def dashboard_permission(request):
    if request.user.is_authenticated:
        pode = request.user.is_staff or request.user.groups.filter(name="dashboard").exists()
        return {"pode_ver_dashboard": pode}
    return {"pode_ver_dashboard": False}
