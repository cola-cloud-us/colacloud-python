"""Pagination helpers for iterating through large result sets."""

from typing import Any, AsyncIterator, Callable, Iterator, Optional, TypeVar

from .models import ColaSummary, Pagination, PermitteeSummary

T = TypeVar("T", ColaSummary, PermitteeSummary)

# Type alias for fetch_page functions
FetchPageFunc = Callable[[int], tuple[list[T], Pagination]]
AsyncFetchPageFunc = Callable[[int], "tuple[list[T], Pagination]"]


class PaginatedIterator(Iterator[T]):
    """Iterator for paginating through sync API responses.

    This iterator automatically fetches additional pages as needed,
    allowing you to iterate through all results without manually
    handling pagination.

    Example:
        ```python
        for cola in client.colas.iterate(q="whiskey"):
            print(cola.brand_name)
        ```
    """

    def __init__(
        self,
        fetch_page: Callable[[int], tuple[list[T], Pagination]],
        start_page: int = 1,
    ) -> None:
        """Initialize the paginated iterator.

        Args:
            fetch_page: Function that takes a page number and returns
                (items, pagination) tuple.
            start_page: Starting page number (default: 1).
        """
        self._fetch_page: Callable[[int], tuple[list[T], Pagination]] = fetch_page
        self._current_page = start_page
        self._items: list[T] = []
        self._item_index = 0
        self._pagination: Optional[Pagination] = None
        self._exhausted = False

    def __iter__(self) -> "PaginatedIterator[T]":
        return self

    def __next__(self) -> T:
        # If we have items left in current batch, return next one
        if self._item_index < len(self._items):
            item = self._items[self._item_index]
            self._item_index += 1
            return item

        # Check if we've exhausted all pages
        if self._exhausted:
            raise StopIteration

        # Fetch next page
        self._items, self._pagination = self._fetch_page(self._current_page)
        self._item_index = 0
        self._current_page += 1

        # Check if this was the last page
        if self._pagination.page >= self._pagination.pages or len(self._items) == 0:
            self._exhausted = True

        # If no items in this page, we're done
        if len(self._items) == 0:
            raise StopIteration

        # Return first item from new batch
        item = self._items[self._item_index]
        self._item_index += 1
        return item

    @property
    def total(self) -> Optional[int]:
        """Total number of items across all pages, if known."""
        return self._pagination.total if self._pagination else None

    @property
    def pages(self) -> Optional[int]:
        """Total number of pages, if known."""
        return self._pagination.pages if self._pagination else None


class AsyncPaginatedIterator(AsyncIterator[T]):
    """Async iterator for paginating through async API responses.

    This iterator automatically fetches additional pages as needed,
    allowing you to iterate through all results without manually
    handling pagination.

    Example:
        ```python
        async for cola in client.colas.iterate(q="whiskey"):
            print(cola.brand_name)
        ```
    """

    def __init__(
        self,
        fetch_page: Callable[[int], Any],  # Returns Awaitable[tuple[list[T], Pagination]]
        start_page: int = 1,
    ) -> None:
        """Initialize the async paginated iterator.

        Args:
            fetch_page: Async function that takes a page number and returns
                (items, pagination) tuple.
            start_page: Starting page number (default: 1).
        """
        self._fetch_page = fetch_page
        self._current_page = start_page
        self._items: list[T] = []
        self._item_index = 0
        self._pagination: Optional[Pagination] = None
        self._exhausted = False

    def __aiter__(self) -> "AsyncPaginatedIterator[T]":
        return self

    async def __anext__(self) -> T:
        # If we have items left in current batch, return next one
        if self._item_index < len(self._items):
            item = self._items[self._item_index]
            self._item_index += 1
            return item

        # Check if we've exhausted all pages
        if self._exhausted:
            raise StopAsyncIteration

        # Fetch next page
        self._items, self._pagination = await self._fetch_page(self._current_page)
        self._item_index = 0
        self._current_page += 1

        # Check if this was the last page
        if self._pagination.page >= self._pagination.pages or len(self._items) == 0:
            self._exhausted = True

        # If no items in this page, we're done
        if len(self._items) == 0:
            raise StopAsyncIteration

        # Return first item from new batch
        item = self._items[self._item_index]
        self._item_index += 1
        return item

    @property
    def total(self) -> Optional[int]:
        """Total number of items across all pages, if known."""
        return self._pagination.total if self._pagination else None

    @property
    def pages(self) -> Optional[int]:
        """Total number of pages, if known."""
        return self._pagination.pages if self._pagination else None
