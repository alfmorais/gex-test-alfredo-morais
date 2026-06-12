from enum import Enum

import pytest

from src.views.enum.gateways import Gateway


class TestGatewayEnum:
    @pytest.mark.asyncio
    async def test_gateway_values(self):
        assert Gateway.GRUMMER.value == "grummer", (
            "O valor para GRUMMER deve ser 'grummer'"
        )
        assert Gateway.LOUS.value == "lous", (
            "O valor para LOUS deve ser 'lous'"
        )

    @pytest.mark.asyncio
    async def test_gateway_inheritance(self):
        assert isinstance(Gateway.GRUMMER, str), (
            "Gateway deve ser uma instância de str"
        )
        assert isinstance(Gateway.GRUMMER, Enum), (
            "Gateway deve ser uma instância de Enum"
        )

    @pytest.mark.asyncio
    async def test_gateway_list_content(self):
        expected_gateways = {"grummer", "lous"}
        actual_gateways = {g.value for g in Gateway}

        assert actual_gateways == expected_gateways, (
            f"Gateways encontrados: {actual_gateways}"
        )

    @pytest.mark.asyncio
    async def test_gateway_uniqueness(self):
        assert len(Gateway) == len(set(g.value for g in Gateway)), (
            "Valores de Gateway devem ser únicos"
        )
