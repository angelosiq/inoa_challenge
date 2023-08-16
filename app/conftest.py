import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient
from stocks.models import UserProfile

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture(name="api_client")
def client_api():
    client = APIClient()
    return client


@pytest.fixture()
def stock():
    return baker.make("stocks.Stock")


@pytest.fixture(name="superuser")
def superuser_instance():
    user = baker.make(User, is_superuser=True)

    profile = UserProfile.objects.get(user=user)
    profile.balance = 1000
    profile.save()

    return user


@pytest.fixture()
def interval():
    return baker.make("django_celery_beat.IntervalSchedule", every=5, period="minutes")
