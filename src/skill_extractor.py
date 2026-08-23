import re


KNOWN_SKILLS = [
    "Python",
    "C",
    "C++",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "FastAPI",
    "Docker",
    "Git",
    "GitHub",
    "Linux",
    "SystemVerilog",
    "UVM",
    "Verilog",
    "x86 Assembly",
    "Postman",
    "ChromaDB",
    "Gemini",
    "Machine Learning",
    "Computer Vision",
    "SQL",
    "MongoDB",
    "Firebase",
]


def extract_skills(text):
    found_skills = []

    text_lower = text.lower()

    for skill in KNOWN_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


if __name__ == "__main__":
    with open("../data/cvs/my_cv.txt", "r", encoding="utf-8") as file:
        text = file.read()

    skills = extract_skills(text)

    print("Extracted Skills:")

    for skill in skills:
        print("-", skill)