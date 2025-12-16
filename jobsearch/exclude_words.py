EXCLUDE_WORDS = {

    # 1. Resume / Document Structure (Meta-only)
    "RESUME_STOPWORDS": {
        "resume", "curriculum", "vitae", "cv",
        "name", "address", "email", "phone",
        "linkedin", "github",
        "summary", "objective", "profile",
        "experience", "education",
        "skills", "projects",
        "certifications", "references",
        "available", "upon", "request"
    },

    # 2. Grammar & Function Words (Pure Noise)
    "GRAMMAR_NOISE": {
        "and", "or", "with", "without",
        "for", "to", "from", "in", "on",
        "of", "at", "by", "as",
        "is", "are", "was", "were",
        "be", "been",
        "this", "that", "these", "those",
        "a", "an", "the",
        "all", "any", "each"
    },

    # 3. Months / Date Noise
    "MONTHS": {
        "january", "jan",
        "february", "feb",
        "march", "mar",
        "april", "apr",
        "may",
        "june", "jun",
        "july", "jul",
        "august", "aug",
        "september", "sep", "sept",
        "october", "oct",
        "november", "nov",
        "december", "dec"
    },

    # 4. Generic Resume Nouns (Non-Skill Alone)
    "NOUN_NOISE": {
        "role", "position", "title",
        "company", "organization", "employer",
        "team", "department", "group",
        "project", "projects", "initiative",

        "task", "tasks",
        "assignment", "assignments",

        "result", "results",
        "outcome", "outcomes",
        "achievement", "achievements",

        "year", "years", "month", "months",
        "date", "dates", "duration",

        "course", "courses",
        "class", "classes",
        "training",

        "client", "clients",
        "customer", "customers",
        "stakeholder", "stakeholders",

        "documentation",
        "report", "reports",
        "presentation", "presentations",
        "meeting", "meetings",

        "detail", "details"
    },

    # 5. Generic Resume Verbs (Action Without Skill Context)
    "VERB_NOISE": {
        "worked", "working",
        "performed", "performing",
        "handled", "handling",
        "completed", "completing",
        "participated", "participating",
        "contributed", "contributing",
        "assisted", "assisting",
        "supported", "supporting",

        "used", "using",
        "utilized", "utilizing",
        "leveraged", "leveraging",

        "learned", "learning",
        "trained", "training",
        "studied", "studying"
    }
}
