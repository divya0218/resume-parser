import re


def extract_resume_information(text):
    """Extract structured information from resume text using rules and regex."""

    result = {
        "personal_information": {
            "full_name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin": None,
            "github": None,
        },
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "certifications": [],
    }

    if not isinstance(text, str):
        text = str(text or "")

    text = text.replace("\u00a0", " ").replace("\u2022", "•")
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]
    personal = result["personal_information"]

    def add_unique(target, value):
        value = str(value).strip()
        if value and value not in target:
            target.append(value)

    # --------------------------------------------------
    # 1. Contact information
    # --------------------------------------------------
    email_match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text,
        re.IGNORECASE,
    )
    if email_match:
        personal["email"] = email_match.group(0).rstrip(".,;)")

    phone_candidates = re.findall(
        r"(?<!\w)(?:\+\s?\d{1,3}[\s().-]?)?(?:\d[\s().-]?){8,13}\d(?!\w)",
        text,
    )
    for candidate in phone_candidates:
        digits = re.sub(r"\D", "", candidate)
        if 10 <= len(digits) <= 13:
            personal["phone"] = candidate.strip()
            break

    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_%./-]+",
        text,
        re.IGNORECASE,
    )
    if linkedin_match:
        personal["linkedin"] = linkedin_match.group(0).rstrip(".,;)")

    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+",
        text,
        re.IGNORECASE,
    )
    if github_match:
        personal["github"] = github_match.group(0).rstrip(".,;)")

    # Detect common city/state pairs.
    states = (
        "Maharashtra|Karnataka|Gujarat|Rajasthan|Delhi|Tamil Nadu|Kerala|"
        "Punjab|Goa|Telangana|Uttar Pradesh|West Bengal|Madhya Pradesh|"
        "Andhra Pradesh|Haryana|Bihar|Odisha|Assam|Jharkhand|Chhattisgarh|"
        "Uttarakhand|Himachal Pradesh|Sikkim|Manipur|Meghalaya|Mizoram|"
        "Nagaland|Tripura|Arunachal Pradesh|Jammu and Kashmir"
    )
    location_match = re.search(
        rf"\b([A-Z][A-Za-z.' -]+,\s*(?:{states}))\b",
        text,
        re.IGNORECASE,
    )
    if location_match:
        personal["location"] = location_match.group(1).strip()

    # Guess a name from the first few lines, excluding obvious headings.
    ignored_names = {
        "resume", "curriculum vitae", "cv", "professional summary",
        "contact information", "software developer", "data analyst",
        "information technology", "backend development",
    }
    for line in lines[:8]:
        candidate = line.strip(" :|-•")
        if candidate.lower() in ignored_names:
            continue
        if (
            2 <= len(candidate.split()) <= 4
            and re.fullmatch(r"[A-Za-z]+(?:[ '-][A-Za-z]+)*", candidate)
            and not re.search(
                r"\b(engineer|developer|analyst|student|intern|manager|"
                r"resume|curriculum|linkedin|github)\b",
                candidate,
                re.IGNORECASE,
            )
        ):
            personal["full_name"] = candidate.title()
            break

    # --------------------------------------------------
    # 2. Identify section headings
    # --------------------------------------------------
    section_keywords = {
        "education": {
            "education", "academic background", "educational qualifications",
            "academic qualifications",
        },
        "experience": {
            "experience", "work experience", "professional experience",
            "employment history", "internship experience", "work history",
            "professional background", "internships",
        },
        "skills": {
            "skills", "technical skills", "technologies", "core competencies",
            "technical competencies", "key skills", "areas of expertise",
        },
        "projects": {
            "projects", "personal projects", "academic projects",
            "project experience", "selected projects",
        },
        "certifications": {
            "certifications", "certificates", "licenses and certifications",
            "courses and certifications", "licenses",
        },
    }
    stop_headings = {
        "summary", "professional summary", "profile", "objective",
        "career objective", "achievements", "interests", "languages",
        "references", "declaration", "additional information",
        "personal details",
    }

    sections = {key: [] for key in section_keywords}
    current_section = None

    for line in lines:
        heading = line.lower().strip(" :|-•\t")
        matched_section = next(
            (section for section, names in section_keywords.items()
             if heading in names),
            None,
        )
        if matched_section:
            current_section = matched_section
            continue
        if heading in stop_headings:
            current_section = None
            continue
        if "fictional sample" in heading:
            continue
        if current_section:
            sections[current_section].append(line)

    # --------------------------------------------------
    # 3. Date helpers
    # --------------------------------------------------
    month = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )
    date_range_pattern = re.compile(
        rf"(?i)(?:(?:{month})\s+)?(?:19|20)\d{{2}}\s*"
        rf"(?:-|–|—|to)\s*"
        rf"(?:(?:{month})\s+)?(?:19|20)\d{{2}}|"
        rf"(?:(?:{month})\s+)?(?:19|20)\d{{2}}\s*"
        rf"(?:-|–|—|to)\s*(?:present|current|ongoing)"
    )
    year_pattern = re.compile(r"\b(?:19|20)\d{2}\b")

    def find_duration(value):
        match = date_range_pattern.search(value)
        if match:
            return match.group(0).strip()
        years = year_pattern.findall(value)
        if len(years) >= 2:
            return f"{years[0]} - {years[1]}"
        if years:
            return years[0]
        return None

    def remove_dates(value):
        value = date_range_pattern.sub("", value)
        value = year_pattern.sub("", value)
        return re.sub(r"\s+", " ", value).strip(" ,;|:-–—")

    # --------------------------------------------------
    # 4. Education
    # Supports degree, institution, and duration on separate lines.
    # --------------------------------------------------
    degree_pattern = re.compile(
        r"\b(bachelor|b\.?\s?tech|b\.?\s?e\.?|master|m\.?\s?tech|"
        r"m\.?\s?e\.?|ph\.?\s?d|diploma|degree|b\.?\s?sc|m\.?\s?sc|"
        r"higher secondary|class\s+\d+|ssc|hsc|bca|mca|mba|bba|"
        r"bcom|mcom|b\.?\s?pharm|m\.?\s?pharm|associate degree)\b",
        re.IGNORECASE,
    )
    institution_pattern = re.compile(
        r"\b(college|university|institute|school|academy|polytechnic|"
        r"vidyalaya|junior college)\b",
        re.IGNORECASE,
    )
    grade_pattern = re.compile(
        r"\b(?:CGPA|GPA|percentage|score)\s*:?\s*\d+(?:\.\d+)?(?:/\d+)?%?",
        re.IGNORECASE,
    )

    for line in sections["education"]:
        raw_line = line.strip(" \t•●▪*-")
        if not raw_line:
            continue

        duration = find_duration(raw_line)

        # A date-only line should update the latest education record,
        # not become a degree or institution.
        date_only_line = bool(
            duration
            and not degree_pattern.search(remove_dates(raw_line))
            and not institution_pattern.search(remove_dates(raw_line))
        )
        if date_only_line:
            if result["education"]:
                result["education"][-1]["duration"] = duration
            continue

        cleaned = grade_pattern.sub("", raw_line)
        cleaned_without_dates = remove_dates(cleaned).strip(" ,;|:-–—•")

        if not cleaned_without_dates:
            if duration and result["education"]:
                result["education"][-1]["duration"] = duration
            continue

        # If a line contains a degree, create or update a degree record.
        if degree_pattern.search(cleaned_without_dates):
            # Split explicit degree/institution separators if both are inline.
            parts = re.split(r"\s+(?:[-–—|])\s+|,\s*", cleaned_without_dates, maxsplit=1)
            degree = parts[0].strip(" ,;|:-–—")
            institution = parts[1].strip(" ,;|:-–—") if len(parts) > 1 else None

            # If the institution is embedded in the same text, split at its keyword.
            inst_match = institution_pattern.search(cleaned_without_dates)
            if inst_match and not institution:
                possible_degree = cleaned_without_dates[:inst_match.start()].strip(" ,;|:-–—")
                possible_institution = cleaned_without_dates[inst_match.start():].strip(" ,;|:-–—")
                if possible_degree:
                    degree = possible_degree
                    institution = possible_institution

            result["education"].append({
                "degree": degree or cleaned_without_dates,
                "institution": institution or None,
                "duration": duration,
            })
            continue

        # A college/university line usually belongs to the most recent degree.
        if institution_pattern.search(cleaned_without_dates):
            if result["education"] and not result["education"][-1]["institution"]:
                result["education"][-1]["institution"] = cleaned_without_dates
                if duration:
                    result["education"][-1]["duration"] = duration
            else:
                result["education"].append({
                    "degree": cleaned_without_dates,
                    "institution": None,
                    "duration": duration,
                })
            continue

        # Handle a duration included on a line after a degree/institution.
        if duration and result["education"]:
            result["education"][-1]["duration"] = duration
            continue

        # If a non-heading continuation line follows a degree with no institution,
        # use it as the institution unless it looks like another degree.
        if result["education"] and not result["education"][-1]["institution"]:
            if not degree_pattern.search(cleaned_without_dates):
                result["education"][-1]["institution"] = cleaned_without_dates
        else:
            result["education"].append({
                "degree": cleaned_without_dates,
                "institution": None,
                "duration": duration,
            })

    # --------------------------------------------------
    # 5. Skills
    # --------------------------------------------------
    skill_categories = {
        "languages", "programming languages", "data", "data tools",
        "backend", "frontend", "front end", "databases", "database",
        "tools", "frameworks", "libraries", "cloud", "devops",
        "testing", "platforms", "technologies", "other",
    }
    for line in sections["skills"]:
        for part in re.split(r"[,;|•]", line):
            skill = part.strip(" \t-•:")
            if not skill:
                continue
            if ":" in skill:
                label, remainder = skill.split(":", 1)
                if label.strip().lower() in skill_categories:
                    skill = remainder.strip()
            if skill:
                add_unique(result["skills"], skill)

    # --------------------------------------------------
    # 6. Experience
    # --------------------------------------------------
    role_pattern = re.compile(
        r"\b(intern|developer|engineer|manager|analyst|trainee|designer|"
        r"consultant|administrator|programmer|assistant|specialist|"
        r"executive|architect|technician|lead|officer|coordinator|"
        r"scientist|associate)\b",
        re.IGNORECASE,
    )
    for line in sections["experience"]:
        duration = find_duration(line)
        if role_pattern.search(line):
            result["experience"].append({
                "role_and_company": line.strip(" •-"),
                "duration": duration,
                "description": [],
            })
        elif result["experience"]:
            last = result["experience"][-1]
            if duration and not last["duration"]:
                last["duration"] = duration
            else:
                add_unique(last["description"], line.strip(" •-"))
        else:
            result["experience"].append({
                "role_and_company": line.strip(" •-"),
                "duration": duration,
                "description": [],
            })

    # --------------------------------------------------
    # 7. Projects
    # Flexible separators + known technology names.
    # --------------------------------------------------
    technology_pattern = re.compile(
        r"\b("
        r"python|pandas|numpy|java|javascript|typescript|c\+\+|c#|"
        r"html|css|sql|mysql|postgresql|mongodb|sqlite|react|angular|"
        r"vue|node\.?js|express|django|flask|fastapi|streamlit|pytorch|"
        r"tensorflow|scikit-learn|opencv|pillow|pymupdf|pytesseract|"
        r"git|github|docker|kubernetes|aws|azure|firebase|supabase|redis|"
        r"rest\s*api|graphql|bootstrap|tailwind(?:\s*css)?|"
        r"machine\s+learning|deep\s+learning|power\s*bi|tableau|php|"
        r"laravel|flutter|dart|oracle|matplotlib|seaborn|nlp"
        r")\b",
        re.IGNORECASE,
    )
    separator_pattern = re.compile(r"[-—–_:=|]+")

    for line in sections["projects"]:
        clean_line = line.strip(" \t•●▪*-")
        if not clean_line:
            continue

        matches = list(technology_pattern.finditer(clean_line))
        technologies = []
        for match in matches:
            tech = match.group(0).strip()
            if tech.lower() not in {item.lower() for item in technologies}:
                technologies.append(tech)

        first_tech_start = matches[0].start() if matches else -1
        prefix = clean_line[:first_tech_start] if first_tech_start >= 0 else ""
        has_separator_before_tech = bool(
            first_tech_start >= 0 and separator_pattern.search(prefix)
        )

        # Start a new project for the first line, or for a line that has a
        # title followed by a recognized technology stack.
        if not result["projects"] or has_separator_before_tech:
            title = clean_line
            if has_separator_before_tech:
                possible_title = prefix.rstrip(" \t-—–_:=|([{(").strip()
                if possible_title:
                    title = possible_title
            result["projects"].append({
                "name_and_description": title,
                "technologies": technologies,
                "description": [],
            })
        else:
            current = result["projects"][-1]
            known = {item.lower() for item in current["technologies"]}
            for tech in technologies:
                if tech.lower() not in known:
                    current["technologies"].append(tech)
                    known.add(tech.lower())
            add_unique(current["description"], clean_line)

    # --------------------------------------------------
    # 8. Certifications
    # --------------------------------------------------
    for line in sections["certifications"]:
        clean_line = line.strip()
        if not clean_line:
            continue
        starts_new = bool(re.match(r"^(?:[•●▪*-]|\d+[.)])\s*", clean_line))
        clean_line = re.sub(r"^(?:[•●▪*-]|\d+[.)])\s*", "", clean_line)
        if not result["certifications"] or starts_new:
            add_unique(result["certifications"], clean_line)
        else:
            previous = result["certifications"][-1]
            if clean_line not in previous:
                result["certifications"][-1] = previous.rstrip(" .") + " — " + clean_line

    # --------------------------------------------------
    # 9. Remove duplicate records
    # --------------------------------------------------
    for key in ("education", "experience", "projects"):
        unique = []
        seen = set()
        for item in result[key]:
            marker = str(item).casefold()
            if marker not in seen:
                seen.add(marker)
                unique.append(item)
        result[key] = unique

    result["certifications"] = list(dict.fromkeys(result["certifications"]))
    result["skills"] = list(dict.fromkeys(result["skills"]))

    return result
