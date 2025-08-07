import sqlite3
from queries import search_teacher_by_name, get_courses_for_user, get_students_in_course

def main():
    print("🧪 Canvas CLI Tester")
    print("Available commands:")
    print("  search   - Search for teacher by name")
    print("  courses  - List courses for user by user_id (optionally by role)")
    print("  students - List all students enrolled in a given course by course_id")
    print("  exit     - Quit\n")

    TERMS = ['BPS_W25', 'BPS_DP24', 'BPS_DP25']

    while True:
        command = input("Enter command: ").strip().lower()

        if command == 'exit':
            print("Goodbye!")
            break

        elif command == 'search':
            query = input("Enter part of teacher's name to search: ").strip()
            results = search_teacher_by_name(query)
            if not results:
                print("No matching teachers found.\n")
            else:
                print(f"Found {len(results)} teacher(s):")
                for r in results:
                    print(f" - {r['user_id']}: {r['full_name']}")
                print()

        elif command == 'courses':
            user_id = input("Enter user_id: ").strip()
            role = input("Enter role (optional): ").strip()
            role = role if role else None

            courses = get_courses_for_user(user_id, role, TERMS)
            if not courses:
                print("No courses found for that user.\n")
            else:
                print(f"Found {len(courses)} course(s):")
                for c in courses:
                    print(f" - {c['course_id']} | {c['short_name']} — {c['long_name']}")
                print()

        elif command == 'students':
            course_id = input("Enter a course_id: ").strip()

            students = get_students_in_course(course_id)
            if not students:
                print("No students found for that course")
            else:
                print(f"Found {len(students)} student(s):")
                for s in students:
                    print(f" - {s['user_id']}: {s['full_name']}")
                print()

        else:
            print("Unknown command. Please type 'search', 'courses', or 'exit'.\n")


if __name__ == '__main__':
    main()