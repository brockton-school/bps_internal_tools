import sqlite3

DB_PATH = '/app/data/canvas.db'

def search_teacher_by_name(query, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DISTINCT u.user_id, u.full_name
        FROM users u
        JOIN enrollments e ON u.user_id = e.user_id
        WHERE e.role = 'teacher'
          AND e.course_id GLOB 'c[0-9]*'
          AND LOWER(u.full_name) LIKE LOWER(?)
    ''', (f'%{query}%',))

    results = cursor.fetchall()
    conn.close()

    return [{'user_id': user_id, 'full_name': full_name} for user_id, full_name in results]

def get_courses_for_user(user_id, role=None, terms=None, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT DISTINCT c.course_id, c.short_name, c.long_name
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.user_id = ?
          AND e.course_id GLOB 'c[0-9]*'
    '''
    params = [user_id]

    # Add role filter
    if role:
        query += ' AND e.role = ?'
        params.append(role)

    # Add term_id filter
    if terms:
        # Dynamically generate placeholders like (?, ?, ?) for term filtering
        placeholders = ', '.join(['?'] * len(terms))
        query += f' AND c.term_id IN ({placeholders})'
        params.extend(terms)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [
        {
            'course_id': course_id,
            'short_name': short_name,
            'long_name': long_name
        }
        for course_id, short_name, long_name in results
    ]


def get_students_in_course(course_id, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DISTINCT u.user_id, u.full_name
        FROM enrollments e
        JOIN users u ON e.user_id = u.user_id
        WHERE e.course_id = ?
          AND e.role = 'student'
    ''', (course_id,))

    results = cursor.fetchall()
    conn.close()

    return [{'user_id': user_id, 'full_name': full_name} for user_id, full_name in results]

def get_course_info(course_id: str, db_path=DB_PATH) -> dict:
    """
    Returns the course long name and short name for the given course ID.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT long_name, short_name 
        FROM courses 
        WHERE course_id = ?
    ''', (course_id,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return {'long_name': result[0], 'short_name': result[1]}
    else:
        return {'long_name': 'Unknown Course', 'short_name': ''}
