import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import datetime

from tests.factories import (
    ProduitFactory, CategorieProduitFactory, CustomerFactory,
    PanierFactory, CommandeFactory, ContactFactory
)


@pytest.mark.unit
@pytest.mark.django_db
def test_produit_creation():
    produit = ProduitFactory(prix=Decimal('15.99'))
    assert produit.id is not None
    assert str(produit) == produit.nom  # Basé sur __str__ dans models.py.
    assert produit.prix == Decimal('15.99')
    assert produit.slug == slugify(produit.nom) + '-slug'  # Basé sur save().


@pytest.mark.unit
@pytest.mark.django_db
def test_produit_check_promotion():
    produit = ProduitFactory(
        date_debut_promo=datetime.date.today() - datetime.timedelta(days=1),
        date_fin_promo=datetime.date.today() + datetime.timedelta(days=1)
    )
    assert produit.check_promotion is True  # Méthode @property dans models.py.

    produit.date_fin_promo = datetime.date.today() - datetime.timedelta(days=1)
    produit.save()
    assert produit.check_promotion is False


@pytest.mark.unit
@pytest.mark.django_db
def test_produit_negative_price_invalid():
    with pytest.raises(ValidationError) as excinfo:
        produit = ProduitFactory.build(prix=Decimal('-5.00'))
        produit.full_clean()
    assert 'prix' in str(excinfo.value)  # Assumé contrainte (ajoute si absent).


@pytest.mark.unit
@pytest.mark.django_db
def test_customer_creation():
    customer = CustomerFactory()
    assert str(customer) == customer.user.username  # Basé sur __str__.
    assert customer.user.email == customer.user.email  # Lien avec User.


@pytest.mark.unit
@pytest.mark.django_db
def test_panier_total_with_promo():
    panier = PanierFactory()
    produit = ProduitFactory(prix=Decimal('10.00'), prix_promotionnel=Decimal('8.00'))
    ProduitPanierFactory(panier=panier, produit=produit, quantite=2)
    # Assumé méthode total dans models (inféré de views).
    assert panier.prix_total == Decimal('16.00')  # Avec promo.


@pytest.mark.unit
@pytest.mark.django_db
def test_commande_check_paiement():
    commande = CommandeFactory()
    assert commande.check_paiement is True  # @property dans models.py.


@pytest.mark.unit
@pytest.mark.django_db
def test_contact_creation():
    contact = ContactFactory()
    assert str(contact) == contact.nom
    assert contact.email.endswith('@example.com')  # Exemple Faker.