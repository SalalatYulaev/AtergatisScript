import os
import sys
import subprocess
from datetime import datetime
from shutil import copyfile, rmtree
from zipfile import ZipFile



release_file = "stable.zip"
test_file = "test.zip"
log_dir = "logs\\"
log_file = "logs\\deploy.log"
scripts_path = "scripts\\"
new_scripts_path = "AtergatisScript\\scripts\\"
templates_dir = "AtergatisScript\\scripts\\templates\\"
init_script = "scripts\\init.py"



def _check_dirs():
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
		deploy_log("Created logs dir")
	else:
		deploy_log("Logs dir exists")
	if not os.path.exists(scripts_path):
		os.makedirs(scripts_path)
		deploy_log("Created scripts dir")
	else:
		deploy_log("Scripts dir exists")


def _check_release_file():
	if not os.path.exists(release_file):
		deploy_log("Release file not exists, searching for test file")
		if not os.path.exists(test_file):
			deploy_log("Release and test files are not exests! Starting update directory.", level='ALARM')
			return False
		else:
			deploy_log("Test build file was found")
			return True
	else:
		deploy_log("Stable build file was found")
		return True


def deploy_log(data, level='INFO'):
	timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S")
	with open(log_file, 'a') as f:
		f.write("{:22}{:8}{}\n".format(timestamp, level, str(data)))


def _unzip():
	deploy_log("Unzipping scripts")
	if os.path.exists(release_file):
		with ZipFile(release_file) as zf:
			zf.extractall()
			deploy_log("Stable build unzipped")
	else:
		if os.path.exists(test_file):
			with ZipFile(test_file) as zf:
				zf.extractall()
				deploy_log("Test build unzipped")


def _copy_templates():
	deploy_log("Starting copying templates")
	template_files = os.listdir(templates_dir)
	for file in template_files:
		if not file in os.listdir():
			deploy_log(f"{file} not found. Copying")
			copyfile(templates_dir + file, file)
		else:
			deploy_log(f"{file} exists")
	deploy_log("Templates copied. Removing templates dir.")
	rmtree("AtergatisScript\\scripts\\templates")


def _copy_scripts():
	deploy_log("Starting copying scripts")
	for file in os.listdir(new_scripts_path):
		copyfile(new_scripts_path + file, scripts_path + file)
	deploy_log("Scripts copied. Removing temp scripts dir")
	rmtree("AtergatisScript")


def _execute_init():
	if not os.path.exists(init_script):
		deploy_log("Init script NOT found, aborting")
		print("Init script NOT found, aborting")
	else:
		deploy_log("Executing init.py")
		subprocess.Popen([sys.executable, init_script])


def full_deploy():
	deploy_log("Full deploy started")
	_unzip()
	_copy_templates()	
	_copy_scripts()
	_execute_init()


def update_files():
	deploy_log("Upgrade files started")
	_execute_init()


def deploy():
	_check_dirs()
	if _check_release_file():
		full_deploy()
	else:
		update_files()
	deploy_log("=" * 30)
	


if __name__ == '__main__':
	deploy()