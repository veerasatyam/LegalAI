from enum import Enum
from typing import List, Dict, Set

class LegalEntity(Enum):
    """Types of entities we need to extract"""
    PERSON = "person"
    GROUP = "group"
    AUTHORITY = "authority"  # police, government official
    PROPERTY = "property"
    VEHICLE = "vehicle"
    LOCATION = "location"

class LegalAction(Enum):
    """Actions that map to IPC sections"""
    # Against person
    ASSAULT = "assault"
    CRIMINAL_FORCE = "criminal_force"
    WRONGFUL_RESTRAINT = "wrongful_restraint"
    WRONGFUL_CONFINEMENT = "wrongful_confinement"
    
    # Against property
    TRESPASS = "trespass"
    THEFT = "theft"
    EXTORTION = "extortion"
    CRIMINAL_INTIMIDATION = "criminal_intimidation"
    
    # Public order
    RIOTING = "rioting"
    UNLAWFUL_ASSEMBLY = "unlawful_assembly"
    OBSTRUCTION = "obstruction"
    
    # Offenses related to documents
    FORGERY = "forgery"
    
class HarmType(Enum):
    """Types of harm/damage"""
    PHYSICAL = "physical"
    PSYCHOLOGICAL = "psychological"
    PROPERTY_DAMAGE = "property_damage"
    RESTRICTION_MOVEMENT = "restriction_of_movement"
    REPUTATION = "reputation"
    PRIVACY = "privacy"

# Keywords that indicate specific legal concepts
LEGAL_INDICATORS = {
    "wrongful_restraint": [
        "blocked", "stopped", "prevented from going", "wouldn't let me pass",
        "obstructed", "barred my way", "held me back", "stopped me from"
    ],
    "wrongful_confinement": [
        "locked in", "trapped", "wouldn't let me leave", "imprisoned",
        "held captive", "confined", "locked the door"
    ],
    "assault": [
        "threatened to hit", "raised hand", "threatened to beat",
        "said they would kill", "threatened with weapon"
    ],
    "criminal_force": [
        "pushed", "slapped", "hit", "beat", "punched", "kicked",
        "pulled my hair", "attacked"
    ],
    "criminal_intimidation": [
        "threatened", "said they would harm", "warned me", "threatened my family",
        "said they would kill"
    ],
    "theft": [
        "stole", "took my", "snatched", "picked my pocket",
        "took without permission"
    ],
    "trespass": [
        "entered my house", "came into my property", "broke into",
        "entered without permission", "refused to leave"
    ]
}