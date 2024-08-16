# from django.db import models
# from Main.models.payment_models import *
# from Main.models.school_operations_models import *
# from Main.models.transaction_records_models import *
# from django.dispatch import receiver
# from django.db.models.signals import pre_save, post_save
# # from django.dispatch import Signal

# # transaction_status = [('pending', 'Pending'), 
# #                       ('approved', 'Approved'), 
# #                       ('declined', 'Declined')]

# # class Transaction_status(models.Model):
# #     message = models.CharField(max_length=250, choices=transaction_status)

# #     def __str__(self):
# #         return str(self.message)


# staff = Staff_type.objects.all()
# transaction_list = Operations_account_transaction_record.objects.all()
# payroll_list = Payroll.objects.all()

# class Notification(models.Model):
#     sender = models.CharField(max_length=100)
#     recipient = models.CharField(max_length=100, choices=staff.name)
#     date_time = models.DateTimeField(auto_now=True)
#     message = models.TextField()

#     def __str__(self):
#         return f'Sender: {self.sender}, Recipient {self.recipient}'



# @receiver(pre_save, sender=transaction_list)
# def transaction_handler(sender, instance, pk, **kwargs):
#     notification = Notification.objects.get(pk=pk)

#     if instance.status == "PENDING":
#         notification_instance = Notification.objects.create(
#             sender=notification.sender,
#             recipient = notification.recipient,
#             message = notification.message,
#             )
#         notification_instance.save()
#         # indentation error
#         return ("SUCCESS")  
#         print(f'{message}')

#     if instance.status == "SUCCESS":
#         notification_instance = Notification.objects.create(
#             sender= notification.sender,
#             recipient = notification.recipient,
#             message = notification.message,
#             )
#         notification_instance.save()
#         return ("SUCCESS") 
#         print(f'{message}')

#     if instance.status == "CANCELLED":
#         notification_instance = Notification.objects.create(
#             sender= notification.sender,
#             recipient = notification.recipient,
#             message = notification.message,
#             )
#         notification_instance.save()
#         return ("SUCCESS") 
#         print(f'{message}')

#     if instance.status == "INITIALIZED" and instance.transaction_type=="CASH":
#         notification_instance = Notification.objects.create(
#             sender= notification.sender,
#             recipient = notification.recipient,
#             message = notification.message,
#             )
#         notification_instance.save()
#         return ("SUCCESS") 
#         print(f'{message}')

    


# @receiver(pre_save, sender=payroll_list)
# def salary_pending_handler(sender, instance, **kwargs):
#     if instance.status == "PENDING":
#         message = "Salary Payment is Pending"
#         print(f'{message}')

# @receiver(pre_save, sender=payroll_list)
# def salary_initiated_handler(sender, instance, **kwargs):
#     if instance.status == "INITIALIZED":
#         message = "Salary Payment was Initiated"
#         print(f'{message}')

# @receiver(pre_save, sender=payroll_list)
# def salary_success_handler(sender, instance, **kwargs):
#     if instance.status == "SUCCESS":
#         message = "Salary Payment was successful"
#         print(f'{message}')

# @receiver(pre_save, sender=payroll_list)
# def salary_failed_handler(sender, instance, **kwargs):
#     if instance.status == "FAILED":
#         message = "Salary Payment Failed"
#         print(f'{message}')


# """sheryf.534@gmail.com
# 1234"""