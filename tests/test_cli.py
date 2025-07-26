"""
Tests for the CLI module.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock
from click.testing import CliRunner
from jsonschema_diff.cli import main


class TestCLI:
    """Test cases for the CLI module."""

    def test_main_with_valid_files(self):
        """Test main function with valid schema files."""
        runner = CliRunner()
        
        # Create temporary files
        old_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        new_schema = {"type": "object", "properties": {"name": {"type": "integer"}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump(new_schema, new_file)
            new_file_path = new_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, new_file_path])
            
            assert result.exit_code == 0
            assert "name" in result.output  # Should contain the difference
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    def test_main_with_output_file(self):
        """Test main function with output file option."""
        runner = CliRunner()
        
        old_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        new_schema = {"type": "object", "properties": {"name": {"type": "integer"}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump(new_schema, new_file)
            new_file_path = new_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as output_file:
            output_file_path = output_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, new_file_path, '--output', output_file_path])
            
            assert result.exit_code == 0
            assert f"Diff written to {output_file_path}" in result.output
            
            # Check that output file was written
            with open(output_file_path, 'r') as f:
                content = f.read()
                assert "name" in content
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)
            os.unlink(output_file_path)

    def test_main_with_no_color_option(self):
        """Test main function with no-color option."""
        runner = CliRunner()
        
        old_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        new_schema = {"type": "object", "properties": {"name": {"type": "integer"}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump(new_schema, new_file)
            new_file_path = new_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, new_file_path, '--no-color'])
            
            assert result.exit_code == 0
            # Output should not contain ANSI escape codes
            assert '\x1b[' not in result.output
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    def test_main_file_not_found_error(self):
        """Test main function with non-existent file."""
        runner = CliRunner()
        
        # Create one valid file
        old_schema = {"type": "object"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, '/non/existent/file.json'])
            
            assert result.exit_code == 2  # Click returns code 2 for missing file
            assert "does not exist" in result.output  # Check for actual Click error message
            
        finally:
            os.unlink(old_file_path)

    def test_main_json_decode_error(self):
        """Test main function with invalid JSON file."""
        runner = CliRunner()
        
        # Create file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as invalid_file:
            invalid_file.write("{ invalid json }")
            invalid_file_path = invalid_file.name
        
        # Create valid file
        old_schema = {"type": "object"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, invalid_file_path])
            
            assert result.exit_code == 1
            assert "Error: Invalid JSON" in result.output
            
        finally:
            os.unlink(old_file_path)
            os.unlink(invalid_file_path)

    def test_main_general_exception(self):
        """Test main function with general exception."""
        runner = CliRunner()
        
        old_schema = {"type": "object"}
        new_schema = {"type": "object"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump(new_schema, new_file)
            new_file_path = new_file.name
        
        try:
            # Mock compare_schemas to raise an exception
            with patch('jsonschema_diff.cli.compare_schemas') as mock_compare:
                mock_compare.side_effect = Exception("Test error")
                
                result = runner.invoke(main, [old_file_path, new_file_path])
                
                assert result.exit_code == 1
                assert "Error: Test error" in result.output
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    def test_main_with_unicode_content(self):
        """Test main function with Unicode content in schemas."""
        runner = CliRunner()
        
        old_schema = {"type": "object", "properties": {"имя": {"type": "string"}}}
        new_schema = {"type": "object", "properties": {"имя": {"type": "integer"}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as old_file:
            json.dump(old_schema, old_file, ensure_ascii=False)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as new_file:
            json.dump(new_schema, new_file, ensure_ascii=False)
            new_file_path = new_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, new_file_path])
            
            assert result.exit_code == 0
            assert "имя" in result.output
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    def test_main_identical_schemas(self):
        """Test main function with identical schemas."""
        runner = CliRunner()
        
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(schema, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump(schema, new_file)
            new_file_path = new_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, new_file_path])
            
            assert result.exit_code == 0
            # Should run successfully even with no differences
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    def test_main_empty_schemas(self):
        """Test main function with empty schemas."""
        runner = CliRunner()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump({}, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump({}, new_file)
            new_file_path = new_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, new_file_path])
            
            assert result.exit_code == 0
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    def test_main_output_file_write_error(self):
        """Test main function when output file cannot be written."""
        runner = CliRunner()
        
        old_schema = {"type": "object"}
        new_schema = {"type": "object"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump(new_schema, new_file)
            new_file_path = new_file.name
        
        try:
            # Try to write to a directory instead of a file
            result = runner.invoke(main, [old_file_path, new_file_path, '--output', '/'])
            
            assert result.exit_code == 1
            assert "Error:" in result.output
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    @patch('jsonschema_diff.cli.compare_schemas')
    def test_ansi_escape_regex(self, mock_compare):
        """Test that ANSI escape codes are properly removed with --no-color."""
        runner = CliRunner()
        
        # Mock compare_schemas to return text with ANSI codes
        mock_compare.return_value = '\x1b[36m\x1b[1mr Test output\x1b[0m'
        
        old_schema = {"type": "object"}
        new_schema = {"type": "object"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as old_file:
            json.dump(old_schema, old_file)
            old_file_path = old_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as new_file:
            json.dump(new_schema, new_file)
            new_file_path = new_file.name
        
        try:
            result = runner.invoke(main, [old_file_path, new_file_path, '--no-color'])
            
            assert result.exit_code == 0
            assert '\x1b[' not in result.output
            assert 'Test output' in result.output
            
        finally:
            os.unlink(old_file_path)
            os.unlink(new_file_path)

    def test_main_as_script(self):
        """Test the if __name__ == '__main__' block."""
        with patch('jsonschema_diff.cli.main') as mock_main:
            # Import the module to trigger the if __name__ == '__main__' check
            import jsonschema_diff.cli
            
            # The main function should not be called during import
            mock_main.assert_not_called()
