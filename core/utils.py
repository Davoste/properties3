from decimal import Decimal
from .models import ExchangeRate

def convert_to_kes(amount, from_currency):
    if from_currency == "KES":
        return Decimal(amount)
    
    try: 
        rate = ExchangeRate.objects.get(target_currency=from_currency).kes_to_currency

        return Decimal(amount)/rate
    except ExchangeRate.DoesNotExist:
        return Decimal(amount)
    
def convert_from_kes(amount_kes, to_currency):
    if to_currency == "KES":
        return Decimal(amount_kes)

    try:
        rate = ExchangeRate.objects.get(target_currency=to_currency).kes_to_currency

        return Decimal(amount_kes)*rate
    except ExchangeRate.DoesNotExist:
        return(Decimal(amount_kes))    