with open(r'D:\12th Student Data Collection Website\app\routers\admin_students.py', 'r') as f:
    lines = f.readlines()

# Fix line 184 (index 183): should be 4 spaces
lines[183] = '    \n'

# Fix line 185 (index 184): should be 4 spaces
lines[184] = '    updated_student = await database.students.find_one({"_id": ObjectId(student_id)})\n'

# Fix line 188 (index 187): should be 0 spaces
lines[187] = '\n'

with open(r'D:\12th Student Data Collection Website\app\routers\admin_students.py', 'w') as f:
    f.writelines(lines)

print('Fixed indentation in admin_students.py part 2')