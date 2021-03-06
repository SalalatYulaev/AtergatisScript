import os
import sys
import subprocess
import yaml
from datetime import datetime
from shutil import copyfile, rmtree
from zipfile import ZipFile



release_file = "stable.zip"
test_file = "test.zip"
log_dir = "logs\\"
log_file = "logs\\deploy.log"
deploy_info_file = "deploy_list.yml"
scripts_path = "scripts\\"
new_scripts_path = "AtergatisScript\\scripts\\"
templates_dir = "AtergatisScript\\scripts\\templates\\"
init_script = "scripts\\init.py"
mon_dir = "monitoring\\"



def deploy_log(data, level='INFO'):
	timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S")
	with open(log_file, 'a') as f:
		f.write("{:22}{:8}{}\n".format(timestamp, level, str(data)))


def _check_dirs():
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
		deploy_log("Created logs dir")
	else:
		deploy_log("Logs dir exists")
	if not os.path.exists(mon_dir):
		os.makedirs(mon_dir)
		deploy_log("Created temp dir")
	else:
		deploy_log("Logs dir exists")
	if not os.path.exists(scripts_path):
		os.makedirs(scripts_path)
		deploy_log("Created scripts dir")
	else:
		deploy_log("Scripts dir exists")


def _check_release_file():
	deploy_log("Checking release file")
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


def _check_deploy_list_file():
	deploy_log("Checking deploy_list file")
	with open(deploy_info_file) as f:
		data = yaml.safe_load(f)
	deployment = data['deployment'].lower()
	scripts = data['update_scripts']
	deploy_log(f"Deployment: {deployment}")
	return deployment, scripts


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
	deploy_log("Copying templates")
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
	deploy_log("Copying scripts")
	for file in os.listdir(new_scripts_path):
		deploy_log(f"Copying {file}")
		copyfile(new_scripts_path + file, scripts_path + file)
	deploy_log("Scripts copied. Removing temp scripts dir")
	rmtree("AtergatisScript")


def _copy_custom_scripts(scripts):
	deploy_log("Copying custom scripts")
	for entry in scripts:
		for script, boo in entry.items():
			if boo:
				deploy_log(f"Copying {script}")
				copyfile(new_scripts_path + script, scripts_path + script)
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


def custom_deploy(scripts):
	deploy_log("Partial deploy started")
	_unzip()
	_copy_templates()
	_copy_custom_scripts(scripts)
	_execute_init()	


def update_files():
	deploy_log("Upgrade files started")
	_execute_init()


def deploy():
	_check_dirs()
	if _check_release_file():
		try:
			deploy, scripts = _check_deploy_list_file()
			if deploy == "full":
				full_deploy()
			if deploy == "custom":
				custom_deploy(scripts)
		except Exception as err:
			deploy_log(f"Error: {str(err)}")
			full_deploy()
	else:
		update_files()
	deploy_log("=" * 30)
	


if __name__ == '__main__':
	deploy()