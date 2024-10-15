import pytest
import tomllib
import argparse
from unittest.mock import patch, mock_open, MagicMock
import pymodule
from pymodule import core
#from core import config
#from config import Config
#from pymodule.logger import getAppLogger

class TestConfig:

    @pytest.fixture
    def config_instance(self):
        """Fixture to create a fresh instance of Config."""
        return pymodule.core.Config()

    def test_default_config(self, config_instance):
        """
        Test that the default configuration is correctly initialized.
        """
        expected_config = pymodule.core.Config.DEFAULT_CONFIG
        assert config_instance.config == expected_config

    @patch('pymodule.core.config.open', new_callable=mock_open, read_data=b'{"parameters": {"param1": 10}}')
    @patch('pymodule.core.config.tomllib.load')
    def test_load_toml_success(self, mock_tomli_load, mock_open, config_instance):
        """
        Test that a valid TOML file is loaded correctly.
        """
        mock_tomli_load.return_value = {"parameters": {"param1": 10}}
        config_file = config_instance.load_toml("config.toml")
        assert config_file == {"parameters": {"param1": 10}}
        mock_open.assert_called_once_with("config.toml", 'rb')
        mock_tomli_load.assert_called_once()

    @patch('pymodule.core.config.open', side_effect=FileNotFoundError)
    def test_load_toml_file_not_found(self, mock_open, config_instance):
        """
        Test that FileNotFoundError is raised and logged when the TOML file is not found.
        """
        with patch('pymodule.core.config.logger') as mock_logger:
            with pytest.raises(FileNotFoundError):
                config_instance.load_toml("missing.toml")
            mock_logger.error.assert_called_once()

    def test_load_config_file_invalid_syntax(self, config_instance):
        # Mock the open and tomllib.load to simulate invalid TOML syntax
        with patch('pymodule.core.config.open', new_callable=mock_open, read_data=b'invalid_toml_data'):
            with patch('pymodule.core.config.tomllib.load', side_effect=tomllib.TOMLDecodeError("Invalid TOML", "", 0)):
                # Use pytest.raises to check if the appropriate exception is raised
                with pytest.raises(tomllib.TOMLDecodeError):
                    config_instance.load_config_file(file_path='invalid_config.toml')

    @patch.object(pymodule.core.Config, 'load_toml', return_value={"parameters": {"param1": 10}})
    def test_load_config_file(self, mock_load_toml, config_instance):
        """
        Test that the config file is loaded and deep_update is called.
        """
        with patch.object(core.Config, 'deep_update') as mock_deep_update:
            config_file = config_instance.load_config_file("config.toml")
            assert config_file == {"parameters": {"param1": 10}}
            mock_load_toml.assert_called_once_with(file_path='config.toml')
            mock_deep_update.assert_called_once_with(config=config_instance.config, config_file={"parameters": {"param1": 10}})

    def test_load_config_file_with_empty_name(self, config_instance):
        """
        Test that load_config_file returns an empty dict when given an empty filename.
        """
        result = config_instance.load_config_file("")
        assert result == {}

    def test_load_config_file_with_default(self, config_instance):
        """
        Test that the default 'config.toml' is used if None is passed.
        """
        with patch('pymodule.core.config.logger') as mock_logger:
            with patch.object(core.Config, 'load_toml', return_value={"logging": {"verbose": False}}) as mock_load_toml:
                config_instance.load_config_file(None)
                mock_logger.error.assert_called_once_with("CFG: Using default 'None'")
                mock_load_toml.assert_called_once_with(file_path="config.toml")

    # Deep Update Tests
    def test_deep_update_basic_merge(self, config_instance):
        """
        Test deep_update with a basic merge scenario.
        """
        config = {'param1': 1, 'param2': 2}
        config_file = {'param1': 100}  # Update param1
        config_instance.deep_update(config, config_file)
        expected_config = {'param1': 100, 'param2': 2}
        assert config == expected_config

    def test_deep_update_nested_merge(self, config_instance):
        """
        Test deep_update with nested dictionaries.
        """
        config = {'nested': {'key1': 'value1', 'key2': 'value2'}}
        config_file = {'nested': {'key2': 'new_value2', 'key3': 'value3'}}
        config_instance.deep_update(config, config_file)
        expected_config = {'nested': {'key1': 'value1', 'key2': 'new_value2', 'key3': 'value3'}}
        assert config == expected_config

    def test_deep_update_overwrite_non_dict(self, config_instance):
        """
        Test deep_update where a non-dict value overwrites a dict value.
        """
        config = {'nested': {'key1': 'value1'}}
        config_file = {'nested': 'new_value'}
        config_instance.deep_update(config, config_file)
        expected_config = {'nested': 'new_value'}
        assert config == expected_config

    def test_deep_update_add_new_key(self, config_instance):
        """
        Test deep_update where a new key is added to the configuration.
        """
        config = {'existing_key': 'value'}
        config_file = {'new_key': 'new_value'}
        config_instance.deep_update(config, config_file)
        expected_config = {'existing_key': 'value', 'new_key': 'new_value'}
        assert config == expected_config

    def test_merge_options(self, config_instance):
        """
        Test the merge_options function with CLI arguments.
        """
        cli_args = argparse.Namespace(param1=10, param2=20, verbose=False)
        config_file = {
            'parameters': {'param1': 1, 'param2': 2},
            'logging': {'verbose': True}
        }
        config_instance.config = config_file  # Simulate loaded config
        merged_config = config_instance.merge_options(config_file, cli_args)

        expected_config = {
            'parameters': {'param1': 10, 'param2': 20},  # CLI args should override
            'logging': {'verbose': False}  # CLI arg should override
        }
        assert merged_config == expected_config

    def test_merge_options_no_cli(self, config_instance):
        """
        Test merge_options with no CLI arguments (None).
        """
        config_file = {
            'parameters': {'param1': 1, 'param2': 2},
            'logging': {'verbose': True}
        }
        config_instance.config = config_file  # Simulate loaded config
        merged_config = config_instance.merge_options(config_file, None)

        expected_config = {
            'parameters': {'param1': 1, 'param2': 2},
            'logging': {'verbose': True}
        }
        assert merged_config == expected_config  # No changes without CLI args
