# core/signals.py
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from .models import PropertyZone, OwnerStaff, CustomUser, Subscription, Plan


def get_active_subscription(user):
    """Helper to fetch the latest active subscription for a user."""
    sub = (
        Subscription.objects.filter(user_id=user, status="active")
        .order_by("-end_date")
        .first()
    )
    if not sub:
        return None, None

    # Fetch plan by name (Plan.name is unique)
    try:
        plan = Plan.objects.get(name=sub.plan_name)
    except Plan.DoesNotExist:
        return sub, None

    return sub, plan


@receiver(pre_save, sender=PropertyZone)
def enforce_max_locations(sender, instance, **kwargs):
    if instance.pk:  # Skip updates
        return

    owner = instance.owner_id
    subscription, plan = get_active_subscription(owner)
    if not subscription or not plan:
        raise ValidationError("No active subscription or plan found")

    max_locations = plan.max_locations
    current_locations = PropertyZone.objects.filter(owner_id=owner).count()

    if current_locations >= max_locations:
        raise ValidationError(
            f"Plan limit reached: Max {max_locations} locations allowed."
        )


@receiver(pre_save, sender=OwnerStaff)
def enforce_max_staff(sender, instance, **kwargs):
    if instance.pk:  # Skip updates
        return

    owner = instance.owner
    subscription, plan = get_active_subscription(owner)
    if not subscription or not plan:
        raise ValidationError("No active subscription or plan found")

    max_staff = plan.max_staff
    current_staff = OwnerStaff.objects.filter(owner=owner).count()

    if max_staff is not None and current_staff >= max_staff:
        raise ValidationError(
            f"Plan limit reached: Max {max_staff} staff allowed."
        )
    


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from pms.models import Rent, RentCycle,Payment
from pms.api.rent_cycle import generate_cycles_for_rent
from pms.api.rent import RENT_ACTIVE

@receiver(post_save, sender=Rent)
def handle_rent_save(sender, instance, created, **kwargs):
    today = timezone.now().date()

    if instance.status.lower() != RENT_ACTIVE:
        return

    if created:
        generate_cycles_for_rent(instance)
    else:
        if RentCycle.objects.filter(
            rent=instance,
            is_paid=False
        ).first().payment:
            payment = Payment.objects.filter(id=RentCycle.objects.filter(rent=instance,is_paid=False)
                                             .first().payment.pk)
            payment.delete()

        # Keep paid and past cycles, delete only unpaid + future ones
        RentCycle.objects.filter(
            rent=instance,
            is_paid=False
        ).delete()
        
        


        last_cycle = RentCycle.objects.filter(rent=instance).order_by('-cycle_end').first()
        new_start = last_cycle.cycle_end if last_cycle else instance.start_date.date()
        generate_cycles_for_rent(instance, start_date=new_start)




# Example placeholder for KDS (if/when you have a KDS model)
# @receiver(pre_save, sender=KDSModel)
# def enforce_max_kds(sender, instance, **kwargs):
#     if instance.pk:  # Skip updates
#         return
#
#     owner = instance.owner
#     subscription, plan = get_active_subscription(owner)
#     if not subscription or not plan:
#         raise ValidationError("No active subscription or plan found")
#
#     max_kds = plan.max_kds
#     current_kds = KDSModel.objects.filter(owner=owner).count()
#
#     if current_kds >= max_kds:
#         raise ValidationError(f"Plan limit reached: Max {max_kds} KDS allowed")
