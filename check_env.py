import sys, pkgutil
print('python version', sys.version)
print('has pytest', pkgutil.find_loader('pytest') is not None)
print('has httpx', pkgutil.find_loader('httpx') is not None)
