from Kamisu66 import EthicsCommittee
import traceback
import importlib
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

def main_action(data):
	EC = EthicsCommittee("error", "error")
	try:
		try:
			from action.main_config import module_list
		except ImportError as e:
			if str(e) == "No module named 'action.main_config'":
				return
			if str(e) == "cannot import name 'module_list'":
				return
			raise e
		if not isinstance(module_list, list):
			EC.log("module_list is not a list")
		for module_name in module_list:
			if not isinstance(module_name, str):
				EC.log("module_name '{}' is not a str".format(str(module_name)))
			try:
				module = importlib.import_module("."+module_name, "action")
				module.main(data)
			except ImportError as e:
				EC.log("module '{}' does not exist".format(module_name))
			except AttributeError as e:
				if str(e) == "'module' object has no attribute 'main'":
					EC.log("modue '{}' does not contain main function".format(module_name))
	except Exception as e:
		traceback.print_exc()
		EC.log(traceback.format_exc())
