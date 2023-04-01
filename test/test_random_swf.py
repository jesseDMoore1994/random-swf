from returns.io import IO, IOSuccess, Success, IOFailure, Failure
from unittest.mock import patch, MagicMock
from requests import Session
from requests.exceptions import HTTPError
from random_swf import random_swf


@patch.object(Session, "get")
def test_get_page_success(mock_get):
    mock_resp = mock_get.return_value = MagicMock()
    mock_resp.content = b"<head/>"
    match random_swf.get_page("https://locker.phinugamma.org/swf/"):
        case IOSuccess(Success(value)): 
            assert value == {
                "base_url": "https://locker.phinugamma.org/swf/",
                "content": "<head/>"
            }
        case IOFailure(_):
            assert False

    mock_get.assert_called_once_with(
        "https://locker.phinugamma.org/swf/",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
    )


@patch.object(Session, "get")
def test_get_page_failure(mock_get):
    mock_resp = mock_get.return_value = MagicMock()
    mock_resp.raise_for_status.side_effect = [HTTPError("error")]
    match random_swf.get_page("https://locker.phinugamma.org/swf/"):
        case IOSuccess(_): 
            assert False 
        case IOFailure(Failure(value)):
            assert isinstance(value, HTTPError)

    mock_get.assert_called_once_with(
        "https://locker.phinugamma.org/swf/",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
    )

def test_get_links():
    with open("test/mock_page.html") as f:
        page = {
            "base_url": "http://baseurl.com/swf/",
            "content": f.read()
        }
    with open("test/expected_links.txt") as f:
        expected_links = f.read().splitlines()
    assert random_swf.get_links(page)({
        "blacklist": ["../"]
    }) == expected_links
