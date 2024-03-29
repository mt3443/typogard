import time
import requests
import datetime
import sys

node_name = sys.argv[1]

lines = open('/volatile/m139t745/rubygems/input/{}'.format(node_name)).read().splitlines()
output = open('/volatile/m139t745/rubygems/output/{}'.format(node_name), 'a')

today = datetime.datetime.today()

for line in lines:
	package = line.split()[0]
	version = line.split()[1].replace('(', '').replace(')', '')

	r = requests.get('https://rubygems.org/api/v1/downloads/{}-{}.json'.format(package, version))

	if r.status_code != 200:
		print('ERROR: STATUS CODE {} RETURNED FOR PACKAGE {} DOWNLOAD COUNT'.format(r.status_code, package))
	else:
		downloads = r.json()['total_downloads']

		time.sleep(0.1)
		# get package age
		r = requests.get('https://rubygems.org/api/v1/versions/{}.json'.format(package))

		if r.status_code != 200:
			print('ERROR: STATUS CODE {} RETURNED FOR PACKAGE {} AGE'.format(r.status_code, package))
		else:

			start_date = r.json()[-1]['built_at']
			year = int(start_date[:4])
			month = int(start_date[5:7])
			day = int(start_date[8:10])

			birthday = datetime.datetime(year, month, day, 0, 0, 0)

			weeks_since = int((today - birthday).days / 7)
			if weeks_since == 0:
				downloads_per_week = int(downloads)
			else:
				downloads_per_week = int(int(downloads) / weeks_since)

			output.write('{},{}\n'.format(package, downloads_per_week))
			output.flush()

	time.sleep(0.1)

output.close()