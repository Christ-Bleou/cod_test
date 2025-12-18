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