with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        # Enforce stream & combination filtering on enrollments
        if is_pu:
            if stream:
                where_clauses.append("(e.stream = ? OR e.stream IS NULL)")
                # When combination is specifically chosen, filter by subject_combination
                if combination:
                    where_clauses.append("e.subject_combination = ?")
                    params.append(combination)'''

replacement = '''        # Enforce stream & combination filtering on enrollments
        if is_pu:
            if stream:
                where_clauses.append("(e.stream = ? OR e.stream IS NULL)")
                params.append(stream)
                # When combination is specifically chosen, filter by subject_combination
                if combination:
                    where_clauses.append("e.subject_combination = ?")
                    params.append(combination)'''

assert target in content, 'target not found'
content = content.replace(target, replacement, 1)

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Successfully fixed params binding in backend/main.py')
