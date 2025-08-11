import sys

def password_validation():
    """Validate user password with 3 attempts"""
    correct_password = "p4n@in"
    attempts = 3
    
    print("Set your password :")
    print("   p4n@in")
    print("   Enter your Password :")
    
    while attempts > 0:
        user_input = input("   ").strip()
        
        if user_input == correct_password:
            print("   note : user select right password")
            return True
        else:
            attempts -= 1
            if attempts > 0:
                print(f"   wrong password ... try {attempts} more time{'s' if attempts > 1 else ''} out of {attempts}")
            else:
                print("   wrong password ... try 0 more time 0")
    
    return False

def mcq_exam():
    """Conduct MCQ exam with scoring"""
    questions = [
        {
            "question": "1. Who invented Java Programming?",
            "options": [
                "Guido van Rossum",
                "James Gosling",
                "Dennis Ritchie",
                "Bjarne Stroustrup"
            ],
            "correct": 2
        },
        {
            "question": "2. Which of the following is not a Java feature?",
            "options": [
                "Object-oriented",
                "Use of pointers",
                "Portable",
                "Dynamic and Extensible"
            ],
            "correct": 2
        },
        {
            "question": "3. What is the extension of compiled java classes?",
            "options": [
                ".txt",
                ".js",
                ".class",
                ".java"
            ],
            "correct": 3
        },
        {
            "question": "4. Which environment variable is used to set the java path?",
            "options": [
                "JAVA_HOME",
                "JavaPATH",
                "JavaROOT",
                "JavaAPI"
            ],
            "correct": 1
        },
        {
            "question": "5. Which of the following is a superclass of every class in Java?",
            "options": [
                "ArrayList",
                "Abstract class",
                "Object class",
                "String"
            ],
            "correct": 3
        }
    ]
    
    score = 0
    print("\n   then start MCQ EXAM...\n")
    
    for q in questions:
        print(f"\n   {q['question']}")
        for i, option in enumerate(q['options'], 1):
            print(f"   {i}. ) {option}")
        
        try:
            answer = int(input("\n   Enter your answer (1-4): "))
            if answer == q['correct']:
                score += 1
                print("   Correct!")
            else:
                print(f"   Wrong! Correct answer is {q['correct']}. ) {q['options'][q['correct']-1]}")
        except ValueError:
            print("   Invalid input! Please enter a number between 1-4.")
    
    print(f"\n   Exam completed! Your score: {score}/{len(questions)}")
    return score

def main():
    """Main program execution"""
    print("Welcome to the MCQ Exam System!\n")
    
    if password_validation():
        mcq_exam()
    else:
        print("\n   Maximum attempts reached. Access denied!")
        sys.exit(1)

if __name__ == "__main__":
    main()
