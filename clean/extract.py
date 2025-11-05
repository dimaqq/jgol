import re
re.search(r' (?P<time>\d{2}:\d{2}:\d{2}) .* (?P<board>\[[01]{36}\])', lines[-10])
