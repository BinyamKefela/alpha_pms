from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Report
from ..serializers import ReportSerializer
from pms.api.custom_pagination import CustomPagination
import datetime


class ReportListView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in Report._meta.fields]
    ordering_fields = [field.name for field in Report._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


class ReportRetrieveView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ReportUpdateView(generics.UpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ReportDestroyView(generics.DestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'
    
    def destroy(self, request, *args, **kwargs):
        report = self.get_object()
        if not report:
            return Response({"error":"report not found!"}, status=status.HTTP_404_NOT_FOUND)
        report.delete()
        #report.save()
        return Response({"message":"report deleted successfully!"},status=status.HTTP_200_OK)


class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()



# reports/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum
from ..models import Subscription

class SubscriptionReportView(APIView):
    permission_classes = [IsAdminUser]  # Optional, restricts to admins

    def get(self, request):
        # Aggregate by plan_name
        data = (
            Subscription.objects
            .values('plan_name')
            .annotate(
                total_users=Count('user_id', distinct=True),
                total_revenue=Sum('price')
            )
            .order_by('plan_name')
        )

        # Prepare frontend structure
        response_data = {
            "plans": [d['plan_name'] for d in data],
            "users": [d['total_users'] for d in data],
            "revenue": [float(d['total_revenue'] or 0) for d in data]
        }

        return Response(response_data)
    


from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.utils.dateparse import parse_date
from ..models import Payment,SalesPayment,SubscriptionPayment,RentalPayment


class RevenueReportView(APIView):
    def get(self, request):
        start_date = parse_date(request.query_params.get('start_date'))
        end_date = parse_date(request.query_params.get('end_date'))
        
        

        # Base queryset filters
        filters = {}
        if start_date and end_date:
            filters["created_at__range"] = [start_date, end_date]
        if request.query_params.get("rent_id__property_id__property_zone_id__owner_id__id"):
            filters["rent_id__property_id__property_zone_id__owner_id__email"] = request.query_params.get("rent_id__property_id__property_zone_id__owner_id__email")
        if request.query_params.get("rent_id__property_id__property_zone_id__manager_id__id"):
            filters["rent_id__property_id__property_zone_id__manager_id__email"] = request.query_params.get("rent_id__property_id__property_zone_id__manager_id__email")

        # 1️ Rent payments
        rent_data = (
            Payment.objects.filter(status="complete", **filters)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        
        sales_filters = {}
        if start_date and end_date:
            sales_filters["created_at__range"] = [start_date, end_date]
        if request.query_params.get("property_zone_sale_id__property_zone_id__owner_id__id"):
            sales_filters["property_zone_sale_id__property_zone_id__owner_id__id"] = request.query_params.get("property_zone_sale_id__property_zone_id__owner_id__id")
        #  Sales payments
        sale_data = (
            SalesPayment.objects.filter(status="complete", **sales_filters)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        
        subscription_filters = {}
        if start_date and end_date:
            subscription_filters["created_at__range"] = [start_date, end_date]
        if request.query_params.get("subscription_id__user_id__id"):
            subscription_filters["subscription_id__user_id__id"] = request.query_params.get("subscription_id__user_id__id")
        #  Subscription payments
        subscription_data = (
            SubscriptionPayment.objects.filter(status="complete", **subscription_filters)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        
        workspace_filters = {}
        if start_date and end_date:
            workspace_filters["created_at__range"] = [start_date, end_date]
        if request.query_params.get("rental__space__zone__owner_id__id"):
            workspace_filters["rental__space__zone__owner_id__id"] = request.query_params.get("rental__space__zone__owner_id__id")

        #  Workspace (coworking) payments
        workspace_data = (
            RentalPayment.objects.filter(status="complete", **workspace_filters)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        # Collect all unique months
        all_months = sorted(
            set(
                list(d["month"] for d in rent_data)
                + list(d["month"] for d in sale_data)
                + list(d["month"] for d in subscription_data)
                + list(d["month"] for d in workspace_data)
            )
        )

        # Helper to get totals by month
        def get_monthly_totals(data):
            totals = {}
            for d in data:
                totals[d["month"].strftime("%Y-%m")] = float(d["total"] or 0)
            return totals

        rent_totals = get_monthly_totals(rent_data)
        sale_totals = get_monthly_totals(sale_data)
        subscription_totals = get_monthly_totals(subscription_data)
        workspace_totals = get_monthly_totals(workspace_data)

        # Prepare final response
        response_data = {
            "months": [m.strftime("%Y-%m") for m in all_months],
            "rent": [rent_totals.get(m.strftime("%Y-%m"), 0) for m in all_months],
            "sale": [sale_totals.get(m.strftime("%Y-%m"), 0) for m in all_months],
            "subscription": [subscription_totals.get(m.strftime("%Y-%m"), 0) for m in all_months],
            "workspace": [workspace_totals.get(m.strftime("%Y-%m"), 0) for m in all_months],
        }

        return Response(response_data)
    




from django.db.models import Count
from ..models import CustomUser
from django.contrib.auth.models import Group


class UserTypeReportView(APIView):
    """
    Returns the number of users per group (role) for visualization.
    Example response:
    {
      "groups": ["Admin", "Manager", "Tenant", "No Group"],
      "counts": [5, 12, 50, 3]
    }
    """
    def get(self, request):
        # Get all groups with their user counts
        group_data = (
            Group.objects
            .annotate(user_count=Count('customuser'))
            .values('name', 'user_count')
            .order_by('name')
        )

        # Users without any group
        no_group_count = CustomUser.objects.filter(groups__isnull=True).count()

        # Combine results
        groups = [g['name'] for g in group_data] + ['No Group']
        counts = [g['user_count'] for g in group_data] + [no_group_count]

        response_data = {
            "groups": groups,
            "counts": counts
        }

        return Response(response_data)
    


# reports/views.py
from django.contrib.auth.models import Group
from django.db.models import Q


class ExportUsersReportView(APIView):
    """
    Returns users grouped by role with counts and chart summary.
    """

    def get_group_users(self, group_name):
        """Helper: Get users belonging to a group."""
        try:
            group = Group.objects.get(name__iexact=group_name)
            users = CustomUser.objects.filter(groups=group)
        except Group.DoesNotExist:
            users = CustomUser.objects.none()
        return users

    def format_user(self, user):
        """Helper: Format user for frontend."""
        name = " ".join(filter(None, [user.first_name, user.middle_name, user.last_name])) or user.email
        return {
            "id": user.id,
            "name": name,
            "email": user.email,
            "created_at": user.date_joined.strftime("%Y-%m-%d"),
        }

    def get(self, request):
        # Define group names (you can adjust these to your actual roles)
        roles = ["Owner", "Tenant", "Staff", "Manager"]

        results = {}
        chart_labels = []
        chart_series = []

        for role in roles:
            users = self.get_group_users(role)
            results_key = role.lower() + "s"  # e.g., 'owners', 'tenants', etc.
            formatted_users = [self.format_user(u) for u in users]

            results[results_key] = {
                "total": users.count(),
                "data": formatted_users
            }

            chart_labels.append(role + "s")
            chart_series.append(users.count())

        # Build response
        response_data = {
            **results,
            "chart": {
                "labels": chart_labels,
                "series": chart_series
            }
        }

        return Response(response_data)
    


# reports/views.py
from ..models import (
    SubscriptionPayment,
    SalesPayment,
    Payment,
    RentalPayment,
)
from django.db.models import Count
from datetime import datetime


class PaymentsExportReportView(APIView):
    """
    Returns all types of payments grouped by category for exports and charts.
    Example Response:
    {
      "subscription": {...},
      "sales": {...},
      "rent": {...},
      "rental": {...},
      "chart": {...}
    }
    """

    def get(self, request):
        # Optional filters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        filters = {}
        if start_date and end_date:
            filters["created_at__range"] = [start_date, end_date]

        # -------------------------------
        # 1️ Subscription Payments
        # -------------------------------
        subscription_qs = SubscriptionPayment.objects.filter(**filters)
        subscription_data = [
            {
                "id": p.id,
                "user": p.user_id.first_name or p.user_id.email if p.user_id else "N/A",
                "amount": float(p.amount or 0),
                "paid_at": p.paid_at.strftime("%Y-%m-%d") if p.paid_at else None,
            }
            for p in subscription_qs
        ]

        # -------------------------------
        # 2️ Sales Payments
        # -------------------------------
        sales_qs = SalesPayment.objects.filter(**filters)
        sales_data = [
            {
                "id": p.id,
                "buyer": p.buyer_id.first_name or p.buyer_id.email if p.buyer_id else "N/A",
                "amount": float(p.amount or 0),
                "due_date": p.due_date.strftime("%Y-%m-%d") if p.due_date else None,
            }
            for p in sales_qs
        ]

        # -------------------------------
        # 3️ Rent Payments
        # -------------------------------
        rent_qs = Payment.objects.filter(**filters)
        rent_data = [
            {
                "id": p.id,
                "tenant": p.user_id.first_name or p.user_id.email if p.user_id else "N/A",
                "amount": float(p.amount or 0),
                "due_date": p.due_date.strftime("%Y-%m-%d") if p.due_date else None,
            }
            for p in rent_qs
        ]

        # -------------------------------
        #  Workspace (Coworking) Rental Payments
        # -------------------------------
        rental_qs = RentalPayment.objects.filter(**filters)
        rental_data = [
            {
                "id": p.id,
                "tenant": (
                    p.rental.user.first_name
                    if p.rental.user
                    else p.rental.guest_name or "N/A"
                ),
                "amount": float(p.amount or 0),
                "rental__start_date": (
                    p.rental.start_date.strftime("%Y-%m-%d") if p.rental else None
                ),
                "paid_at": p.paid_at.strftime("%Y-%m-%d") if p.paid_at else None,
            }
            for p in rental_qs
        ]

        # -------------------------------
        # 5 Chart Summary
        # -------------------------------
        chart_labels = ["Subscription", "Sales", "Rent", "Workspace"]
        chart_series = [
            subscription_qs.count(),
            sales_qs.count(),
            rent_qs.count(),
            rental_qs.count(),
        ]

        # -------------------------------
        # Final Response
        # -------------------------------
        response_data = {
            "subscription": {
                "total": subscription_qs.count(),
                "data": subscription_data,
            },
            "sales": {
                "total": sales_qs.count(),
                "data": sales_data,
            },
            "rent": {
                "total": rent_qs.count(),
                "data": rent_data,
            },
            "rental": {
                "total": rental_qs.count(),
                "data": rental_data,
            },
            "chart": {
                "labels": chart_labels,
                "series": chart_series,
            },
        }

        return Response(response_data)





    
    