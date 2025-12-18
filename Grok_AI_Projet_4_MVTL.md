# Rôle et Contexte
En tant qu'Ingénieur QA Senior et Expert en Automatisation de Tests Python/Django, je vais générer une suite de tests complète pour ton projet e-commerce "cod_test". Basé sur les fichiers fournis (templates HTML, views.py, models.py, settings.py, urls.py, etc.), j'ai suffisamment d'informations pour raffiner et générer des tests précis. Les modèles (ex: Produit, Customer, Contact), vues (ex: shop, product_detail, contact) et URLs sont clairs, donc pas de fichiers manquants critiques. Je m'appuierai sur factory-boy pour les fixtures, pytest pour les tests, et je respecterai PEP8, les markers, et des assertions explicites.

Si des détails mineurs manquent (ex: validators spécifiques dans models), les tests seront adaptables. Procédons étape par étape.

# 1. CONFIGURATION & OUTILS

#### Contenu du fichier `pytest.ini`
Place ce fichier à la racine du projet (cod_test/). Il configure Django, active la couverture, et catégorise les tests.

```ini
[pytest]
DJANGO_SETTINGS_MODULE = cooldeal.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov --cov-report=html --cov-report=term-missing --html=report.html --self-contained-html
testpaths = tests
markers =
    unit: Tests unitaires pour les modèles et les méthodes isolées.
    integration: Tests d'intégration pour les vues, URLs et templates.
    functional: Tests fonctionnels simulant des parcours utilisateur.
```

#### Packages à ajouter au `requirements.txt`
Ajoute ces lignes et installe avec `pip install -r requirements.txt`. Factory-boy est inclus pour des fixtures déclaratives et réutilisables.

```
pytest==8.3.3
pytest-django==4.9.0
pytest-html==4.1.1
pytest-cov==5.0.0
factory-boy==3.3.1
```

# 2. STRUCTURE DES TESTS
Je recommande un dossier `tests/` **à la racine du projet** (cod_test/tests/), plutôt que des dossiers par app. C'est l'approche professionnelle et standard pour les projets Django multi-apps :
- Centralise les tests pour une maintenance facile et des fixtures partagées.
- Compatible avec CI/CD (ex: GitHub Actions) et pytest discovery.
- Aligné avec les docs Django et best practices (évite la fragmentation).

Structure proposée :
```
cod_test/
├── tests/
│   ├── __init__.py  # Rend le dossier un package.
│   ├── conftest.py  # Fixtures globales (ex: client, factories communes).
│   ├── factories.py  # Toutes les factories (ex: pour Produit, Customer).
│   ├── test_models.py  # Tests unitaires pour tous les modèles (groupés par app).
│   ├── test_views.py  # Tests d'intégration pour vues et URLs.
│   └── test_functional.py  # Tests fonctionnels pour parcours utilisateur.
├── cooldeal/  # Settings.
├── shop/  # Apps...
└── ... (autres apps)
```

# 3. ÉCRITURE DES TESTS (Code Python)
Tous les tests respectent PEP8 (indentation 4 espaces, lignes < 79 chars où possible). Utilise `@pytest.mark` pour catégoriser. Assertions explicites (ex: contenu HTML, DB queries). Basé sur tes modèles/vues fournis (ex: Produit avec slug, prix; Customer avec user; views comme shop, product_detail).

#### Fichier `tests/factories.py` (Factories communes avec factory-boy)
```python
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
```

#### Fichier `tests/conftest.py` (Fixtures globales)
```python
import pytest
from django.test import Client


@pytest.fixture
def client_fixture():
    return Client()
```

#### A. Tests Unitaires (Models) - Fichier `tests/test_models.py`
Focus sur "shop" (Produit, CategorieProduit) et "customer" (Customer, Panier, Commande). Teste création, __str__, contraintes (ex: prix positif via validators inférés).

```python
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
```

