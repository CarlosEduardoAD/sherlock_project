import pytest
import main

def test_conn():
    assert main.on_ready() == True