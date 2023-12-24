#!/usr/bin/env python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
Module to check integration tests are listed in documentation.

Compare the contents of the integrations table and the docker-compose
integration files, if there is a mismatch, the table is generated.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))  # make sure common_precommit_utils is imported
from typing import List

from common_precommit_utils import (
    AIRFLOW_BREEZE_SOURCES_PATH,
    AIRFLOW_SOURCES_ROOT_PATH,
    insert_documentation,
    console,
)
from tabulate import tabulate

DOCUMENTATION_PATH = AIRFLOW_BREEZE_SOURCES_PATH / "TESTING.rst"
INTEGRATION_TESTS_PATH = AIRFLOW_SOURCES_ROOT_PATH / "scripts" / "ci" / "docker-compose"
INTEGRATION_TEST_PREFIX = "integration-*.yml"

# 1. get list of ingetrations from INTEGRATION_TESTS_PATH
# 1. get list of integrations from DOCUMENTATION_PATH (relevant part?)
#       see: https://raw.githubusercontent.com/timonviola/airflow/main/STATIC_CODE_CHECKS.rst
#       table is generated and is surrounded by markers:
# '  .. BEGIN AUTO-GENERATED INTEGRATION LIST'
#
#'  .. END AUTO-GENERATED INTEGRATION LIST'
#
# warn if not the same


def get_integrations(
    tests_path: Path = INTEGRATION_TESTS_PATH, integration_prefix: str = INTEGRATION_TEST_PREFIX
) -> List[str]:
    """Get list of integrations from matching filenames."""
    if not tests_path.is_dir() and tests_path.exists():
        console.print(f"[red]Bad tests path: {tests_path}. [/]")
        sys.exit(1)

    integrations_files = [_i for _i in tests_path.glob(integration_prefix)]

    if len(integrations_files) == 0:
        console.print(
            f"[red]No integrations found."
            f"Pattern '{integration_prefix}' did not match any files under {tests_path}. [/]"
        )
        sys.exit(1)

    # parse into list of ids
    integrations = []
    for _i in integrations_files:
        try:
            integrations.append(_i.stem.split("-")[1])
        except IndexError:
            console.print(f"[red]Tried to parse {_i.stem}, but did not contain '-' separator. [/]")
            continue

    return integrations


def update_integration_tests_array(integrations: List[str]):
    rows = []
    description = ""
    for integration in sorted(integrations):
        # TODO: replace description
        rows.append((integration, description))
    formatted_table = "\n" + tabulate(rows, tablefmt="grid", headers=("Identifier", "Description")) + "\n\n"
    insert_documentation(
        file_path=AIRFLOW_SOURCES_ROOT_PATH / "TESTING.rst",
        content=formatted_table.splitlines(keepends=True),
        header="  .. BEGIN AUTO-GENERATED INTEGRATION LIST",
        footer="  .. END AUTO-GENERATED INTEGRATION LIST",
    )


def main():
    # parser = argparse.ArgumentParser()
    # TODO: any constraints on naming? e.g. number of '-' separators?
    # parser.add_argument("--max-length", help="Max length for hook names")
    # args = parser.parse_args()
    # See above todo
    # max_length = int(args.max_length or 70)
    integrations = get_integrations()
    if len(integrations) == 0:
        console.print(f"[red]No integrations found.[/]")
        sys.exit(1)

    update_integration_tests_array(integrations)

if __name__ == "__main__":
    main()
