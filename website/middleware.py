from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings

class SessionSecurityMiddleware:
    """Middleware para expirar sesiones inactivas y proteger contra session hijacking."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_time = timezone.datetime.fromisoformat(last_activity)
                idle_seconds = (timezone.now() - last_time).total_seconds()
                if idle_seconds > 1800:
                    logout(request)
                    return redirect('website:login')
            request.session['last_activity'] = timezone.now().isoformat()
        
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        return response