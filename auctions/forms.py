from django import forms
from .models import Category


class NewListingsForm (forms.Form):
    title = forms.CharField(label='Title',
                            widget=forms.TextInput(attrs={
                                'class': 'form-control '}
                            ),
                            max_length=20,
                            required=True)
    description = forms.CharField(label='Description',
                                  #   widget=forms.TextInput,
                                  widget=forms.Textarea(
                                      attrs={'class': 'form-control '}),
                                  max_length=500,
                                  required=True)
    starting_bid = forms.DecimalField(label="Starting bid",
                                      widget=forms.NumberInput(
                                          attrs={
                                              'class': 'form-control  '
                                          }),
                                      max_digits=5,
                                      decimal_places=2,
                                      required=True)
    image_url = forms.URLField(label='Image URL',
                               widget=forms.TextInput(attrs={
                                     'class': 'form-control'}),
                               required=False)

    active = forms.BooleanField(label="Activate",
                                widget=forms.CheckboxInput(
                                    attrs={
                                        'class': 'form-check'
                                    }
                                ),
                                required=False,
                                initial=False,
                                )
    # Hmm I'm not sure i like this
    category = forms.ModelChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        queryset=Category.objects.all(),
        required=False,
        blank=True)


class BidForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, required=True, min_value=0.0,
                                widget=forms.TextInput(
                                    attrs={
                                        'class': 'form-control large-input-field'}
                                ))
