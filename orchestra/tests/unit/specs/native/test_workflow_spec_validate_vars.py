# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specwhenic language governing permissions and
# limitations under the License.

from orchestra.tests.unit.specs.native import base


class WorkflowSpecVarsValidationTest(base.OrchestraWorkflowSpecTest):

    def test_bad_vars_yaql(self):
        wf_def = """
            version: 1.0
            description: A basic sequential workflow.
            input:
              - y
            vars:
              foo: <% $.a %>
              fooa: <% $.x + $.y + $.z %>
            tasks:
              task1:
                action: std.noop
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'yaql',
                    'expression': '<% $.a %>',
                    'message': 'Variable "a" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.x + $.y + $.z %>',
                    'message': 'Variable "x" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.x + $.y + $.z %>',
                    'message': 'Variable "z" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_bad_vars_jinja(self):
        wf_def = """
            version: 1.0
            description: A basic sequential workflow.
            input:
              - y
            vars:
              foo: "{{ _.a }}"
              fooa: "{{ _.x + _.y + _.z }}"
            tasks:
              task1:
                action: std.noop
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'jinja',
                    'expression': '{{ _.a }}',
                    'message': 'Variable "a" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                },
                {
                    'type': 'jinja',
                    'expression': '{{ _.x + _.y + _.z }}',
                    'message': 'Variable "x" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                },
                {
                    'type': 'jinja',
                    'expression': '{{ _.x + _.y + _.z }}',
                    'message': 'Variable "z" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_bad_vars_mix_yaql_and_jinja(self):
        wf_def = """
            version: 1.0
            description: A basic sequential workflow.
            input:
              - y
            vars:
              foo: "{{ _.a }}"
              fooa: <% $.x + $.y + $.z %>
            tasks:
              task1:
                action: std.noop
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'jinja',
                    'expression': '{{ _.a }}',
                    'message': 'Variable "a" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.x + $.y + $.z %>',
                    'message': 'Variable "x" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.x + $.y + $.z %>',
                    'message': 'Variable "z" is referenced before assignment.',
                    'schema_path': 'properties.vars',
                    'spec_path': 'vars'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_bad_vars_in_sequential_tasks(self):
        wf_def = """
            version: 1.0
            description: A basic sequential workflow.
            vars:
              foobar: foobar
            tasks:
              task1:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task1) = "SUCCESS" %>
                    do: task2
              task2:
                action: std.echo
                input:
                  message: <% $.foo %>
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'yaql',
                    'expression': '<% $.foo %>',
                    'message': (
                        'Variable "foo" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task2.properties.input'
                    ),
                    'spec_path': 'tasks.task2.input'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_bad_vars_in_branches(self):
        wf_def = """
            version: 1.0
            description: A basic sequential workflow.
            vars:
              foobar: foobar
            tasks:
              task1:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task1) = "SUCCESS" %>
                    publish: foo="bar"
                    do: task2
                  - when: <% task_state(task1) = "ERROR" %>
                    publish: bar="foo"
                    do: task3
              task2:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
              task3:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'yaql',
                    'expression': '<% $.foo + $.bar %>',
                    'message': (
                        'Variable "bar" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task2.properties.input'
                    ),
                    'spec_path': 'tasks.task2.input'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.foo + $.bar %>',
                    'message': (
                        'Variable "foo" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task3.properties.input'
                    ),
                    'spec_path': 'tasks.task3.input'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_bad_vars_in_parallels(self):
        wf_def = """
            version: 1.0
            description: A basic sequential workflow.
            vars:
              foobar: foobar
            tasks:
              task1:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task1) = "SUCCESS" %>
                    publish: foo="bar"
                    do: task2
              task2:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
              task3:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task3) = "SUCCESS" %>
                    publish: bar="foo"
                    do: task4
              task4:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'yaql',
                    'expression': '<% $.foo + $.bar %>',
                    'message': (
                        'Variable "bar" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task2.properties.input'
                    ),
                    'spec_path': 'tasks.task2.input'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.foo + $.bar %>',
                    'message': (
                        'Variable "foo" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task4.properties.input'
                    ),
                    'spec_path': 'tasks.task4.input'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_bad_vars_in_reusable_split_tasks(self):
        wf_def = """
            version: 1.0
            description: A basic sequential workflow.
            vars:
              foobar: foobar
            tasks:
              task1:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task1) = "SUCCESS" %>
                    publish: foo="bar"
                    do: task2
              task2:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
                next:
                  - when: <% task_state(task2) = "SUCCESS" %>
                    do: task5
              task3:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task3) = "SUCCESS" %>
                    publish: bar="foo"
                    do: task4
              task4:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
                next:
                  - when: <% task_state(task4) = "SUCCESS" %>
                    do: task5
              task5:
                action: std.echo
                input:
                  message: <% $.foo %>
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'yaql',
                    'expression': '<% $.foo + $.bar %>',
                    'message': (
                        'Variable "bar" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task2.properties.input'
                    ),
                    'spec_path': 'tasks.task2.input'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.foo + $.bar %>',
                    'message': (
                        'Variable "foo" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task4.properties.input'
                    ),
                    'spec_path': 'tasks.task4.input'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.foo %>',
                    'message': (
                        'Variable "foo" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task5.properties.input'
                    ),
                    'spec_path': 'tasks.task5.input'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_vars_in_join_task(self):
        wf_def = """
            version: 1.0
            description: A complex branching workflow.
            vars:
              foobar: foobar
            tasks:
              task1:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task1) = "SUCCESS" %>
                    publish: foo="bar"
                    do: task2
              task2:
                action: std.echo
                input:
                  message: <% $.foo %>
                next:
                  - when: <% task_state(task2) = "SUCCESS" %>
                    do: task5
              task3:
                action: std.echo
                input:
                  message: <% $.foobar %>
                next:
                  - when: <% task_state(task3) = "SUCCESS" %>
                    publish: bar="foo"
                    do: task4
              task4:
                action: std.echo
                input:
                  message: <% $.bar %>
                next:
                  - when: <% task_state(task4) = "SUCCESS" %>
                    do: task5
              task5:
                join: all
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
        """

        wf_spec = self.instantiate(wf_def)

        self.assertDictEqual(wf_spec.validate(), dict())

    def test_bad_vars_in_publish(self):
        wf_def = """
            version: 1.0
            description: A basic workflow.
            tasks:
              task1:
                action: std.noop
                next:
                  - publish: foo="bar" bar="foo"
                    do: task2
              task2:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
                next:
                  - publish: foobar=<% $.fu + $.bar %>
                    do: task3
              task3:
                action: std.echo
                input:
                  message: <% $.fu + $.bar %>
                next:
                  - publish: foobar=<% $.fu + $.bar %>
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'yaql',
                    'expression': '<% $.fu + $.bar %>',
                    'message': (
                        'Variable "fu" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task2.properties.'
                        'next.items.properties.publish'
                    ),
                    'spec_path': 'tasks.task2.next[0].publish'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.fu + $.bar %>',
                    'message': (
                        'Variable "fu" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task3.properties.input'
                    ),
                    'spec_path': 'tasks.task3.input'
                },
                {
                    'type': 'yaql',
                    'expression': '<% $.fu + $.bar %>',
                    'message': (
                        'Variable "fu" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task3.properties.'
                        'next.items.properties.publish'
                    ),
                    'spec_path': 'tasks.task3.next[0].publish'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)

    def test_publish_inline_params(self):
        wf_def = """
            version: 1.0
            description: A basic workflow.
            tasks:
              task1:
                action: std.noop
                next:
                  - publish: foo="bar" bar="foo"
                    do: task2, task3
              task2:
                action: std.echo
                input:
                  message: <% $.foo + $.bar %>
              task3:
                action: std.echo
                input:
                  message: <% $.fu + $.bar %>
        """

        wf_spec = self.instantiate(wf_def)

        expected_errors = {
            'context': [
                {
                    'type': 'yaql',
                    'expression': '<% $.fu + $.bar %>',
                    'message': (
                        'Variable "fu" is referenced before assignment.'
                    ),
                    'schema_path': (
                        'properties.tasks.properties.task3.properties.input'
                    ),
                    'spec_path': 'tasks.task3.input'
                }
            ]
        }

        self.assertDictEqual(wf_spec.validate(), expected_errors)