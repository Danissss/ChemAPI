from django.db import models

# Create your models here.

class Property(models.Model):
	inchikey = models.TextField()
	inchi    = models.TextField()
	smiles   = models.TextField()
	value    = models.DecimalField(decimal_places=3,max_digits=8)
	property_name = models.CharField(max_length=256)
	source   = models.TextField()
	create_date = models.DateTimeField()

	# method
	# def search(self, structure, property_name, source):


