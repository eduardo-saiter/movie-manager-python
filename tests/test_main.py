from unittest.mock import Mock

import main as main_module


def test_main_exits_and_closes_connection(monkeypatch, capsys) -> None:
    conn = Mock()
    monkeypatch.setattr(main_module, "connect", Mock(return_value=conn))
    monkeypatch.setattr(main_module, "initialize_database", Mock())
    monkeypatch.setattr(main_module, "MovieApiClient", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "MovieRepository", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "MovieServices", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "menu", Mock())
    monkeypatch.setattr("builtins.input", Mock(return_value="6"))

    main_module.main()

    assert "Saindo do sistema" in capsys.readouterr().out
    conn.close.assert_called_once_with()


def test_main_closes_connection_after_keyboard_interrupt(monkeypatch, capsys) -> None:
    conn = Mock()
    monkeypatch.setattr(main_module, "connect", Mock(return_value=conn))
    monkeypatch.setattr(main_module, "initialize_database", Mock())
    monkeypatch.setattr(main_module, "MovieApiClient", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "MovieRepository", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "MovieServices", Mock(return_value=Mock()))
    monkeypatch.setattr(main_module, "menu", Mock())
    monkeypatch.setattr("builtins.input", Mock(side_effect=KeyboardInterrupt))

    main_module.main()

    assert "Programa interrompido pelo usuário" in capsys.readouterr().out
    conn.close.assert_called_once_with()
