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

"""fprime-to-xtce package."""

try:
    # Grab the version from the scm-generated file
    from fprime_xtce._version import __version__
except ImportError:
    try:
        # Fallback to the PIP reported version
        from importlib.metadata import version
        __version__ = version("fprime-to-xtce")
    except Exception:
        # Final fallback: no version info available
        __version__ = "0.0.0.dev0"