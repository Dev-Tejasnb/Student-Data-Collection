with open(r'D:\12th Student Data Collection Website\app\routers\admin_students.py', 'r') as f:
    lines = f.readlines()

# Fix line 120 (index 119): should be 4 spaces
lines[119] = '    \n'

# Fix line 122 (index 121): should be 4 spaces
lines[121] = '    \n'

# Fix line 123 (index 122): should be 4 spaces
lines[122] = '    student_doc = await database.students.find_one({"_id": ObjectId(student_id)})\n'

# Fix line 129 (index 128): should be 0 spaces
lines[128] = '\n'

with open(r'D:\12th Student Data Collection Website\app\routers\admin_students.py', 'w') as f:
    f.writelines(lines)

print('Fixed indentation in admin_students.py')