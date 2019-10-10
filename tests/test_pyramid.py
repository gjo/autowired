import pytest
from autowired import AutowireField
from zope.interface import Interface

try:
    import pyramid
except ImportError:  # pragma: no cover
    pyramid = None


class IFoo(Interface):
    pass


class IBar(Interface):
    pass


class Bar:
    foo = AutowireField(IFoo)


@pytest.mark.skipif(pyramid is None, reason="pyramid is not installed")
def test():
    from pyramid.config import Configurator
    from pyramid.request import Request

    config = Configurator()
    config.include("autowired.pyramid")

    foo = object()
    config.register_service(foo, IFoo)
    config.register_autowire(Bar, IBar)

    def aview(request):
        bar = request.find_service(IBar)
        assert foo is bar.foo

    config.add_route("root", pattern="/")
    config.add_view(aview, route_name="root", renderer="json")
    app = config.make_wsgi_app()
    Request.blank("/").get_response(app)
