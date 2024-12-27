from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book_Borrow

@receiver(post_save, sender=Book_Borrow)
def update_available_copies(sender, instance, created, **kwargs):
    if created:  # Only update when a new Book_Borrow object is created
        book = instance.book
        if book.available_copies > 0:
            book.available_copies -= 1  # Reduce available copies by 1
            book.save()
