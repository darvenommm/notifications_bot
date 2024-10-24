from dependency_injector import containers, providers


class Container(containers.Container):
    config = providers.Configuration()
