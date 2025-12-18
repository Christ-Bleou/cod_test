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