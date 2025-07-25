from .models import ExchangeRate

def available_currencies(request):
    currencies = ExchangeRate.objects.values_list("target_currency", flat=True)
    return {
        "available_currencies": ["KES"] + list(currencies)  # Always include KES as base
    }