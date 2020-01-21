
import subprocess

f = open('days.txt', 'r')
content = f.read()
# f.close()

lines = content.split('\n')
for line in lines[320:]:
    subprocess.Popen(["python", "import list.py", line])