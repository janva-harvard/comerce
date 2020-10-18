from django import forms
#from .models import Category


class NewListingsForm (forms.Form):
    title = forms.CharField(label='Title',
                            max_length=20,
                            required=True)
    description = forms.CharField(label='Description',
                                  max_length=200,
                                  required=True)
    starting_bid = forms.DecimalField(label="Starting bid",
                                      max_digits=5,
                                      decimal_places=2,
                                      required=True)
    img_url = forms.URLField(label='Image URL', required=False)
    activated = forms.BooleanField(label="Activate", required=False)
    # category = forms.ModelChoiceField(
    #     queryset=Catgory.objects.all(),  required=False)
