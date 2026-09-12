with open(r'D:\12th Student Data Collection Website\app\routers\auth.py', 'r') as f:
    lines = f.readlines()

# Fix line 152 (index 151): should be 4 spaces, not 5
lines[151] = '    \n'

# Fix line 153 (index 152): should be 4 spaces
lines[152] = '    if user_data.role != existing_user.get("role", "staff"):\n'

# Fix line 155 (index 154): should be 0 spaces (empty line)
lines[154] = '\n'

with open(r'D:\12th Student Data Collection Website\app\routers\auth.py', 'w') as f:
    f.writelines(lines)

print('Fixed indentation')