class ServiceContainer:
    def __init__(self):
        self.services = {}

    def register(self, name, service) -> None:
        self.services[name] = service

    def get(self, name) -> object:
        return self.services[name]

    def get_all(self) -> dict:
        return self.services

    def remove(self, name) -> None:
        del self.services[name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, service):
        self.register(name, service)

    def __contains__(self, name):
        return name in self.services

    def __iter__(self):
        return iter(self.services)

    def __len__(self):
        return len(self.services)

    def __repr__(self):
        return f"<ServiceContainer {self.services}>"

    def __str__(self):
        return f"<ServiceContainer {self.services}>"


service_container = None


def get_service_container_instance():
    global service_container
    if service_container is None:
        service_container = ServiceContainer()
    return service_container


class ContainerSingleton:
    _instance = None

    def __new__(self, value):
        if self._instance is None:
            self._instance = super(ContainerSingleton, self).__new__(self)
            self.value = value
        return self._instance
