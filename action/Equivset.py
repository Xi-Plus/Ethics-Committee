import os
import subprocess
import locale


def Equivset(string):
	path = os.path.dirname(os.path.realpath(__file__))
	ps = subprocess.Popen(['php', '{}/Equivset.php'.format(path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	res = ps.communicate(string.encode())[0].decode()
	return res
