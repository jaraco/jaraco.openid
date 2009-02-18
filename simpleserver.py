#!/usr/bin/env python

import sys
import os

def setup_iis_environment():
	#if hasattr(sys, 'isapidllhandle'):
	#	import win32traceutil
	global appdir
	appdir = os.path.dirname(__file__)
	egg_cache = os.path.join(appdir, 'egg-tmp')
	if not os.path.exists(egg_cache):
		os.makedirs(egg_cache)
	os.environ['PYTHON_EGG_CACHE'] = egg_cache
	sys.path.insert(0, "C:\\Python\\DLLs")
	#os.chdir(appdir)

setup_iis_environment()

class OpenIDApp(object):
	def __init__(self):
		from openid.server.server import Server
		from openid.store.memstore import MemoryStore
		store = MemoryStore()
		self.server = Server(store, 'http://www.jaraco.com/')

	def __call__(self, environ, start_response):
		"""
		The WSGI App - verifies the identity against the requested identity
		"""
		start_response("200 OK", [('Content-Type', 'text/html')])
		return ["foo"]
		query = dict(urlparse.parse_qsl(environ['QUERY_STRING']))
		request = self.server.decodeRequest(query)
		if not request:
			path_info = environ['PATH_INFO']
			if path_info:
				username = path_info.rsplit('/', 1)[-1]
				start_response("200 OK", [('Content-Type', 'text/html')])
				provider = 'http://drake.jaraco.com/isapi-openid'
				local_id = '%(provider)s/%(username)s' % vars()
				return ["""<HTML><HEAD><LINK rel="openid2.provider" href="%(provider)s"><LINK rel="openid2.local_id" href="%(local_id)s"></HEAD><BODY>Id for %(username)s</BODY></HTML>""" % vars()]
			else:
				start_response("401 Unauthorized")
				return [""]
		id_requested = request.identity.rsplit('/', 1)[-1]
		# assume the user has already authenticated using basic auth
		id_authenticated = environ['REMOTE_USER'].rsplit('\\', 1)[-1]
		matched = id_requested and id_requested == id_authenticated
		response = request.answer(matched)
		start_response("303 found", [('Location', response.encodeToURL())])
		return ['']

def demo_app(environ,start_response):
	"""Demo app from wsgiref"""
	from StringIO import StringIO
	stdout = StringIO()
	print >>stdout, "Hello world!"
	print >>stdout
	h = environ.items(); h.sort()
	for k,v in h:
		print >>stdout, k,'=',`v`
	start_response("200 OK", [('Content-Type','text/plain')])
	return [stdout.getvalue()]


import isapi_wsgi
# The entry points for the ISAPI extension.
def __ExtensionFactory__():
	import traceback
	try:
		#return isapi_wsgi.ISAPISimpleHandler(demo_app)
		import win32api
		win32api.LoadLibrary("C:\\Python\\DLLs\\_hashlib.dll")
		return isapi_wsgi.ISAPISimpleHandler(OpenIDApp())
	except:
		f = open(os.path.join(appdir, 'critical error.txt'), 'w')
		f.write(str(os.listdir('c:\\Python\\DLLs'))+'\n')
		f.write(str(sys.path)+'\n')
		traceback.print_exc(file=f)
		f.close()

def manage_isapi():
	# If run from the command-line, install ourselves.
	from isapi.install import ISAPIParameters, ScriptMapParams, VirtualDirParameters, HandleCommandLine
	params = ISAPIParameters()
	# Setup the virtual directories - this is a list of directories our
	# extension uses - in this case only 1.
	# Each extension has a "script map" - this is the mapping of ISAPI
	# extensions.
	sm = [
		ScriptMapParams(Extension="*", Flags=0)
	]
	vd = VirtualDirParameters(Name="isapi-openid",
							  Description = "ISAPI-WSGI OpenID Provider",
							  ScriptMaps = sm,
							  ScriptMapUpdate = "replace"
							  )
	params.VirtualDirs = [vd]
	HandleCommandLine(params)

if __name__=='__main__':
	pass
	manage_isapi()

