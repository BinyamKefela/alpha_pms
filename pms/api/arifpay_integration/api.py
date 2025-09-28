import requests
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from pms.models import Notification, Payment, Rent
import datetime
from django.contrib.auth import get_user_model
from ..payment import PAYMENT_PENDING, PAYMENT_COMPLETE, PAYMENT_CANCELLED, PAYMENT_METHOD_UNSET, PAYMENT_FAILED
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
URL = "https://gateway.arifpay.org/api/checkout/session"
X_ARIFPAY_KEY = "z3iBlZ3Jqdb3ZVyhOE1WnjTWfOunYbZK"

User = get_user_model()


CANCEL_URL = settings.CANCEL_URL
PHONE = settings.PHONE
EMAIL = settings.EMAIL
ERROR_URL = settings.ERROR_URL
NOTIFY_URL = settings.NOTIFY_URL
SUCCESS_URL = settings.SUCCESS_URL
BENEFICIARY_ACCOUNT_NUMBER = settings.BENEFICIARY_ACCOUNT_NUMBER
BANK = settings.BANK

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_rent(request):
    data = request.data
    try:
        user = User.objects.get(id=data.get('user_id'))
    except:
        return Response({"error":"there is no user with the given id"},status=status.HTTP_400_BAD_REQUEST)
    try:
        rent = Rent.objects.get(id=int(data.get('rent_id')))
    except:
        return Response({"error":"there is no rent with the given id"},status=status.HTTP_400_BAD_REQUEST)
    
    payment = Payment()


     #creating the payment in own database
    payment.rent_id = rent
    payment.user_id = user
    payment.amount = float(data.get("amount"))
    payment.due_date = rent.end_date
    payment.status = PAYMENT_PENDING
    payment.payment_method = PAYMENT_METHOD_UNSET
    #payment.transaction_id = 
    payment.created_at = datetime.datetime.now() 
    #payment.updated_at = 

    payment.save()

    items = data.get("items",[])
    if not isinstance(items, list) or not items:
        return Response({"error": "Invalid or missing 'items' list"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
       total_amount = sum(item["price"] * item["quantity"] for item in items)
    except (KeyError, TypeError):
       return Response({"error": "Each item must contain 'price' and 'quantity' as numbers."}, status=status.HTTP_400_BAD_REQUEST)
    
    headers={
        "content-type":"application/json"
                }
    payload = {
      "cancelUrl": CANCEL_URL,
      "phone": PHONE,
      "email":EMAIL,
      "nonce": payment.pk, 
      "errorUrl": ERROR_URL,
      "notifyUrl": NOTIFY_URL,
      "successUrl": SUCCESS_URL,
      "paymentMethods":  ["TELEBIRR","AWASH","AWASH_WALLET","PSS","CBE","AMOLE","BOA","KACHA","TELEBIRR_USSD","HELLOCASH","MPESSA"],
      "expireDate": "2025-02-01T03:45:27",
      "items": items,
      "beneficiaries": [
          {
              "accountNumber": BENEFICIARY_ACCOUNT_NUMBER, 
              "bank": BANK,
              "amount": total_amount
          }
      ],
      "lang": "EN"
        }
    
    try:
        response = requests.post(f"{settings.INTERNAL_API_BASE_URL}/pms/api/arif_pay_check_out",json=payload)
    except:
        return Response({"there was an error in the payment process"},headers=headers,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message":"successfully posted data to checkout api"},status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_out(request):
    
    headers={
        "content-type":"application/json",
        "x-arifpay-key":X_ARIFPAY_KEY
    }

    body = request.data

    response = requests.post(url=URL,json=body,headers=headers)
    if not response.ok:
        return Response(response.json(),status=response.status_code)
   

    success_url = response.json().get("data").get("paymentUrl")
    if success_url:
        return redirect(to=success_url)
    return Response(response.json(),status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([])
def payment_complete(request):
    data = request.data
    try:
       #update the payment data
       payment = Payment.objects.get(pk=int(data.get("nonce")))
       payment.payment_method = data.get("paymentMethod")
       payment.amount = data.get("totalAmount")
       payment.status = payment.status = (
           PAYMENT_COMPLETE if data.get("transaction", {}).get("transactionStatus") == "SUCCESS"
             else PAYMENT_FAILED)

       payment.transaction_id = data.get("transaction").get("transactionId")
       payment.updated_at = datetime.datetime.now()
       payment.save()

    except:
        return Response({"error":"There was an error in saving the payment status"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #create the notification object
    notification = Notification()
    notification.notification_type = "payment_complete"
    try:
        notification.rent_id = Rent.objects.get(pk = payment.rent_id)
    except:
        return Response({"error":"there is nor rent associated with the payment made"},status=status.HTTP_400_BAD_REQUEST)
    notification.message = f"payment made for rent id {payment.rent_id} with amount {payment.amount} on date {payment.updated_at}"
    notification.created_at = datetime.datetime.now()
