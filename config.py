# Copyright 2015 Google Inc.
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

"""
This file contains all of the configuration values for the application.
Update this file with the values for your specific Google Cloud project.
You can create and manage projects at https://console.developers.google.com
"""

import os

# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = 'secret'

# Use datastore to store the data in the application.
DATA_BACKEND = 'datastore'

# Google Cloud Project ID.
PROJECT_ID = 't-science-106105'

# Google Cloud Storage and upload settings.
CLOUD_STORAGE_BUCKET = 't-science-106105'
MAX_CONTENT_LENGTH = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['csv', 'pb', 'txt'])
