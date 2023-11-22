#encode = 'utf-8'
import pytest
from fibonacci import fibonacci


def test_0():
	assert fibonacci(0) == [0]

def test_1():
	assert fibonacci(1) == [0, 1]

def test_2():
	assert fibonacci(2) == [0, 1, 1]

def test_5():
	assert fibonacci(5) == [0, 1, 1, 2, 3, 5]

def test_n():
	for n in range(10,1000):
		assert fibonacci(n).len() == n+1

