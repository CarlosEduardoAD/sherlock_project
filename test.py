import pytest
import main

def TestConn():
    assert main.on_ready() == True