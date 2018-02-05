#!/usr/bin/env python

# Runs a subsetting test suite. Compares the results of subsetting via harfbuz
# to subsetting via fonttools.

from __future__ import print_function

import io
import os
import subprocess
import sys
import tempfile

from subset_test_suite import SubsetTestSuite


def cmd(command):
	p = subprocess.Popen (
		command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait ()
	print (p.stderr.read (), end="") # file=sys.stderr
	return p.stdout.read (), p.returncode

def read_binary(file_path):
	with open(file_path, 'rb') as f:
		return f.read()

def fail_test(test, cli_args, message):
	print ('ERROR: %s' % message)
	print ('Test State:')
	print ('  test.font_path    %s' % os.path.abspath(test.font_path))
	print ('  test.profile_path %s' % os.path.abspath(test.profile_path))
	print ('  test.unicodes	    %s' % test.unicodes())
	expected_file = os.path.join(test_suite.get_output_directory(),
				     test.get_font_name())
	print ('  expected_file	    %s' % os.path.abspath(expected_file))
	return 1

def run_test(test):
	out_file = os.path.join(tempfile.mkdtemp(), test.get_font_name() + '-subset.ttf')
	cli_args = [hb_subset,
		    "--font-file=" + test.font_path,
		    "--output-file=" + out_file,
		    "--unicodes=%s" % test.unicodes()]
	_, return_code = cmd(cli_args)

	if return_code:
		return fail_test(test, cli_args, "%s returned %d" % (' '.join(cli_args), return_code))

	expected = read_binary(os.path.join(test_suite.get_output_directory(),
					    test.get_font_name()))
	actual = read_binary(out_file)

	if len(actual) != len(expected):
		return fail_test(test, cli_args, "expected %d bytes, actual %d: %s" % (
				len(expected), len(actual), ' '.join(cli_args)))

	if not actual == expected:
		return fail_test(test, cli_args, 'files are the same length but not the same bytes')

	return 0


args = sys.argv[1:]
if not args or sys.argv[1].find('hb-subset') == -1 or not os.path.exists (sys.argv[1]):
	print ("First argument does not seem to point to usable hb-subset.")
	sys.exit (1)
hb_subset, args = args[0], args[1:]

if not len(args):
	print ("No tests supplied.")
	sys.exit (1)

fails = 0
for path in args:
	with io.open(path, mode="r", encoding="utf-8") as f:
		print ("Running tests in " + path)
		test_suite = SubsetTestSuite(path, f.read())
		for test in test_suite.tests():
			fails += run_test(test)

if fails != 0:
	print (str (fails) + " test(s) failed.")
	sys.exit(1)
else:
	print ("All tests passed.")
