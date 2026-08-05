from unittest.mock import Mock

import web_dependencies


def test_get_movie_service_builds_dependencies_and_closes_connection(
    monkeypatch,
) -> None:
    conn = Mock()
    repository = Mock()
    service = Mock()

    connect_mock = Mock(return_value=conn)
    initialize_mock = Mock()
    repository_factory = Mock(return_value=repository)
    service_factory = Mock(return_value=service)

    monkeypatch.setattr(web_dependencies, "connect", connect_mock)
    monkeypatch.setattr(
        web_dependencies,
        "initialize_database",
        initialize_mock,
    )
    monkeypatch.setattr(
        web_dependencies,
        "MovieRepository",
        repository_factory,
    )
    monkeypatch.setattr(
        web_dependencies,
        "MovieServices",
        service_factory,
    )

    dependency = web_dependencies.get_movie_service()

    assert next(dependency) is service
    dependency.close()

    connect_mock.assert_called_once_with()
    initialize_mock.assert_called_once_with(conn)
    repository_factory.assert_called_once_with(conn)
    service_factory.assert_called_once_with(
        web_dependencies.api_client,
        repository,
    )
    conn.close.assert_called_once_with()
