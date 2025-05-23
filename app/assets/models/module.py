from abc import ABC, ABCMeta, abstractmethod


class ApiModule(ABC, metaclass=ABCMeta):
    @abstractmethod
    def __enter__(self):
        return NotImplemented

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        return NotImplemented

    def __call__(self, *args, **kwargs) -> "ApiModule":
        return self

    @abstractmethod
    def run(self, *args, **kwargs) -> dict[str, any]:
        return NotImplemented
