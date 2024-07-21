import pytest

from dsg_lib.common_functions.email_validation import validate_email_address


def test_validate_email_address_valid():
    result = validate_email_address('test@google.com')
    assert result['valid'] is True
    assert result['email'] == 'test@google.com'

def test_validate_email_address_invalid():
    result = validate_email_address('invalid')
    assert result['valid'] is False
    assert result['email'] == 'invalid'
    assert result['error_type'] == 'EmailNotValidError'

def test_validate_email_address_undeliverable():
    result = validate_email_address('test@example.com')
    assert result['valid'] is False
    assert result['email'] == 'test@example.com'
    assert result['error_type'] == 'EmailUndeliverableError'


def test_validate_email_address_dns_type():
    with pytest.raises(ValueError):
        validate_email_address('test@google.com', dns_type='invalid')

def test_validate_email_address_timeout():
    result = validate_email_address('test@google.com', timeout=0, dns_type="timeout")
    assert result['valid'] is True
    assert result['email'] == 'test@google.com'

def test_validate_email_address_timeout_invalid():
    with pytest.raises(TypeError):
        validate_email_address('test@example.com', timeout='invalid', dns_type="timeout")

def test_validate_email_address_check_delivery_false():
    result = validate_email_address('test@example.com', check_deliverability=False)
    assert result['valid'] is True
    assert result['email'] == 'test@example.com'
