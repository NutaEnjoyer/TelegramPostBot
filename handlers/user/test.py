import pytz


def parse_time(data):
	from datetime import datetime

	currentSecond = datetime.now().second
	currentMinute = datetime.now().minute
	currentHour = datetime.now().hour
	currentDay = datetime.now().day
	currentMonth = datetime.now().month
	currentYear = datetime.now().year

	spl = data.split()
	if len(spl) > 2:
		return

	if len(spl) == 2:
		time = spl[0]
		date = spl[1]
		spl = time.split(':')
		if len(spl) > 2: return

		if len(spl) == 2:
			hour = spl[0]
			minut = spl[1]

		else:
			hour = spl[0][:-2]
			minut = spl[0][-2:]

		if not (hour.isdigit() and minut.isdigit()): return

		hour = int(hour)
		minut = int(minut)

		if not (hour >= 0 and hour < 24 and minut >= 0 and minut < 60): return

		spl = date.split('.')
		if len(spl) > 2: return

		if len(spl) == 2:
			day = spl[0]
			month = spl[1]

		else:
			day = spl[0][:-2]
			month = spl[0][-2:]

		if not (day.isdigit() and month.isdigit()): return

		day = int(day)
		month = int(month)

		if not (day >= 0 and day < 32 and month >= 0 and month < 13): return

	else:
		time = spl[0]
		date = spl[1]
		spl = time.split(':')
		if len(spl) > 2: return

		if len(spl) == 2:
			hour = spl[0]
			minut = spl[1]

		else:
			hour = spl[0][:-2]
			minut = spl[0][-2:]

		if not (hour.isdigit() and minut.isdigit()): return

		hour = int(hour)
		minut = int(minut)

		day = currentDay
		month = currentMonth

	post_date = datetime(year=currentYear, month=month, day=day, hour=hour, minute=minut)
	now_date = datetime.now(tz=pytz.timezone("Asia/Qatar"))
	now_date = now_date.replace(tzinfo=None)
	if post_date < now_date:
		return

	delta = post_date - now_date

	return {
		'human_date': post_date.strftime("%H:%M %d.%m"),
		'seconds': delta.seconds
	}

mes = '1648 1606'


print(parse_time(mes))

