"""
Plain language definitions of legal terms
"""

LEGAL_TERMS = {
    "cognizable": {
        "plain": "Police can arrest without warrant",
        "explanation": "For this offense, police can arrest you immediately without getting a court order first. They can also start investigating without permission.",
        "impact": "More serious - police can take direct action"
    },
    "non_cognizable": {
        "plain": "Police need court permission to arrest",
        "explanation": "Police cannot arrest you without a warrant. They need to get permission from a magistrate first.",
        "impact": "Less urgent - process takes longer"
    },
    "bailable": {
        "plain": "Can get bail from police station",
        "explanation": "If arrested, you have the right to be released on bail. The police officer can grant bail at the station itself.",
        "impact": "Easier to get released"
    },
    "non_bailable": {
        "plain": "Bail decided by court",
        "explanation": "Bail is not automatic. You'll need to apply to a court, and the judge decides based on factors like evidence and flight risk.",
        "impact": "Harder to get bail - may need lawyer"
    },
    "compoundable": {
        "plain": "Can be settled between parties",
        "explanation": "You and the other party can reach a compromise and the case can be dropped with court permission.",
        "impact": "Possible to resolve without full trial"
    },
    "non_compoundable": {
        "plain": "Cannot be privately settled",
        "explanation": "Even if you compromise with the other party, the case continues because it's considered a crime against society.",
        "impact": "Must go through full legal process"
    },
    "summary_trial": {
        "plain": "Fast-track court hearing",
        "explanation": "The case is decided quickly, usually in a few hearings, without complex procedures.",
        "impact": "Faster resolution"
    },
    "warrant_trial": {
        "plain": "Full court trial",
        "explanation": "Regular court process with evidence, witnesses, and multiple hearings.",
        "impact": "Longer process, needs lawyer"
    }
}

CRIME_SEVERITY = {
    "high": {
        "description": "Serious criminal offense",
        "examples": ["Robbery", "Murder", "Rape", "Kidnapping"],
        "advice": "Get a lawyer immediately. Do not talk to police without legal counsel."
    },
    "medium": {
        "description": "Moderate criminal offense",
        "examples": ["Theft", "Assault", "Criminal intimidation"],
        "advice": "Consider legal advice. Document everything."
    },
    "low": {
        "description": "Minor offense or compoundable",
        "examples": ["Wrongful restraint", "Trespass", "Simple hurt"],
        "advice": "Can often be resolved through compromise or small fines."
    }
}