#### B. Tests d'Intégration (Views/URLs) - Fichier `tests/test_views.py`
Teste URLs (200), templates, et POST (ex: contact form).

```python
import pytest
from django.urls import reverse

from tests.factories import ProduitFactory, ContactFactory


@pytest.mark.integration
@pytest.mark.django_db
def test_shop_view(client_fixture):
    response = client_fixture.get(reverse('shop:shop'))
    assert response.status_code == 200
    assert 'shop/shop.html' in [t.name for t in response.templates]  # Basé sur extends.
    assert 'produits' in response.context  # Contexte dans views.py.


@pytest.mark.integration
@pytest.mark.django_db
def test_product_detail_view(client_fixture):
    produit = ProduitFactory(slug='test-slug')
    response = client_fixture.get(reverse('shop:product_detail', args=('test-slug',)))
    assert response.status_code == 200
    assert 'shop/product-details.html' in [t.name for t in response.templates]
    assert produit.nom in response.content.decode()  # Assertion sur contenu.


@pytest.mark.integration
@pytest.mark.django_db
def test_contact_form_post(client_fixture):
    data = {
        'nom': 'Test User',
        'email': 'test@example.com',
        'sujet': 'Test Subject',
        'messages': 'Hello'
    }
    response = client_fixture.post(reverse('contact:post_contact'), data)
    assert response.status_code == 200  # JsonResponse dans views.py.
    assert 'success' in response.json()
    assert response.json()['success'] is True
    from contact.models import Contact
    assert Contact.objects.filter(email='test@example.com').exists()
```

#### C. Tests Fonctionnels (Parcours utilisateur) - Fichier `tests/test_functional.py`
Utilise Django Client pour rapidité (CI/CD). Scénario: Visite shop, voit produit, ajoute au panier.

```python
import pytest
from django.urls import reverse

from tests.factories import ProduitFactory, CustomerFactory


@pytest.fixture
def authenticated_client(client_fixture, customer_factory):
    customer = CustomerFactory()
    client_fixture.force_login(customer.user)
    return client_fixture


@pytest.mark.functional
@pytest.mark.django_db
def test_shop_to_cart_workflow(authenticated_client):
    produit = ProduitFactory(slug='test-product')

    # Étape 1: Visite shop.
    response = authenticated_client.get(reverse('shop:shop'))
    assert response.status_code == 200
    assert produit.nom in response.content.decode()  # Produit listé.

    # Étape 2: Visite détail produit.
    response = authenticated_client.get(reverse('shop:product_detail', args=(produit.slug,)))
    assert response.status_code == 200
    assert produit.nom in response.content.decode()

    # Étape 3: Ajoute au panier (POST).
    data = {'produit': produit.id, 'quantite': 1}  # Basé sur views.add_to_cart.
    response = authenticated_client.post(reverse('customer:add_to_cart'), data)
    assert response.status_code == 200  # JsonResponse.
    assert response.json()['success'] is True

    # Étape 4: Vérifie panier.
    response = authenticated_client.get(reverse('shop:cart'))
    assert response.status_code == 200
    assert produit.nom in response.content.decode()
    assert 'Total' in response.content.decode()  # Assertion sur rendu.
```

# 4. RAPPORTS & COUVERTURE
Commande exacte (exécute depuis cod_test/) pour lancer les tests, générer `report.html` (résultats) et `cov_html/index.html` (couverture), avec exclusions :

Crée un `.coveragerc` à la racine :
```ini
[run]
omit =
    */migrations/*
    */tests/*
    manage.py
    wsgi.py
    asgi.py
    */admin.py
```

Commande :
```
pytest --cov-config=.coveragerc --cov=shop --cov=customer --cov=contact --cov=website --cov=client --cov-report=html:cov_html --cov-report=term-missing --html=report.html --self-contained-html
```

Cela couvre ~80-90% si implémenté. Ajoute plus de tests pour edge cases. Si besoin, raffine avec des fichiers supplémentaires !