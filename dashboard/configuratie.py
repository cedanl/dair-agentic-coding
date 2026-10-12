"""Instellingen van het dashboard, afgeleid van uitvoer/data-profiel.html."""

TITEL = "Uitval in het eerste jaar per sector"
VRAAG = "Verschilt het aandeel uitval in het eerste jaar tussen de sectoren?"

SCHEIDINGSTEKEN = ";"

# Kolomnamen per rol
PERSOON = "persoonsgebonden_nummer"
JAAR = "inschrijvingsjaar"
VERBLIJFSJAAR = "verblijfsjaar_actuele_instelling"
DIPLOMAJAAR = "diplomajaar"
SECTOR = "croho_onderdeel_actuele_opleiding"

VERPLICHT = [PERSOON, JAAR, VERBLIJFSJAAR, DIPLOMAJAAR, SECTOR]

# Een instromer heeft dit verblijfsjaar bij de instelling
INSTROOM_VERBLIJFSJAAR = 1

# Voorbeeldwaarden: de echte drempels bepaalt de eigen organisatie
DREMPEL_GROEP = 30  # groepen met minder instromers tonen we niet
DREMPEL_CEL = 5  # een percentage waarvan teller of rest kleiner is tonen we niet

ONBEKEND = "(onbekend)"
