from authmate.models import PrincipalRecord, PrincipalRef
from authmate.protocols import PrincipalProvider


class InvalidProvider(PrincipalProvider):
    async def get_principal(self, ref: PrincipalRef) -> PrincipalRecord:
        return "not a PrincipalRecord"
