from django import forms
from .models import Category


class NewListingsForm (forms.Form):
    title = forms.CharField(label='Title',
                            max_length=20,
                            required=True)
    description = forms.CharField(label='Description',
                                  widget=forms.Textarea,
                                  max_length=200,
                                  required=True)
    starting_bid = forms.DecimalField(label="Starting bid",
                                      max_digits=5,
                                      decimal_places=2,
                                      required=True)
    image_url = forms.URLField(label='Image URL', required=False)

    active = forms.BooleanField(label="Activate",
                                required=False,
                                initial=False,
                                )
    # Hmm I'm not sure i like this
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        blank=True)


class BidForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, required=True, min_value=0.0,
                                widget=forms.TextInput(
                                    attrs={
                                        'class': 'form-control large-input-field'}
                                ))
