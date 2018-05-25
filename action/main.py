from Kamisu66 import EthicsCommittee
import traceback

def main_action(data):
	try:
		pass
	except Exception as e:
		traceback.print_exc()
		EC = EthicsCommittee("error", "error")
		EC.log(traceback.format_exc())
