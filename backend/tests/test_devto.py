"""
Unit tests for the Dev.to publishing service in devto.py.
Tests use mock_devto_request to avoid real HTTP calls.
"""


class TestPostToPlatform:

    def test_successful_publish_returns_dict(
        self, mock_devto_request
    ):
        """Successful publish returns parsed JSON dict."""
        from devto import post_to_platform

        result = post_to_platform("Two Sum", "# Blog content")
        assert isinstance(result, dict)
        assert result["id"] == 123

    def test_post_sends_correct_title(
        self, mock_devto_request
    ):
        """The title is included in the request body."""
        from devto import post_to_platform

        post_to_platform("Two Sum", "# Blog content")
        call_kwargs = mock_devto_request["request"].call_args[1]
        assert call_kwargs["json"]["article"]["title"] == "LeetCode Solution: Two Sum"

    def test_post_sends_correct_content(
        self, mock_devto_request
    ):
        """The markdown content is included in the request body."""
        from devto import post_to_platform

        post_to_platform("Two Sum", "# Blog content here")
        call_kwargs = mock_devto_request["request"].call_args[1]
        assert "# Blog content here" in (
            call_kwargs["json"]["article"]["body_markdown"]
        )

    def test_devto_api_error_raises(
        self, mock_devto_request
    ):
        """Non-2xx response raises an exception."""
        from devto import post_to_platform

        mock_devto_request["response"].status_code = 500
        mock_devto_request["response"].text = "Internal Server Error"

        import pytest
        with pytest.raises(Exception):
            post_to_platform("Two Sum", "# Blog content")
