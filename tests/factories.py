import factory
from django.contrib.auth.models import User
from shop.models import Produit, CategorieProduit, Etablissement, CategorieEtablissement
from customer.models import Customer, Panier, Commande, ProduitPanier
from contact.models import Contact, NewsLetter
from cities_light.models import City
from decimal import Decimal
from django.utils import timezone


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City

    name = factory.Faker('city')


class CategorieEtablissementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategorieEtablissement

    nom = factory.Faker('word')
    description = factory.Faker('text')


class EtablissementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Etablissement

    user = factory.SubFactory(UserFactory)
    nom = factory.Faker('company')
    categorie = factory.SubFactory(CategorieEtablissementFactory)
    ville = factory.SubFactory(CityFactory)


class CategorieProduitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategorieProduit

    nom = factory.Faker('word')
    description = factory.Faker('text')


class ProduitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Produit

    nom = factory.Faker('word')
    description = factory.Faker('text')
    prix = Decimal('10.00')
    etablissement = factory.SubFactory(EtablissementFactory)
    categorie = factory.SubFactory(CategorieProduitFactory)
    slug = factory.LazyAttribute(lambda obj: f"{obj.nom.lower()}-slug")


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory)
    adresse = factory.Faker('address')
    contact_1 = factory.Faker('phone_number')
    ville = factory.SubFactory(CityFactory)


class PanierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Panier

    customer = factory.SubFactory(CustomerFactory)
    code_promo = None  # Optionnel


class ProduitPanierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProduitPanier

    produit = factory.SubFactory(ProduitFactory)
    panier = factory.SubFactory(PanierFactory)
    quantite = 1


class CommandeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Commande

    customer = factory.SubFactory(CustomerFactory)
    prix_total = Decimal('10.00')


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    nom = factory.Faker('name')
    email = factory.Faker('email')
    sujet = factory.Faker('sentence')
    message = factory.Faker('text')


class NewsLetterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsLetter

    email = factory.Faker('email')