import pytest
from web import create_app


class TestCase:
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        # db.create_all()

    def tearDown(self):
        # db.session.remove()
        # db.drop_all()
        self.app_context.pop()


@pytest.fixture(scope='session')
def app_content(tmpdir_factory):
    case = TestCase()
    case.setUp()
    yield case
    case.tearDown()
