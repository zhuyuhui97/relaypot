from twisted.application import internet
from twisted.internet import endpoints
from twisted.application import service

top_service = service.MultiService()


def create_endpoint_services(reactor, parent, listen_endpoints, factory):
    for listen_endpoint in listen_endpoints:
        endpoint = endpoints.serverFromString(reactor, listen_endpoint)

        service = internet.StreamServerEndpointService(endpoint, factory)
        # FIXME: Use addService on parent ?
        service.setServiceParent(parent)
