"""Tests for pagination helpers."""

import pytest

from colacloud.models import ColaSummary, Pagination
from colacloud.pagination import AsyncPaginatedIterator, PaginatedIterator


class TestPaginatedIterator:
    """Tests for the synchronous PaginatedIterator."""

    def test_single_page(self):
        """Test iteration over a single page of results."""
        items = [
            ColaSummary(ttb_id="1", brand_name="Brand 1", product_type="wine", permit_number="P1"),
            ColaSummary(ttb_id="2", brand_name="Brand 2", product_type="wine", permit_number="P2"),
        ]
        pagination = Pagination(page=1, per_page=10, total=2, pages=1)

        def fetch_page(page: int):
            if page == 1:
                return items, pagination
            return [], pagination

        iterator = PaginatedIterator(fetch_page)
        result = list(iterator)

        assert len(result) == 2
        assert result[0].ttb_id == "1"
        assert result[1].ttb_id == "2"

    def test_multiple_pages(self):
        """Test iteration over multiple pages."""
        page1_items = [
            ColaSummary(ttb_id="1", brand_name="Brand 1", product_type="wine", permit_number="P1"),
        ]
        page2_items = [
            ColaSummary(ttb_id="2", brand_name="Brand 2", product_type="wine", permit_number="P2"),
        ]

        def fetch_page(page: int):
            if page == 1:
                return page1_items, Pagination(page=1, per_page=1, total=2, pages=2)
            elif page == 2:
                return page2_items, Pagination(page=2, per_page=1, total=2, pages=2)
            return [], Pagination(page=page, per_page=1, total=2, pages=2)

        iterator = PaginatedIterator(fetch_page)
        result = list(iterator)

        assert len(result) == 2
        assert result[0].ttb_id == "1"
        assert result[1].ttb_id == "2"

    def test_empty_results(self):
        """Test iteration with no results."""

        def fetch_page(page: int):
            return [], Pagination(page=1, per_page=10, total=0, pages=0)

        iterator = PaginatedIterator(fetch_page)
        result = list(iterator)

        assert len(result) == 0

    def test_total_property(self):
        """Test that total property is available after first fetch."""
        items = [
            ColaSummary(ttb_id="1", brand_name="Brand 1", product_type="wine", permit_number="P1"),
        ]
        pagination = Pagination(page=1, per_page=10, total=100, pages=10)

        def fetch_page(page: int):
            return items if page == 1 else [], pagination

        iterator = PaginatedIterator(fetch_page)

        # Before fetching
        assert iterator.total is None

        # Trigger first fetch
        next(iterator)

        # After fetching
        assert iterator.total == 100
        assert iterator.pages == 10

    def test_start_page_parameter(self):
        """Test starting from a specific page."""
        page2_items = [
            ColaSummary(ttb_id="2", brand_name="Brand 2", product_type="wine", permit_number="P2"),
        ]

        def fetch_page(page: int):
            if page == 2:
                return page2_items, Pagination(page=2, per_page=1, total=2, pages=2)
            return [], Pagination(page=page, per_page=1, total=2, pages=2)

        iterator = PaginatedIterator(fetch_page, start_page=2)
        result = list(iterator)

        assert len(result) == 1
        assert result[0].ttb_id == "2"


@pytest.mark.asyncio
class TestAsyncPaginatedIterator:
    """Tests for the asynchronous AsyncPaginatedIterator."""

    async def test_single_page(self):
        """Test async iteration over a single page of results."""
        items = [
            ColaSummary(ttb_id="1", brand_name="Brand 1", product_type="wine", permit_number="P1"),
            ColaSummary(ttb_id="2", brand_name="Brand 2", product_type="wine", permit_number="P2"),
        ]
        pagination = Pagination(page=1, per_page=10, total=2, pages=1)

        async def fetch_page(page: int):
            if page == 1:
                return items, pagination
            return [], pagination

        iterator = AsyncPaginatedIterator(fetch_page)
        result = []
        async for item in iterator:
            result.append(item)

        assert len(result) == 2
        assert result[0].ttb_id == "1"
        assert result[1].ttb_id == "2"

    async def test_multiple_pages(self):
        """Test async iteration over multiple pages."""
        page1_items = [
            ColaSummary(ttb_id="1", brand_name="Brand 1", product_type="wine", permit_number="P1"),
        ]
        page2_items = [
            ColaSummary(ttb_id="2", brand_name="Brand 2", product_type="wine", permit_number="P2"),
        ]

        async def fetch_page(page: int):
            if page == 1:
                return page1_items, Pagination(page=1, per_page=1, total=2, pages=2)
            elif page == 2:
                return page2_items, Pagination(page=2, per_page=1, total=2, pages=2)
            return [], Pagination(page=page, per_page=1, total=2, pages=2)

        iterator = AsyncPaginatedIterator(fetch_page)
        result = []
        async for item in iterator:
            result.append(item)

        assert len(result) == 2
        assert result[0].ttb_id == "1"
        assert result[1].ttb_id == "2"

    async def test_empty_results(self):
        """Test async iteration with no results."""

        async def fetch_page(page: int):
            return [], Pagination(page=1, per_page=10, total=0, pages=0)

        iterator = AsyncPaginatedIterator(fetch_page)
        result = []
        async for item in iterator:
            result.append(item)

        assert len(result) == 0

    async def test_total_property(self):
        """Test that total property is available after first fetch."""
        items = [
            ColaSummary(ttb_id="1", brand_name="Brand 1", product_type="wine", permit_number="P1"),
        ]
        pagination = Pagination(page=1, per_page=10, total=100, pages=10)

        async def fetch_page(page: int):
            return items if page == 1 else [], pagination

        iterator = AsyncPaginatedIterator(fetch_page)

        # Before fetching
        assert iterator.total is None

        # Trigger first fetch
        await iterator.__anext__()

        # After fetching
        assert iterator.total == 100
        assert iterator.pages == 10
