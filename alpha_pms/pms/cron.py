from django.utils import timezone
from django.core.mail import send_mail
from .models import WorkSpaceRental


def check_due_rentals():
    today = timezone.now().date()
    due_rentals = WorkSpaceRental.objects.filter(
        due_date__lte=today,
        is_active=True
    )

    for rental in due_rentals:
        renter_name = rental.guest_name or (str(rental.user.first_name())+str(" ")+str(rental.user.last_name) if rental.user else "Customer")
        renter_email = rental.guest_email or (rental.user.email if rental.user else None)

        if renter_email:
            subject = "Workspace Rental Due"
            message = (
                f"Dear {renter_name},\n\n"
                f"Your rental for {rental.space.name} is due on {rental.due_date}. "
                f"Please renew your rental to continue using the workspace.\n\n"
                "Thank you."
            )
            send_mail(subject, message, None, [renter_email], fail_silently=True)
