import enum
from src import ModuleManager, utils

class Script(enum.Enum):
    Unknown = 0
    Latin = 1
    Cyrillic = 2
    Greek = 3
    Armenian = 4
    FullWidth = 5
    Coptic = 6
    Cherokee = 7
    TaiLe = 8
WORD_SEPERATORS = [",", " ", "\t", "."]

SCORE_LENGTH = 100

class Module(ModuleManager.BaseModule):
    def _detect_script(self, char):
        point = ord(char)
        # NULL .. LATIN SMALL LETTER TURNED H WITH FISHHOOK AND TAIL
        if   0x0000 <= point <= 0x02AF:
            return Script.Latin
        # GREEK CAPITAL LETTER HETA .. GREEK CAPITAL REVERSED DOTTED LUNATE SIGMA SYMBOL
        elif 0x0370 <= point <= 0x03ff:
            return Script.Greek
        # CYRILLIC CAPITAL LETTER IE WITH GRAVE .. CYRILLIC SMALL LETTER EL WITH DESCENDER
        elif 0x0400 <= point <= 0x052F:
            return Script.Cyrillic
        # ARMENIAN CAPITAL LETTER AYB .. ARMENIAN HYPHEN
        elif 0x0531 <= point <= 0x058A:
            return Script.Armenian
        # FULLWIDTH EXCLAMATION MARK .. FULLWIDTH RIGHT WHITE PARENTHESIS
        elif 0xFF01 <= point <= 0xff60:
            return Script.FullWidth
        # COPTIC CAPITAL LETTER ALFA .. COPTIC MORPHOLOGICAL DIVIDER
        elif 0x2C80 <= point <= 0x2CFF:
            return Script.Coptic
        # CHEROKEE LETTER A .. CHEROKEE SMALL LETTER MV
        elif 0x13A0 <= point <= 0x13FD:
            return Script.Cherokee
        # TAI LE LETTER KA .. U+197F
        elif 0x1950 <= point <= 0x197F:
            return Script.TaiLe
        return Script.Unknown

    @utils.hook("received.message.channel")
    def channel_message(self, event):
        last_script = None
        last_was_separator = False
        score = 0
        scripts = set([])

        for char in event["message"]:
            if char in WORD_SEPERATORS:
                last_was_separator = True
            else:
                script = self._detect_script(char)
                scripts.add(script)
                if not script == Script.Unknown:
                    if last_script and not script == last_script:
                        score += 1
                        if not last_was_separator:
                            score += 1

                    last_script = script

                last_was_separator = False

        score = score/(len(event["message"])/SCORE_LENGTH)
        score = round(score, 2)
        if score > 0:
            self.log.trace("Message given a mixed-unicode score of %f", [score])