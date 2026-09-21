from django import forms

from .models import DeliveryLocation


class CheckoutForm(forms.Form):

    first_name = forms.CharField(
        max_length=100
    )

    last_name = forms.CharField(
        max_length=100
    )

    email = forms.EmailField()

    phone = forms.CharField(
        max_length=30
    )

    address = forms.CharField(
        max_length=255
    )

    city = forms.CharField(
        max_length=150
    )

    state = forms.CharField(
        max_length=120
    )

    zip = forms.CharField(
        max_length=30,
        required=False
    )

    country = forms.CharField(
        max_length=100
    )

    delivery_location = forms.ModelChoiceField(
        queryset=DeliveryLocation.objects.none()
    )


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            "delivery_location"
        ].queryset = (
            DeliveryLocation.objects.filter(
                is_active=True
            )
        )