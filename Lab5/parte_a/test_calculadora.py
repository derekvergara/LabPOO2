# parte_a/test_calculadora.py

import pytest
from calculadora import suma, dividir, es_par

def test_suma():
    assert suma(3, 5) == 8
    assert suma(-2, 2) == 0
    assert suma(0, 0) == 0

def test_dividir():
    assert dividir(10, 2) == 5
    with pytest.raises(ValueError):
        dividir(5, 0)

def test_es_par():
    assert es_par(4) is True
    assert es_par(7) is False
    assert es_par(0) is True
