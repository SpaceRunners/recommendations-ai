# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""
import os
import re

import synthtool as s
import synthtool.gcp as gcp
from synthtool.languages import python

common = gcp.CommonTemplates()

default_version = "v1beta1"

for library in s.get_staging_dirs(default_version):
    # rename library to recommendations ai, to be consistent with product branding
    s.replace(
        [library / "google/**/*.py", library / "tests/**/*.py"],
        "google-cloud-recommendationengine",
        "google-cloud-recommendations-ai",
    )

    # surround path with * with ``
    s.replace(library / "google/**/*.py", """"(projects/\*/.*)"\.""", "``\g<1>``")

    s.replace(
        library / "google/**/*client.py",
        '''"projects/\*/locations/global/catalogs/default_catalog/eventStores/default_event_store/predictionApiKeyRegistrations/\<YOUR_API_KEY\>"''',
        """``projects/*/locations/global/catalogs/default_catalog/eventStores/default_event_store/predictionApiKeyRegistrations/<YOUR_API_KEY>``"""
    )

    s.replace(
        library / "google/**/import_.py",
        "gs://bucket/directory/\*\.json",
        "``gs://bucket/directory/*.json``",
    )

    # Delete broken path helper 'catalog_item_path_path'
    # https://github.com/googleapis/gapic-generator-python/issues/701
    s.replace(
        library / "google/**/client.py",
        """\s+@staticmethod
\s+def catalog_item_path_path.*?
\s+return m\.groupdict\(\) if m else \{\}\n""",
        "",
        flags=re.MULTILINE | re.DOTALL,
    )

    s.replace(
        library / "google/**/async_client.py",
        """parse_catalog_item_path_path =.*?\)""",
        "",
        flags=re.MULTILINE | re.DOTALL,
    )

    s.replace(
        library / "google/**/async_client.py",
        """catalog_item_path_path =.*?\)""",
        "",
        flags=re.MULTILINE | re.DOTALL,
    )

    # Delete unit tests for 'catalog_item_path_path'
    s.replace(
        library / "tests/**/test_catalog_service.py",
        """def test_catalog_item_path_path.*?assert expected == actual""",
        "",
        flags=re.MULTILINE | re.DOTALL,
    )

    s.replace(
        library / "tests/**/test_catalog_service.py",
        """def test_parse_catalog_item_path_path.*?assert expected == actual""",
        "",
        flags=re.MULTILINE | re.DOTALL,
    )

    s.move(library, excludes=["setup.py", "docs/index.rst", "README.rst"])

s.remove_staging_dirs()
# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(cov_level=100, microgenerator=True)

s.move(
    templated_files, excludes=[".coveragerc"]
)  # the microgenerator has a good coveragerc file

python.py_samples(skip_readmes=True)

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
