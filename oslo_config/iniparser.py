# Copyright 2012 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from collections.abc import Iterable
from typing import NoReturn


class ParseError(Exception):
    def __init__(self, message: str, lineno: int, line: str) -> None:
        self.msg = message
        self.line = line
        self.lineno = lineno

    def __str__(self) -> str:
        return f'at line {self.lineno}, {self.msg}: {self.line!r}'


class BaseParser:
    lineno: int = 0
    parse_exc: type[ParseError] = ParseError

    def _assignment(
        self, key: str, value: list[str]
    ) -> tuple[None, list[str]]:
        self.assignment(key, value)
        return None, []

    def _get_section(self, line: str) -> str:
        if not line.endswith(']'):
            return self.error_no_section_end_bracket(line)
        if len(line) <= 2:
            return self.error_no_section_name(line)

        return line[1:-1]

    def _split_key_value(self, line: str) -> tuple[str, list[str]]:
        colon = line.find(':')
        equal = line.find('=')
        if colon < 0 and equal < 0:
            return self.error_invalid_assignment(line)

        if colon < 0 or (equal >= 0 and equal < colon):
            key, value = line[:equal], line[equal + 1 :]
        else:
            key, value = line[:colon], line[colon + 1 :]

        value = value.strip()
        if value and value[0] == value[-1] and value.startswith(("\"", "'")):
            value = value[1:-1]
        return key.strip(), [value]

    def parse(self, lineiter: Iterable[str]) -> None:
        key: str | None = None
        value: list[str] = []

        for line in lineiter:
            self.lineno += 1

            line = line.rstrip()
            if not line:
                # Blank line, ends multi-line values
                if key:
                    key, value = self._assignment(key, value)
                continue
            elif line.startswith((' ', '\t')):
                # Continuation of previous assignment
                if key is None:
                    self.error_unexpected_continuation(line)
                else:
                    value.append(line.lstrip())
                continue

            if key:
                # Flush previous assignment, if any
                key, value = self._assignment(key, value)

            if line.startswith('['):
                # Section start
                section = self._get_section(line)
                if section:
                    self.new_section(section)
            elif line.startswith(('#', ';')):
                self.comment(line[1:].lstrip())
            else:
                key, value = self._split_key_value(line)
                if not key:
                    self.error_empty_key(line)

        if key:
            # Flush previous assignment, if any
            self._assignment(key, value)

    def assignment(self, key: str, value: list[str]) -> None:
        """Called when a full assignment is parsed."""
        raise NotImplementedError()

    def new_section(self, section: str) -> None:
        """Called when a new section is started."""
        raise NotImplementedError()

    def comment(self, comment: str) -> None:
        """Called when a comment is parsed."""
        pass

    def error_invalid_assignment(self, line: str) -> NoReturn:
        raise self.parse_exc(
            "No ':' or '=' found in assignment", self.lineno, line
        )

    def error_empty_key(self, line: str) -> NoReturn:
        raise self.parse_exc('Key cannot be empty', self.lineno, line)

    def error_unexpected_continuation(self, line: str) -> NoReturn:
        raise self.parse_exc('Unexpected continuation line', self.lineno, line)

    def error_no_section_end_bracket(self, line: str) -> NoReturn:
        raise self.parse_exc(
            'Invalid section (must end with ])', self.lineno, line
        )

    def error_no_section_name(self, line: str) -> NoReturn:
        raise self.parse_exc('Empty section name', self.lineno, line)
