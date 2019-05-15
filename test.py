import re
regex = r'\d{17}(x|X)'
print re.findall(regex, '64020319990104005X')