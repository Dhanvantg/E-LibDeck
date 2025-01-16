from django.contrib import admin
from .models import Librarian

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('user', 'psrn')
    search_fields = ('user__username', 'psrn')