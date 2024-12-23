from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Book

@receiver(post_save, sender=Book)
def increment_total_copies(sender, instance, created, **kwargs):
    """
    Increment total_copies in ParentBook when a new Book is created.
    """
    if created:  # Only increment if a new Book instance is created
        instance.parent_book.total_copies += 1
        instance.parent_book.available_copies += 1
        instance.parent_book.save()

@receiver(post_delete, sender=Book)
def decrement_total_copies(sender, instance, **kwargs):
    """
    Decrement total_copies in ParentBook when a Book is deleted.
    """
    instance.parent_book.total_copies -= 1
    instance.parent_book.available_copies -= 1
    instance.parent_book.save()
