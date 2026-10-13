"""Os erros que a biblioteca conhece: algo não existe, algo já existe ou uma regra foi quebrada."""


class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class BusinessRuleError(DomainError):
    pass
