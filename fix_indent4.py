with open(r'D:\12th Student Data Collection Website\app\routers\admin_pdf.py', 'r') as f:
    lines = f.readlines()

# Fix line 70 (index 69): should be 4 spaces
lines[69] = '    \n'

# Fix line 72 (index 71): should be 4 spaces
lines[71] = '    \n'

# Fix line 73 (index 72): should be 4 spaces
lines[72] = '    student_doc = await database.students.find_one({"_id": ObjectId(student_id)})\n'

# Fix line 79 (index 78): should be 0 spaces
lines[78] = '\n'

# Fix line 82 (index 81): should be 4 spaces
lines[81] = '    \n'

# Fix line 84 (index 83): should be 4 spaces
lines[83] = '    \n'

with open(r'D:\12th Student Data Collection Website\app\routers\admin_pdf.py', 'w') as f:
    f.writelines(lines)

print('Fixed indentation in admin_pdf.py')