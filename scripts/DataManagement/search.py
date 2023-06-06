import os

# Script to search for a certain file

def search(filename, directory = None):
	if directory == None:
		directory = os.getcwd()

	for content in os.listdir(directory):
		try:
			if os.path.isdir(directory + '/' + content) == True:
				results = search(filename, directory + '/' + content)
				if results == True:
					return results
			else:
				if content == filename:
					print(directory + '/' + filename)
					return True
		except:
			continue
	return False
