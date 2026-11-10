"""Offline checks for the API boundary without camera/model imports or live credentials."""

import ast
import contextlib
import io
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / 'app.py'
TREE = ast.parse(SOURCE.read_text(), filename=str(SOURCE))


def configuration_code():
    nodes = []
    for node in TREE.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in {'api_key', 'client'}
            for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.If) and any(
            isinstance(child, ast.Raise) for child in ast.walk(node)
        ):
            nodes.append(node)
    return compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec')


class ConfigurationTests(unittest.TestCase):
    def run_configuration(self, value):
        calls = []
        def fake_openai(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(configured=True)
        namespace = {'os': os, 'OpenAI': fake_openai}
        environment = {} if value is None else {'OPENAI_API_KEY': value}
        with patch.dict(os.environ, environment, clear=True):
            try:
                exec(configuration_code(), namespace)
            except RuntimeError as error:
                return calls, namespace, error
        return calls, namespace, None

    def test_missing_and_blank_environment_reject_before_sdk_creation(self):
        for value in [None, '', '   ', '\t\n']:
            with self.subTest(value=value):
                calls, _, error = self.run_configuration(value)
                self.assertEqual(calls, [])
                self.assertIsInstance(error, RuntimeError)
                self.assertIn('OPENAI_API_KEY', str(error))

    def test_explicit_environment_value_reaches_sdk_once(self):
        calls, namespace, error = self.run_configuration('offline-test-value')
        self.assertIsNone(error)
        self.assertEqual(calls, [{'api_key': 'offline-test-value'}])
        self.assertTrue(namespace['client'].configured)

    def test_source_has_no_embedded_provider_credential(self):
        embedded = [node for node in ast.walk(TREE)
                    if isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and node.value.startswith('sk-')]
        self.assertEqual(len(embedded), 0, 'Credential-shaped source literal remains')


class ResponseTests(unittest.TestCase):
    def response_function(self, history=None, fail=False):
        calls = []
        def create(**kwargs):
            calls.append(kwargs)
            if fail:
                raise RuntimeError('offline SDK failure')
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='  Test reply  '))])
        namespace = {'conversation_history': list(history or []),
                     'client': SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))}
        node = next(node for node in TREE.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'get_ai_response')
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), namespace)
        return namespace, calls

    def test_normalized_message_and_existing_api_contract(self):
        namespace, calls = self.response_function()
        self.assertEqual(namespace['get_ai_response']('  HELLO  '), 'Test reply')
        self.assertEqual(calls, [{'model': 'gpt-3.5-turbo',
                                 'messages': [{'role': 'user', 'content': 'hello'}],
                                 'max_tokens': 100, 'temperature': 0.7}])
        self.assertEqual(namespace['conversation_history'], ['hello', 'Test reply'])

    def test_context_is_preserved_and_history_is_bounded(self):
        history = ['first', 'reply one', 'second', 'reply two']
        namespace, calls = self.response_function(history)
        namespace['get_ai_response']('THIRD')
        self.assertEqual(calls[0]['messages'][:4], [
            {'role': 'user', 'content': 'first'}, {'role': 'assistant', 'content': 'reply one'},
            {'role': 'user', 'content': 'second'}, {'role': 'assistant', 'content': 'reply two'}])
        self.assertEqual(namespace['conversation_history'], ['second', 'reply two', 'third', 'Test reply'])

    def test_sdk_failure_keeps_existing_fallback_and_history(self):
        history = ['first', 'reply one']
        namespace, _ = self.response_function(history, fail=True)
        with contextlib.redirect_stdout(io.StringIO()):
            result = namespace['get_ai_response']('new question')
        self.assertEqual(result, 'Hello! How can I help you today?')
        self.assertEqual(namespace['conversation_history'], history)


if __name__ == '__main__':
    unittest.main()
