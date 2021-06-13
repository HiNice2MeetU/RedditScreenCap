from colorama import Fore, Style


def Good(Msg):
	print(Fore.GREEN + "✓ " + Msg)
	print(Style.RESET_ALL, end="")
	#print("✓ " + Msg)

def Bad(Msg):
	print(Fore.RED + "✘ " + Msg)
	print(Style.RESET_ALL, end="")
	#print("✘ " + Msg)

def Info(Msg):
	print(Fore.YELLOW + "i " + Msg)
	print(Style.RESET_ALL, end="")
	#print("i " + Msg)

