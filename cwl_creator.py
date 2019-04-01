# Copyright 2019 Alessandro Pio Greco, Patrick Hedley-Miller, Filipe Jesus, Zeyu Yang

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
from configparser import ConfigParser

import classes

if __name__ == "__main__":
	# change current working directory to project root
	root = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..' ))
	os.chdir(root)

	# read config file
	config = ConfigParser()
	config.read("config.ini")
	database = config.get("main", "database")

	test = classes.database_checker(database)
	test.check_and_run(root)
